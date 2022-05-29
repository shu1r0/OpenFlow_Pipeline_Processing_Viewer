"""
Web socket API

"""
from enum import Enum
from aiohttp import web
from abc import abstractmethod, ABCMeta
import asyncio
import socketio
from logging import getLogger, setLoggerClass, Logger

from src.config import conf
from src.analyzer.packet_trace_handler import packet_trace_list
from .proto.net_pb2 import Host, Switch, Link, PacketTrace, StartTracingRequest, StopTracingRequest, MininetCommand,\
    CommandResultType, CommandResult, GetTraceRequest, GetTraceResult, ChangeTopologyRequest


setLoggerClass(Logger)
logger = getLogger('vnet.api.ws_server')


class WSEvent(Enum):
    """Web Socket Event

    Each variable in the enum represents an event name.
    However, event names are used in lowercase，you should use ''event_name'' property to refer to the event name.

    Each value represents a function name used in the event.

    """

    # start stop
    START_TRACING = "start_tracing"
    STOP_TRACING = "stop_tracing"

    # network configuration
    ADD_HOST = "add_host"
    REMOVE_HOST = "remove_host"
    ADD_SWITCH = "add_switch"
    REMOVE_SWITCH = "remove_switch"
    ADD_LINK = "add_link"
    REMOVE_LINK = "remove_link"

    # get packet trace event
    GET_TRACE = "get_trace"

    # TODO: 今後実装予定
    EXEC_NODE_COMMAND = "exec_cmd"
    EXEC_MININET_COMMAND = "exec_mininet_command"
    EXEC_MININET_COMMAND_RESULT = "exec_mininet_command_result"

    CHANGE_TOPOLOGY = "change_topology"

    # error
    TOPOLOGY_CHANGE_ERROR = "topology_change_error"

    @property
    def event_name(self):
        """ws event name"""
        return self.name.lower()

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.event_name == other
        return False


class ProtoBufInterface(metaclass=ABCMeta):

    def __init__(self, networking, net):
        self.networking = networking
        self.net = net

    def on_start_tracing(self, req: StartTracingRequest) -> None:
        start_tracing_req = StartTracingRequest()
        start_tracing_req.ParseFromString(req)
        self.networking.start(analyzer=True)

    def on_stop_tracing(self, req: StartTracingRequest) -> None:
        start_tracing_req = StartTracingRequest()
        start_tracing_req.ParseFromString(req)
        self.networking.stop_tracing()

    def on_add_host(self, h: Host) -> Host:
        host = Host()
        host.ParseFromString(h)
        r = self.net.add_host(name=host.name, ip=host.ip, mac=host.mac)
        if r:
            return host

    def on_remove_host(self, h: Host) -> Host:
        host = Host()
        host.ParseFromString(h)
        r = self.net.remove_host(name=host.name, ip=host.ip, mac=host.mac)
        if r:
            return host

    def on_add_switch(self, s: Switch) -> Switch:
        switch = Switch()
        switch.ParseFromString(s)
        r = self.net.add_switch(name=switch.name, dpid=switch.datapath_id)
        if r:
            return switch

    def on_remove_switch(self, s: Switch) -> Switch:
        switch = Switch()
        switch.ParseFromString(s)
        r = self.net.remove_switch(name=switch.name, dpid=switch.datapath_id)
        if r:
            return switch

    def on_add_link(self, l: Link) -> Link:
        link = Link()
        link.ParseFromString(l)
        r = self.net.add_link(name=link.name, node1=link.host1, node2=link.host2)
        if r:
            return link

    def on_remove_link(self, l: Link) -> Link:
        link = Link()
        link.ParseFromString(l)
        r = self.net.remove_link(name=link.name, node1=link.host1, node2=link.host2)
        if r:
            return link

    def on_get_trace(self, req: GetTraceRequest) -> None:
        get_trace_req = GetTraceRequest()
        get_trace_req.ParseFromString(req)

        traces = packet_trace_list.pop_protobuf_message()
        traces_msg = GetTraceResult()
        count = 0
        for t in traces:
            traces_msg.packet_traces.append(t)
            count += 1
        traces_msg.traces_length = count
        self.emit_trace(traces_msg)

    def on_exec_node_command(self, c) -> None:
        raise NotImplementedError

    def on_exec_mininet_command(self, c: MininetCommand) -> None:
        mininet_command = MininetCommand()
        mininet_command.ParseFromString(c)
        self.net.cli_connection.input(mininet_command.command)

    def on_change_topology(self, req: ChangeTopologyRequest) -> None:
        change_topology_req = ChangeTopologyRequest()
        change_topology_req.ParseFromString(req)
        # for s in change_topology_req.switches:
        #     self.on_add_switch(s)
        # for h in change_topology_req.hosts:
        #     self.on_add_host(h)
        # for l in change_topology_req.links:
        #     self.on_add_link(l)

    @abstractmethod
    def emit_trace(self, result: GetTraceResult) -> None:
        raise NotImplementedError

    @abstractmethod
    def emit_command_result(self, result: CommandResult) -> None:
        pass


class WSServer(ProtoBufInterface):

    # Web Socket Server Name space
    NAME_SPACE = ''

    def __init__(self, networking, net, ip="0.0.0.0", port=8888):
        super(WSServer, self).__init__(networking=networking, net=net)
        self.ip = ip
        self.port = port

        self.socketio_server = socketio.AsyncServer(cors_allowed_origins='*')
        self.web_app = web.Application()

        self.socketio_server.attach(self.web_app)
        self.runner = web.AppRunner(self.web_app)

    def start(self):
        self.set_event()
        web.run_app(self.web_app, host=self.ip, port=self.port)

    def stop(self):
        asyncio.ensure_future(self.web_app.shutdown())

    async def start_coro(self):
        """start server by asyncio"""
        self.set_event()
        await self.runner.setup()
        site = web.TCPSite(self.runner, host=self.ip, port=self.port)
        await site.start()

    async def stop_coro(self):
        """stop server"""
        await self.runner.cleanup()

    def set_event(self):
        event_handler = {
            WSEvent.START_TRACING.event_name: self.on_start_tracing,
            WSEvent.STOP_TRACING.event_name: self.on_stop_tracing,
            WSEvent.ADD_HOST.event_name: self.on_add_host,
            WSEvent.REMOVE_HOST.event_name: self.on_remove_host,
            WSEvent.ADD_SWITCH.event_name: self.on_add_switch,
            WSEvent.REMOVE_SWITCH.event_name: self.on_remove_switch,
            WSEvent.ADD_LINK.event_name: self.on_add_link,
            WSEvent.REMOVE_LINK.event_name: self.on_remove_link,
            WSEvent.GET_TRACE.event_name: self.on_get_trace,
            WSEvent.EXEC_NODE_COMMAND.event_name: self.on_exec_node_command,
            WSEvent.EXEC_MININET_COMMAND.event_name: self.on_exec_mininet_command,
            WSEvent.CHANGE_TOPOLOGY.event_name: self.on_change_topology
        }

        @self.socketio_server.on('*', namespace=self.NAME_SPACE)
        def catch_event(event, sid, data):
            if event in event_handler.keys():
                result = event_handler[event](data)
                if result:
                    return result.SerializeToString()
            else:
                logger.info("ws server get event (event={}, data={})".format(event, data))

        @self.net.cli_connection.output_deco
        def output_handler(r: str):
            print(r)
            result = CommandResult()
            result.type = CommandResultType.OUTPUT
            result.result = r
            self.emit_command_result(result)

        @self.net.cli_connection.error_deco
        def error_handler(r: str):
            result = CommandResult()
            result.type = CommandResultType.ERROR
            result.result = r
            self.emit_command_result(result)

        @self.net.cli_connection.end_signal_deco
        def end_signal_handler():
            result = CommandResult()
            result.type = CommandResultType.END_SIGNAL
            result.result = ""
            self.emit_command_result(result)

    def emit(self, event: str, data) -> None:
        asyncio.ensure_future(self.socketio_server.emit(event=event, data=data))

    def emit_trace(self, result: GetTraceResult) -> None:
        self.emit(WSEvent.GET_TRACE.event_name, result.SerializeToString())

    def emit_command_result(self, result: CommandResult) -> None:
        self.emit(WSEvent.EXEC_MININET_COMMAND_RESULT.event_name, result.SerializeToString())


