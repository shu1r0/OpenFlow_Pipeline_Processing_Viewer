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
import multiprocessing
import threading
import pickle
import time

# add module path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ofcapture'))

# print module path
import pprint
# print("module path:")
pprint.pprint(sys.path)

# patches asyncio
import nest_asyncio
nest_asyncio.apply()
# __import__('IPython').embed()

from pyof.v0x04.common.utils import unpack_message

from src.ofcapture.ofcapture import OFCaptureWithPipe
from src.ofcapture.capture.of_msg_repository import packet_in_out_repo
from tracing_net.utils.log import setup_tracingnet_logger
from tracing_net.net.net import TracingNet
from src.analyzer.analyzer import Analyzer

from utils.log import get_log_handler, setup_logger


MODE_DEBUGGING = True


class AbstractTracingOFPipeline(metaclass=ABCMeta):
    """Abstract Tracing OpenFlow pipeline

    This is a abstract Tracing OpenFlow Pipeline class. The class integrates components.
    This provides interfaces to start and stop system, to start and stop tracing and more.
    """

    def __init__(self, local_port=63333, log_level=DEBUG, log_file=None):
        self.event_loop = asyncio.get_event_loop()

        parent_conn, child_conn = multiprocessing.Pipe()
        default_logfile = "log/" + "ofcapture-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"  # debug用
        self.ofcapture = OFCaptureWithPipe(log_file=default_logfile, local_port=local_port,
                                   event_loop=self.event_loop, parent_conn=parent_conn)
        self._child_conn_thread = threading.Thread(target=self._handle_child_conn, args=(child_conn, ))

        if log_file:
            setup_tracingnet_logger(log_level=log_level, log_handler=get_log_handler(log_file))
            setup_logger(log_level=log_level, log_handler=get_log_handler(log_file))
        self.tracing_net = TracingNet(controller_port=local_port)
        # web server
        self.tracing_server = None
        self.analyzer = Analyzer(self.tracing_net,
                                 self.ofcapture,
                                 self.tracing_net.packet_repo(),
                                 self.tracing_net.table_repo(),
                                 self.ofcapture.capture.get_packet_in_out_repo())

        setLoggerClass(Logger)
        self.logger = getLogger('tracing_of_pipeline')

    def start(self):
        """

        #. web server start
        #. config network
        #. start network

        Returns:

        """
        p = multiprocessing.Process(target=self.ofcapture.start_server, daemon=True)
        p.start()
        self._child_conn_thread.daemon = True
        self._child_conn_thread.start()
        self.tracing_net.start()

    def stop(self):
        self.tracing_net.stop()

    def start_tracing(self):
        self.tracing_net.start_tracing()
        self.analyzer.start_analyzing()

    def stop_tracing(self):
        self.tracing_net.stop_tracing()

    def _handle_child_conn(self, child_conn):
        while True:
            data = child_conn.recv_bytes()
            msg = pickle.loads(data)
            msg.of_msg = unpack_message(msg.of_msg)
            self.logger.debug("get from ofcapture {}".format(msg))
            self.analyzer.packet_inout_repo.add(msg)


class TracingOFPipeline(AbstractTracingOFPipeline):

    def __init__(self, log_file=None):
        super(TracingOFPipeline, self).__init__(log_file=log_file)


if __name__ == '__main__':
    log_file = 'log/' + "tracing_of_pipeline-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"  # debug用
    tracing = TracingOFPipeline(log_file=log_file)
    net = tracing.tracing_net
    tracing.start()
    controller = net.of_controller
    # start controller
    controller.cmd("ryu-manager test/ryu_controller/app/simple_switch_13.py &")
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
