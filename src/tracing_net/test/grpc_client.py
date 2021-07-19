from api import grpc_client

if __name__ == '__main__':
    client = grpc_client.gRPCClient(ip='10.0.0.109')
    client.add_host('s2')
    # client.add_link('l2', "s1", "s2")