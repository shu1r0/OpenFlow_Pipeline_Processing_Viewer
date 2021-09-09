from aiohttp import web
import socketio
from logging import getLogger, setLoggerClass, Logger


setLoggerClass(Logger)
logger = getLogger('tracing_net.api.ws_server')


net = None
NET_EVENT = {
    'add_host': net.add_host,
    'remove_host': net.remove_host,
    'add_switch': net.add_switch,
}


class MessageHub:
    """for multiprocess."""

    def __init__(self):
        self.parent_con = None
        self.child_con = None

    def receive(self, event, data):
        pass




NAME_SPACE = '/ws'

socketio_server = socketio.AsyncServer()
web_app = web.Application()
# socketio_server.attach(web_app)


@socketio_server.event(namespace=NAME_SPACE)
def connect(sid, environ, auth):
    logger.info('connect sid={}'.format(sid))


@socketio_server.event(namespace=NAME_SPACE)
def disconnect(sid):
    logger.info('disconnect sid={}'.format(sid))


@socketio_server.event(namespace=NAME_SPACE)
def connected(sid, data):
    pass


def ws_server_emit(event, data):
    pass


