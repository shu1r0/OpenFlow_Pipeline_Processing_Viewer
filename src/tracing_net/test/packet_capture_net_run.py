from logging import getLogger, Logger, DEBUG, StreamHandler, Formatter, handlers
import datetime
import time

from net.net import TracingNet
from api.grpc_client import gRPCClient
from mininet.cli import CLI


def packet_capture_net_run():
    net = TracingNet(controller_port=6653)
    net.start()
    net.grpc_server_start()
    client = gRPCClient()
    client.add_switch('s1')
    client.add_host('h1')
    client.add_link("l1", "s1", "h1")
    client.add_host('h2')
    client.add_link("l2", "s1", "h2")
    net.start_all_packet_capture_processes()
    net.cli_run()
    # time.sleep(10)
    net.grpc_server_stop()
    net.stop()