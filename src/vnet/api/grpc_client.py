import grpc
from src.vnet.api.tracer_net_pb2 import *
from src.vnet.api import tracer_net_pb2_grpc

class gRPCClient():

    def __init__(self, ip='localhost', port='50051'):
        self.channel = grpc.insecure_channel(ip + ':' + port)
        self.stub = tracer_net_pb2_grpc.TracerNetServiceStub(self.channel)

    def add_host(self, name):
        node_req = Node(node_type=NodeType.HOST, name=name)
        result = self.stub.addNode(node_req)
        return result.status

    def add_switch(self, name):
        node_req = Node(node_type=NodeType.SWITCH, name=name)
        result = self.stub.addNode(node_req)
        return result.status

    def add_link(self, name, host_name1, host_name2):
        link_req = Link(name=name, host_name1=host_name1, host_name2=host_name2)
        result = self.stub.addLink(link_req)
        return result.status