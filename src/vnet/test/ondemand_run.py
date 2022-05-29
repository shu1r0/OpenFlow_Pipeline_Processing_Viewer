
from net.net import TracedNet
from api.grpc_client import gRPCClient
from mininet.cli import CLI

if __name__ == '__main__':
    net = TracedNet()
    net.start()
    net.grpc_server_start()
    client = gRPCClient()
    client.add_switch('s1')
    client.add_host('h1')
    client.add_link("l1", "s1", "h1")
    client.add_host('h2')
    client.add_link("l2", "s1", "h2")
    CLI(net.mininet)
    net.grpc_server_stop()
    net.stop()