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
    EXEC_MININET_COMMAND = "exec_mininet_cmd"
    EXEC_MININET_COMMAND_RESULT = "exec_mininet_cmd_result"
    EXEC_KEYBOARD_INTERRUPT = "exec_keyboard_interrupt"

    # error
    TOPOLOGY_CHANGE_ERROR = "topology_change_error"

    @property
    def event_name(self):
        """ws event name"""
        return self.name.lower()


class MessageHubBase(metaclass=ABCMeta):
    """for multiprocess."""

    def __init__(self, parent_con, child_con):
        # sender
        self.parent_con = parent_con
        # receiver
        self.child_con = child_con

    @abstractmethod
    def emit2net(self, event: WSEvent, param):
        """emit to net

        Args:
            event (WSEvent) :
            param (dict) : This is used by callback function of ``get_from_client``.
        """
        raise NotImplementedError

    @abstractmethod
    def emit2client(self, event: WSEvent, param):
        """emit to client"""
        raise NotImplementedError

    @abstractmethod
    def get_from_client(self, tracer, net, call_back):
        """receive message sent from client"""
        raise NotImplementedError


class MessageHubForMultiprocess(MessageHubBase):
    """for multiprocess."""

    def __init__(self, parent_con=None, child_con=None):
        super(MessageHubForMultiprocess, self).__init__(parent_con, child_con)
        self.waiting_from_net = False

    def emit2net(self, event: WSEvent, param):
        if conf.OUTPUT_MESSAGE_HUB_TO_LOGFILE:
            logger.debug("MessageHub receives messages from clients and emits them to the vnet. (event={}, param={})".format(event, param))
        event = event.value
        self.parent_con.send({'event': event, 'param': param})

    def emit2client(self, event: WSEvent, protoMsg):
        if conf.OUTPUT_MESSAGE_HUB_TO_LOGFILE:
            logger.debug("MessageHub receives messages from net and emits them to clients. (event={}, param={})".format(event, protoMsg))
        self.child_con.send({'event': event, 'proto': protoMsg})

    def get_from_client(self, tracer, net, call_back):
        while True:
            if self.child_con.poll():
                response = self.child_con.recv()
                if conf.OUTPUT_MESSAGE_HUB_TO_LOGFILE:
                    logger.debug("MessageHub receives messages from clients. (response={})".format(response))
                call_back(tracer, net, event=response['event'], param=response['param'])

    def wait_command_result(self, callback):
        """This sends the command result to callback.
        * This method waits for the command to finish

        Args:
            callback : call back

        """
        # 待機する
        self.waiting_from_net = True
        while True:
            if not self.waiting_from_net:
                break
            if self.parent_con.poll():
                # response from net
                response = self.parent_con.recv()
                response['proto'] = CommandResult.ParseFromString(response['proto'])
                if conf.OUTPUT_MESSAGE_HUB_TO_LOGFILE:
                    logger.debug("MessageHub receives command result from net. (response={})".format(response))
                if isinstance(response['proto'], CommandResult):
                    callback(response['event'], response['proto'])
                    # Note: END_SIGNALが送られないとストップしない
                    if response['proto'].type == CommandResultType.END_SIGNAL:
                        self.waiting_from_net = False

    def wait_traces(self):
        """

        Returns:
            string: trace trace
        """
        if conf.OUTPUT_MESSAGE_HUB_TO_LOGFILE:
            logger.debug("wait packet trace.....")
        traces = self.parent_con.recv()['proto']
        if conf.OUTPUT_MESSAGE_HUB_TO_LOGFILE:
            logger.debug("MessageHub receives traces from vnet. (traces length={})".format(len(traces)))
        return traces


class MessageHub(MessageHubBase):
    """for main process."""

    def __init__(self, tracer=None, net=None, socketio=None):
        super(MessageHub, self).__init__(None, None)
        self.waiting_from_net = False

        self.tracer = tracer
        self.net = net
        self.server_handler = None

        self.socketio = socketio
        self.client_handler = None

    def emit2net(self, event: WSEvent, param):
        """net is mininet"""
        event = event.value
        self.server_handler(self.tracer, self.net, event=event, param=param)

    def emit2client(self, event: WSEvent, protoMsg):
        """client is websocket server"""
        self.child_con.send({'event': event, 'proto': protoMsg})

    def get_from_client(self, tracer, net, call_back):
        self.tracer = tracer
        self.net = net
        self.server_handler = call_back

    def get_from_server(self, socketio, call_back):
        self.socketio = socketio
        self.client_handler = call_back

    def wait_command_result(self, callback):
        """This sends the command result to callback.
        * This method waits for the command to finish

        Args:
            callback : call back

        """
        # 待機する
        self.waiting_from_net = True
        while True:
            if not self.waiting_from_net:
                break
            if self.parent_con.poll():
                # response from net
                response = self.parent_con.recv()
                response['proto'] = CommandResult.ParseFromString(response['proto'])
                if conf.OUTPUT_MESSAGE_HUB_TO_LOGFILE:
                    logger.debug("MessageHub receives command result from net. (response={})".format(response))
                if isinstance(response['proto'], CommandResult):
                    callback(response['event'], response['proto'])
                    # Note: END_SIGNALが送られないとストップしない
                    if response['proto'].type == CommandResultType.END_SIGNAL:
                        self.waiting_from_net = False

    def wait_traces(self):
        """

        Returns:
            string: trace trace
        """
        if conf.OUTPUT_MESSAGE_HUB_TO_LOGFILE:
            logger.debug("wait packet trace.....")
        traces = self.parent_con.recv()['proto']


class TestMessageHub(MessageHubBase):
    """for debug"""

    def __init__(self):
        super(TestMessageHub, self).__init__(None, None)

    def emit2net(self, event: WSEvent, param):
        print("MessageHub receives messages from clients and emits them to the vnet. (event={}, param={})".format(event, param))
        # event = event.value
        # self.parent_con.send({'event': event, 'param': param})

    def emit2client(self, event: WSEvent, param):
        pass

    def get_from_client(self, tracer, net, call_back):
        pass


#
# ↓ init variables
#


# message hub instance
# もし，これを使う場合は，変数を初期化する
message_hub = MessageHub()


def get_messsage_hub(parent_con, child_con):
    """getter for message hub

    Args:
        parent_con:
        child_con:

    Returns:
        MessageHub
    """
    message_hub.parent_con = parent_con
    message_hub.child_con = child_con
    return message_hub


# Web Socket Server Name space
NAME_SPACE = ''


# socket server
# CORSのオリジン設定をすべて許可に
socketio_server = socketio.AsyncServer(cors_allowed_origins='*')

# web application
web_app = web.Application()
socketio_server.attach(web_app)
runner = web.AppRunner(web_app)



#
# ↓ Web Event Handler
#

def exec_wsevent_action(tracer, net, event: WSEvent, param):
    """callback for messagehub

    * get_from_client handler

    Args:
        tracer (AbstractTracingOFPipeline) :
        net:
        event:
        param:

    TODO:
        * 経路情報に関して，インターフェースがnetで良いのか(Tracerにするか)要検討
    """
    if event == WSEvent.EXEC_MININET_COMMAND.value:
        connection = net.cli.cli_connection
        # todo: ここでBlockさせてもいいな
        connection.input(param["command"])
    elif event == WSEvent.GET_TRACE.value:
        traces = packet_trace_list.pop_protobuf_message()
        traces_msg = GetTraceResult()
        traces_msg.packet_traces.extend(traces)
        message_hub.emit2client(WSEvent.GET_TRACE, traces_msg.SerializeToString())
    elif event == WSEvent.START_TRACING.value:
        # 直接tracerにわたすと，cliにBlockされる？？？ => CLIにわたす
        # tracer.start_tracing()
        connection = net.cli.cli_connection
        connection.input("starttracing")
    elif event == WSEvent.STOP_TRACING.value:
        tracer.stop_tracing()
    else:
        handler_string = event
        if isinstance(handler_string, WSEvent):
            handler_string = handler_string.value
        handler = getattr(net, handler_string, None)
        if not handler:
            raise Exception("No WebSocket handler exception. event={}, {}".format(event, param))
        if param:
            handler(**param)
        else:
            handler()


def exec_mininet_command_result_handler(event, result):
    if event == WSEvent.EXEC_MININET_COMMAND_RESULT \
            and isinstance(result, CommandResult):
        socketio_server.emit(event.event_name, result)
    else:
        logger.error("type error")


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
    message_hub.emit2net(event=event, param={})


@socketio_server.on(WSEvent.STOP_TRACING.event_name, namespace=NAME_SPACE)
def stop_tracing(sid, data):
    event = WSEvent.STOP_TRACING
    req = StopTracingRequest()
    req.ParseFromString(data)
    message_hub.emit2net(event=event, param={})


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
    message_hub.emit2net(event=event, param=param)


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
    message_hub.emit2net(event=event, param=param)


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
    message_hub.emit2net(event=event, param=param)


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
    message_hub.emit2net(event=event, param=param)


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
    param = {'link_name': link.name, 'host_name1': link.host1, 'host_name2': link.host2}
    message_hub.emit2net(event=event, param=param)


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
    message_hub.emit2net(event=event, param=param)


@socketio_server.on(WSEvent.GET_TRACE.event_name, namespace=NAME_SPACE)
def get_trace(sid, data):
    """
    #. メッセージを受け取る
    #. tracesを受け取るためのメッセージを送る
    #. tracesを受け取るためにparent.recv()で待つ
    #. tracesを受け取る
    #. tracesをprotobufに変換(変換されていたらなし)
    #. 送信する
    """
    event = WSEvent.GET_TRACE
    get_trace_req = GetTraceRequest()
    get_trace_req.ParseFromString(data)
    message_hub.emit2net(event=event, param={})
    traces = message_hub.wait_traces()
    asyncio.ensure_future(socketio_server.emit(event='get_trace', data=traces))


@socketio_server.on(WSEvent.EXEC_MININET_COMMAND.event_name, namespace=NAME_SPACE)
def exec_mininet_command(sid, data):
    event = WSEvent.EXEC_MININET_COMMAND
    mininet_command = MininetCommand()
    mininet_command.ParseFromString(data)
    message_hub.emit2net(event=event, param={"command": mininet_command.command})
    logger.debug("wait mininet command")
    message_hub.wait_command_result(exec_mininet_command_result_handler)


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
    await runner.setup()
    site = web.TCPSite(runner, host=ip, port=port)
    await site.start()
    await asyncio.Event().wait()


async def ws_server_stop_coro():
    await runner.cleanup()


if __name__ == '__main__':
    message_hub = TestMessageHub()

    def callback(event, param):
        print(str(event) + str(param))

    ws_server_start()
