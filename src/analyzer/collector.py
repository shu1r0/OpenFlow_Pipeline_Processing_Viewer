from src.tracing_net.flowtable import table_repository
from src.tracing_net.packet import packet_repository
from src.ofcapture.capture import of_msg_repository


def collect(nodes, edges, until=None):
    """

    Args:
        nodes:
        edges:
        until:

    Returns:
        list
    """
    raise NotImplementedError


def poll_proxy(ofcaputre, until):
    raise NotImplementedError


def poll_net(tracing_net, util):
    raise NotImplementedError
