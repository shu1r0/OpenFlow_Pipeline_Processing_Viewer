from src.web_server.app import socketio

NAME_SPACE = None


@socketio.on('addNode', namespace=NAME_SPACE)
def add_node(msg):
    pass


@socketio.on('removeNode', namespace=NAME_SPACE)
def remove_node(msg):
    pass


@socketio.on('addLink', namespace=NAME_SPACE)
def add_link(msg):
    pass


@socketio.on('removeLink', namespace=NAME_SPACE)
def remove_link(msg):
    pass
