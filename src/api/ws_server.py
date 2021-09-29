"""
Web socket API

TODO:
    * まずは，接続し，ホストなどを配置できるようにする．
"""
from enum import Enum
from aiohttp import web
from abc import abstractmethod, ABCMeta
import socketio
from logging import getLogger, setLoggerClass, Logger


setLoggerClass(Logger)
logger = getLogger('tracing_net.api.ws_server')


from .proto.net_pb2 import Host, Switch, Link, PacketTrace, StartTracingRequest, StopTracingRequest


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
            param (dict) :
        """
        raise NotImplementedError

    @abstractmethod
    def emit2client(self, event: WSEvent, param):
        """emit to client"""
        raise NotImplementedError

    @abstractmethod
    def get_from_client(self, net, call_back):
        """receive message sent from client"""
        raise NotImplementedError


class MessageHub(MessageHubBase):
    """for multiprocess."""

    def __init__(self, parent_con=None, child_con=None):
        super(MessageHub, self).__init__(parent_con, child_con)

    def emit2net(self, event: WSEvent, param):
        logger.debug("MessageHub receives messages from clients and emits them to the vnet. (event={}, param={})".format(event, param))
        event = event.value
        self.parent_con.send({'event': event, 'param': param})

    def emit2client(self, event: WSEvent, param):
        pass

    def get_from_client(self, net, call_back):
        while True:
            if self.child_con.poll():
                response = self.child_con.recv()
                call_back(net, event=response['event'], param=response['param'])


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

    def get_from_client(self, net, call_back):
        pass


# message hub instance
# もし，これを使う場合は，変数を初期化する
message_hub = MessageHub()


def get_messsage_hub(parent_con, child_con):
    message_hub.parent_con = parent_con
    message_hub.child_con = child_con
    return child_con

#
# Web Socket Server
#
#

NAME_SPACE = ''


# socket server
# CORSのオリジン設定をすべて許可に
socketio_server = socketio.AsyncServer(cors_allowed_origins='*')

# web application
web_app = web.Application()
socketio_server.attach(web_app)


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
    raise NotImplementedError


@socketio_server.on(WSEvent.EXEC_NODE_COMMAND.event_name, namespace=NAME_SPACE)
def exec_node_command(sid, data):
    raise NotImplementedError


def ws_server_start(ip="0.0.0.0", port=8888):
    web.run_app(web_app, host=ip, port=port)


def exec_wsevent_action(net, event: WSEvent, param):
    """callback for messagehub

    Args:
        net:
        event:
        param:

    Returns:

    """
    handler_string = event.value
    handler = getattr(net, handler_string)
    if not handler:
        raise Exception("No WebSocket handler exception")
    if param:
        handler(**param)
    else:
        handler()

#
# def ws_server_stop():
#     web_app.shutdown()


if __name__ == '__main__':
    message_hub = TestMessageHub()

    def callback(event, param):
        print(str(event) + str(param))

    ws_server_start()
