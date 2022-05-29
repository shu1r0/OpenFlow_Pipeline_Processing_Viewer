import grpc
from src.vnet.api.tracer_net_pb2 import NodeType, Node, Link, Result
from src.vnet.api import tracer_net_pb2_grpc
from concurrent import futures
# from net.net import TracerNet

class TracerNetService(tracer_net_pb2_grpc.TracerNetServiceServicer):
    """gRPC Service"""

    def __init__(self, tracer_net):
        """

        Args:
            tracer_net (TracerNet) :
        """
        self.tracer_net = tracer_net

    def addNode(self, request, context):
        node_type = request.node_type
        name = request.name
        status = None
        if node_type == NodeType.HOST:
            status = self.tracer_net.add_host(name)
        if node_type == NodeType.SWITCH:
            status = self.tracer_net.add_switch(name)
        if not status:
            status = 0
        else:
            status = -1
        return Result(status=status)


    def removeNode(self, request, context):
        node_type = request.node_type
        name = request.name
        status = None
        if node_type == NodeType.HOST:
            status = self.tracer_net.remove_host(name)
        if node_type == NodeType.SWITCH:
            status = self.tracer_net.remove_switch(name)
        if not status:
            status = 0
        else:
            status = -1
        return Result(status=status)

    def addLink(self, request, context):
        name = request.name
        host1 = request.host_name1
        host2 = request.host_name2
        status = self.tracer_net.add_link(name, host1, host2)
        if not status:
            status = 0
        else:
            status = -1
        return Result(status=status)

    def removeLink(self, request, context):
        name = request.name
        host1 = request.host_name1
        host2 = request.host_name2
        if name:
            status = self.tracer_net.remove_link(name)
        else:
            status = self.tracer_net.remove_link_between(host1, host2)
        if not status:
            status = 0
        else:
            status = -1
        return Result(status=status)


class TracerNetServer:
    """gRPC server

    Attributes:
        service : gRPC service
        ip : server ip address
        port : server port number
    """

    def __init__(self, tracer_net, ip='[::]', port='50051'):
        self.service = TracerNetService(tracer_net)
        self.ip = ip
        self.port = port

    def start(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        tracer_net_pb2_grpc.add_TracerNetServiceServicer_to_server(
            self.service, self.server
        )
        self.server.add_insecure_port(self.ip + ':' + self.port)
        self.server.start()

    def stop(self):
        self.server.stop(grace=None)
