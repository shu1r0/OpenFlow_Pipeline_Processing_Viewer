"""

flow:
0. tracing network init
1. web server start
2. config network
3. start network
4. tracing start
5. start analyzer
6. stop tracing
"""
from abc import ABCMeta
from logging import getLogger, Logger, DEBUG, INFO, StreamHandler, Formatter, handlers, setLoggerClass
import datetime
import asyncio

import sys
import os
# add module path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ofcapture'))
import pprint
# print("module path:")
pprint.pprint(sys.path)

from src.ofcapture.ofcapture import OFCapture
from tracing_net.utils.log import setup_tracingnet_logger
from tracing_net.net.net import TracingNet
from src.analyzer.analyzer import Analyzer

from utils.log import get_log_handler, setup_logger


class AbstractTracingOFPipeline(metaclass=ABCMeta):
    """Abstract Tracing OpenFlow pipeline

    This is a abstract Tracing OpenFlow Pipeline class. The class integrates components.
    This provides interfaces to start and stop system, to start and stop tracing and more.
    """

    def __init__(self, log_level=DEBUG, log_file=None):
        self.event_loop = asyncio.get_event_loop()
        default_logfile = "log/" + "ofcapture-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"  # debug用
        self.ofcapture: OFCapture = OFCapture(log_file=default_logfile, local_port=63334)
        if log_file:
            setup_tracingnet_logger(log_level=log_level, log_handler=get_log_handler(log_file))
            setup_logger(log_level=log_level, log_handler=get_log_handler(log_file))
        self.tracing_net = TracingNet(controller_port=6653)
        self.tracing_server = None
        self.analyzer = Analyzer(self.tracing_net,
                                 self.ofcapture,
                                 self.tracing_net.packet_repo(),
                                 self.tracing_net.table_repo(),
                                 self.ofcapture.capture.get_packet_in_out_repo())

    def start(self):
        """

        #. web server start
        #. config network
        #. start network

        Returns:

        """
        self.tracing_net.start()
        asyncio.ensure_future(self.ofcapture.start_server_coro())
        # self.ofcapture.start_server()

    def stop(self):
        self.tracing_net.stop()

    def start_tracing(self):
        self.tracing_net.start_tracing()
        self.analyzer.start_analyzing()

    def stop_tracing(self):
        self.tracing_net.stop_tracing()


class TracingOFPipeline(AbstractTracingOFPipeline):

    def __init__(self, log_file=None):
        super(TracingOFPipeline, self).__init__(log_file=log_file)


if __name__ == '__main__':
    log_file = 'log/' + "tracing_of_pipeline-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"  # debug用
    tracing = TracingOFPipeline(log_file=log_file)
    net = tracing.tracing_net
    tracing.start()
    s1 = net.add_switch('s1')

    # add_hostとリンクはセットにしないとエラー(インタフェースの設定がおかしくなる)
    h1 = net.add_host('h1')
    net.add_link('l2', 's1', 'h1')

    s2 = net.add_switch('s2')
    net.add_link('l1', 's1', 's2')

    h2 = net.add_host('h2')
    net.add_link('l3', 's2', 'h2')
    tracing.start_tracing()
    net.cli_run()
    tracing.stop_tracing()
    tracing.stop()
