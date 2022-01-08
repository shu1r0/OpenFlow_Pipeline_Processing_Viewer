"""
Web socket API

TODO:
    * まずは，接続し，ホストなどを配置できるようにする．
    * テーブル情報を取得するインターフェースの追加

Notes:
    * Mininetコマンド実行中はたぶん経路情報の受け取りができない．
        * 同時にすることないでしょ

Errors:
    * コマンドの結果を返す際に，con.poll()でBlockされ，送信ができない
        => コマンドの結果を返すときは，Threadを止めるかなにかする
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
    CommandResultType, CommandResult, GetTraceRequest, GetTraceResult


setLoggerClass(Logger)
logger = getLogger('tracing_net.api.ws_server')


class WSEvent(Enum):
    """Web Socket Event

    Each variable in the enum represents an event name.
    However, event names are used in lowercase，you should use ''event_name'' property to refer to the event name.

    Each value represents a function name used in the event.

    """

    START_TRACING = "start_tracing"
    STOP_TRACING = "stop_tracing"

    ADD_HOST = "add_host"
    REMOVE_HOST = "remove_host"
    ADD_SWITCH = "add_switch"
    REMOVE_SWITCH = "remove_switch"
    ADD_LINK = "add_link"
    REMOVE_LINK = "remove_link"

    GET_TRACE = "get_trace"

    # TODO: 今後実装予定
    EXEC_NODE_COMMAND = "exec_cmd"
    # まだ，実装できていない
    EXEC_MININET_COMMAND = "exec_mininet_command"
    EXEC_MININET_COMMAND_RESULT = "exec_mininet_command_result"

    CHANGE_TOPOLOGY = "change_topology"

    # error
    TOPOLOGY_CHANGE_ERROR = "topology_change_error"

    @property
    def event_name(self):
        """ws event name"""
        return self.name.lower()

    @classmethod
    def CHANGE_NET_EVENTS(cls):
        return [
            cls.ADD_SWITCH, cls.REMOVE_SWITCH,
            cls.ADD_HOST, cls.REMOVE_HOST,
            cls.ADD_LINK, cls.REMOVE_LINK
        ]


class MessageHubBase(metaclass=ABCMeta):
    """for multiprocess."""

    def __init__(self):
        self.tracer = None
        self.socket = None

        self.tracer_handler = None
        self.ws_server_handler = None

    @abstractmethod
    def emit2tracer(self, event: WSEvent, param):
        """emit to net

        Args:
            event (WSEvent) :
            param (dict) : This is used by callback function of ``get_from_client``.
        """
        raise NotImplementedError

    @abstractmethod
    def emit2ws_server(self, event: WSEvent, param):
        """emit to client"""
        raise NotImplementedError

    def set_tracer_handler(self, tracer):
        """

        Args:
            tracer (AbstractTracingOFPipeline) :
            tracer_handler:

        Returns:

        """
        self.tracer = tracer

    def set_ws_server_handler(self, socket):
        """

        Args:
            socket (AsyncServer)
            ws_server_handler:

        Returns:

        """
        self.socket = socket


class MessageHub(MessageHubBase):
    """for main process.

    * この"set_tracer_handler "を指定する必要があります．
    """

    def __init__(self):
        super(MessageHub, self).__init__()

    def emit2tracer(self, event: WSEvent, param):
        if conf.OUTPUT_MESSAGE_HUB_TO_LOGFILE:
            logger.debug("ws_server -> tracer (event={}, param={})".format(event, param))
        if self.tracer:
            msg = self._tracer_handler(event=event, param=param)
            return msg
        else:
            logger.error("no tracer error")

    def emit2ws_server(self, event: WSEvent, protoMsg):
        if conf.OUTPUT_MESSAGE_HUB_TO_LOGFILE:
            logger.debug("tracer -> ws_server (event={}, protoMsgType={})".format(event, type(protoMsg)))
        if self.socket:
            self._ws_server_handler(event=event, protoMsg=protoMsg)
        else:
            logger.error("no socket error")

    def _tracer_handler(self, event: WSEvent, param):
        """callback for messagehub

        Args:
            event:
            param:
        """
        net = self.tracer.tracing_net
        
        if event in WSEvent.CHANGE_NET_EVENTS():
            msg = self._change_net(event, param)
            return msg
        elif event == WSEvent.EXEC_MININET_COMMAND:
            connection = net.cli.cli_connection
            connection.input(param["command"])
            return
        elif event == WSEvent.GET_TRACE:
            traces = packet_trace_list.pop_protobuf_message()
            traces_msg = GetTraceResult()
            count = 0
            for t in traces:
                traces_msg.packet_traces.append(t)
                count += 1
            traces_msg.traces_length = count
            self.emit2ws_server(WSEvent.GET_TRACE, traces_msg)
            return
        elif event == WSEvent.START_TRACING:
            self.tracer.start_tracing()
            return
        elif event == WSEvent.STOP_TRACING:
            self.tracer.stop_tracing()
            return
        elif event == WSEvent.CHANGE_TOPOLOGY:
            switches = param["switches"]
            hosts = param["hosts"]
            links = param["links"]
            for switch in switches:
                net.add_switch(switch.name, dpid=switch.datapath_id)
            for host in hosts:
                net.add_host(host.name, ip=host.ip, mac=host.mac)
            for link in links:
                net.add_link(link.name, link.host1, link.host2)
            return
        else:
            logger.error("No Matching WebSocket Event (event={})".format(event))

    def _change_net(self, event: WSEvent, param):
        net = self.tracer.tracing_net
        handler_string = event.value
        handler = getattr(net, handler_string, None)
        if event == WSEvent.ADD_SWITCH or event == WSEvent.REMOVE_SWITCH:
            switch = handler(**param)
            switch_msg = Switch()
            switch_msg.name = switch.name
            switch_msg.datapath_id = switch.dpid
            return switch_msg
        elif event == WSEvent.ADD_HOST or event == WSEvent.REMOVE_HOST:
            host = handler(**param)
            host_msg = Host()
            host_msg.name = host.name
            # warning: バグ回避
            host_msg.ip = host.params["ip"]
            host_msg.mac = host.params["mac"]
            return host_msg
        elif event == WSEvent.ADD_LINK or event == WSEvent.REMOVE_LINK:
            link = handler(**param)
            link_msg = Link()
            # warning
            link_msg.name = param['name']
            link_msg.host1 = link.intf1.node.name
            link_msg.host2 = link.intf2.node.name
            return link_msg

    def _ws_server_handler(self, event, protoMsg):
        protoMsg = protoMsg.SerializeToString()
        if isinstance(event, WSEvent):
            event = event.event_name
        asyncio.ensure_future(self.socket.emit(event=event, data=protoMsg))


# message hub instance
# もし，これを使う場合は，変数を初期化する
message_hub: MessageHubBase = MessageHub()


#
# ↓ init variables
#

# Web Socket Server Name space
NAME_SPACE = ''


# socket server
# CORSのオリジン設定をすべて許可に
socketio_server = socketio.AsyncServer(cors_allowed_origins='*')

# web application
web_app = web.Application()
socketio_server.attach(web_app)
runner = web.AppRunner(web_app)

message_hub.set_ws_server_handler(socketio_server)


#
# ↓ Web Socket event
#

@socketio_server.event(namespace=NAME_SPACE)
def connect(sid, environ, auth):
    logger.info('connect sid={}'.format(sid))


@socketio_server.event(namespace=NAME_SPACE)
def disconnect(sid):
    logger.info('disconnect sid={}'.format(sid))


@socketio_server.event(namespace=NAME_SPACE)
def connected(sid, data):
    pass


@socketio_server.on(WSEvent.START_TRACING.event_name, namespace=NAME_SPACE)
def start_tracing(sid, data):
    event = WSEvent.START_TRACING
    req = StartTracingRequest()
    req.ParseFromString(data)
    message_hub.emit2tracer(event=event, param={})


@socketio_server.on(WSEvent.STOP_TRACING.event_name, namespace=NAME_SPACE)
def stop_tracing(sid, data):
    event = WSEvent.STOP_TRACING
    req = StopTracingRequest()
    req.ParseFromString(data)
    message_hub.emit2tracer(event=event, param={})


@socketio_server.on(WSEvent.ADD_HOST.event_name, namespace=NAME_SPACE)
def add_host(sid, data):
    """add host

    The required parameters are following ...
        * Host

    Args:
        sid:
        data:
    """
    event = WSEvent.ADD_HOST
    host = Host()
    host.ParseFromString(data)
    param = {'name': host.name, 'ip': host.ip, 'mac': host.mac}
    msg = message_hub.emit2tracer(event=event, param=param)
    if msg:
        return msg.SerializeToString()


@socketio_server.on(WSEvent.REMOVE_HOST.event_name, namespace=NAME_SPACE)
def remove_host(sid, data):
    """remove host

    The required parameters are following ...
        * Host

    Args:
        sid:
        data:
    """
    event = WSEvent.REMOVE_HOST
    host = Host()
    host.ParseFromString(data)
    param = {'name': host.name, 'ip': host.ip, 'mac': host.mac}
    msg = message_hub.emit2tracer(event=event, param=param)
    if msg:
        return msg.SerializeToString()


@socketio_server.on(WSEvent.ADD_SWITCH.event_name, namespace=NAME_SPACE)
def add_switch(sid, data):
    """add switch

    The required parameters are following ...
        * Switch

    Args:
        sid:
        data:
    """
    event = WSEvent.ADD_SWITCH
    switch = Switch()
    switch.ParseFromString(data)
    param = {'name': switch.name, 'dpid': switch.datapath_id}
    msg = message_hub.emit2tracer(event=event, param=param)
    if msg:
        return msg.SerializeToString()


@socketio_server.on(WSEvent.REMOVE_SWITCH.event_name, namespace=NAME_SPACE)
def remove_switch(sid, data):
    """remove switch

    The required parameters are following ...
        * Switch

    Args:
        sid:
        data:
    """
    event = WSEvent.REMOVE_SWITCH
    switch = Switch()
    switch.ParseFromString(data)
    param = {'name': switch.name, 'datapath_id': switch.datapath_id}
    msg = message_hub.emit2tracer(event=event, param=param)
    if msg:
        return msg.SerializeToString()


@socketio_server.on(WSEvent.ADD_LINK.event_name, namespace=NAME_SPACE)
def add_link(sid, data):
    """add Link

    The required parameters are following ...
        * Link

    Args:
        sid:
        data:
    """
    event = WSEvent.ADD_LINK
    link = Link()
    link.ParseFromString(data)
    param = {'name': link.name, 'node1': link.host1, 'node2': link.host2}
    msg = message_hub.emit2tracer(event=event, param=param)
    if msg:
        return msg.SerializeToString()


@socketio_server.on(WSEvent.REMOVE_LINK.event_name, namespace=NAME_SPACE)
def remove_link(sid, data):
    """remove Link

    The required parameters are following ...
        * Link

    Args:
        sid:
        data:
    """
    event = WSEvent.ADD_LINK
    link = Link()
    link.ParseFromString(data)
    param = {'name': link.name, 'host1': link.host1, 'host2': link.host2}
    msg = message_hub.emit2tracer(event=event, param=param)
    if msg:
        return msg.SerializeToString()


@socketio_server.on(WSEvent.GET_TRACE.event_name, namespace=NAME_SPACE)
def get_trace(sid, data):
    event = WSEvent.GET_TRACE
    get_trace_req = GetTraceRequest()
    get_trace_req.ParseFromString(data)
    message_hub.emit2tracer(event=event, param={})


@socketio_server.on(WSEvent.EXEC_MININET_COMMAND.event_name, namespace=NAME_SPACE)
def exec_mininet_cmd(sid, data):
    event = WSEvent.EXEC_MININET_COMMAND
    mininet_command = MininetCommand()
    mininet_command.ParseFromString(data)
    message_hub.emit2tracer(event=event, param={"command": mininet_command.command})


@socketio_server.on(WSEvent.EXEC_NODE_COMMAND.event_name, namespace=NAME_SPACE)
def exec_node_command(sid, data):
    raise NotImplementedError


#
# ↓ Web server start and stop
#

def ws_server_start(ip="0.0.0.0", port=8888):
    web.run_app(web_app, host=ip, port=port)


def ws_server_stop():
    asyncio.ensure_future(web_app.shutdown())


async def ws_server_start_coro(ip="0.0.0.0", port=8888):
    """start server by asyncio"""
    await runner.setup()
    site = web.TCPSite(runner, host=ip, port=port)
    await site.start()


async def ws_server_stop_coro():
    """stop server"""
    await runner.cleanup()


if __name__ == '__main__':
    message_hub = TestMessageHub()

    def callback(event, param):
        print(str(event) + str(param))

    ws_server_start()
