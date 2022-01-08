"""

flow:
0. tracing network init
1. web server start
2. config network
3. start network
4. tracing start
5. start analyzer
6. stop tracing

TODO:
    * WS server と他の動作がうまく行かない問題
        * Processの順番の問題か？？？
    * なぜかProxyが動作しない？？？
        * tracing_startをしなければ，通常通り動く
        * logに反映されていないこともあるが，PacketInなどが無いとそもそもpingが通らん
        * asyncioがわるい？？？ => proxyのasyncioなしでやってみる
        * pakcetなどのThreadをdeamon化したのでテストしてみる
        * tracingの前に時間をおいてみる
        * local2では動く
        * 受け取り側が悪い可能性はあるか？？(つまり，受け取れなくてsendが呼び出せていない => Queueに帰るのも手)

    * フローテーブルがわるい問題
        * 多分取得できてない
        * 至急，変更をする
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
from pyof.v0x04.common.header import Type

from src.ofcapture.ofcapture import OFCaptureWithPipe
from tracing_net.utils.log import setup_tracingnet_logger
from tracing_net.net.net import TracingNet
from src.analyzer.analyzer import Analyzer
from src.analyzer.packet_trace_handler import packet_trace_list
from src.api.ws_server import ws_server_start_coro, message_hub
from src.tracing_net.flowtable.table_repository import table_repository
from src.config import conf
from src.tracing_net.net.cli import WSCLIConnection, TracingCLI
from src.tracing_net.ofproto.instruction import parse_from_obj
from src.tracing_net.ofproto.match import Match
from src.tracing_net.ofproto.table import Flow

from utils.log import get_log_handler, setup_logger


class AbstractTracingOFPipeline(metaclass=ABCMeta):
    """Abstract Tracing OpenFlow pipeline

    This is a abstract Tracing OpenFlow Pipeline class. The class integrates components.
    This provides interfaces to start and stop system, to start and stop tracing and more.
    """

    def __init__(self):
        # conf obj
        self.conf = conf
        self.event_loop = asyncio.get_event_loop()

        # ofcapture
        ofc_parent_conn, ofc_child_conn = multiprocessing.Pipe()
        default_logfile = self.conf.LOGFILE_OFCAPTURE

        self.ofcapture = OFCaptureWithPipe(log_file=default_logfile, local_port=self.conf.LOCAL_PORT,
                                           controller_ip=self.conf.CONTROLLER_IP, controller_port=self.conf.CONTROLLER_PORT,
                                           event_loop=asyncio.new_event_loop(), parent_conn=ofc_parent_conn,
                                           log_level=self.conf.LOGLEVEL_OFCAPTURE)
        self._ofc_process = multiprocessing.Process(target=self.ofcapture.start_server, daemon=True)
        # self._ofc_process = multiprocessing.Process(target=OFCaptureWithPipe, args=(
        #     '127.0.0.1', conf.LOCAL_PORT, conf.CONTROLLER_IP, conf.CONTROLLER_PORT, None, default_logfile,
        #     conf.LOGLEVEL_OFCAPTURE, ofc_parent_conn, True
        # ))
        self._ofc_child_conn_thread = threading.Thread(target=self._handle_ofc_child_conn, args=(ofc_child_conn, ))

        # WS CLI
        cli_connection = WSCLIConnection(message_hub=message_hub, output_stdout=conf.WS_CLI_OUTPUT_STDOUT, event_loop=self.event_loop)

        # mininet network
        log_file = self.conf.LOGFILE_OFPIPELINE_TRACER
        if log_file:
            setup_tracingnet_logger(log_level=self.conf.LOGLEVEL_OFPIPELINE_TRACER, log_handler=get_log_handler(log_file))
            setup_logger(log_level=self.conf.LOGLEVEL_OFPIPELINE_TRACER, log_handler=get_log_handler(log_file))

        self.tracing_net = TracingNet(controller_port=self.conf.LOCAL_PORT,
                                      mininet_log_level=self.conf.MININET_LOG_LEVEL,
                                      cli_connection=cli_connection,
                                      event_loop=self.event_loop)

        message_hub.set_tracer_handler(self)

        # analyzer
        self.analyzer = Analyzer(self.tracing_net,
                                 self.ofcapture,
                                 self.tracing_net.packet_repo(),
                                 self.tracing_net.table_repo(),
                                 self.ofcapture.capture.get_packet_in_out_repo())

        # logger
        setLoggerClass(Logger)
        self.logger = getLogger('tracing_of_pipeline')

    def start(self):
        """start all server

        #. web server start
        #. config network
        #. start network
        """
        self.logger.info("OpenFlow Tracer Start")
        # proxy start
        self._ofc_process.start()
        self._ofc_child_conn_thread.daemon = True
        self._ofc_child_conn_thread.start()

        # mininet start
        # self.tracing_net.start()

        # 本当はstart_tracingで実行したい
        # 内部でsignalを使用しているので，WebSocketから(スレッドから)呼び出せない
        # self.analyzer.start_analyzing()

    def stop(self):
        self.logger.info("OpenFlow Tracer Stop")

        if conf.OUTPUT_TRACES_WHEN_SYSTEM_IS_FINISHED:
            packet_trace_list.print()

        self._ofc_process.terminate()

        self.tracing_net.stop()

    def start_net(self):
        self.tracing_net.start()

    def start_tracing(self):
        """start packet capture and polling flow table
        """
        self.tracing_net.start_tracing()
        self.analyzer.start_analyzing()

    def stop_tracing(self):
        """stop packet capture and polling flow table
        """
        self.tracing_net.stop_tracing()
        self.analyzer.stop_analyzing()
        if conf.OUTPUT_FLOWTABLES_TO_FILE:
            table_repository.output()
        if conf.OUTPUT_PACKET_PROCESSING_TO_FILE:
            packet_trace_list.output()

    def start_ws_and_cli(self):
        """
         * Web系はサブプロセスとして，メインプロセスではCLIと
            => WEB CLI はメインプロセスでまとめる
        Returns:

        """
        # asyncio.ensure_future(hello())
        try:
            if conf.ENABLE_WS_SERVER:
                self.event_loop.run_until_complete(asyncio.gather(*[
                    ws_server_start_coro(conf.WS_SERVER_IPADDRESS, conf.WS_SERVER_PORT),
                    self.tracing_net.ws_cli_run()
                ]))
        except KeyboardInterrupt:
            # todo close
            pass

    def _handle_ofc_child_conn(self, child_conn):
        while True:
            try:
                data = child_conn.recv_bytes()
                msg = pickle.loads(data)
                msg.of_msg = unpack_message(msg.of_msg)
                if msg.message_type == Type.OFPT_PACKET_IN \
                        or msg.message_type == Type.OFPT_PACKET_OUT:
                    self.analyzer.packet_inout_repo.add(msg)
                elif msg.message_type == Type.OFPT_FLOW_MOD:
                    # todo: parse Flow Mod (add)
                    instructions = msg.of_msg.instructions
                    instructions = parse_from_obj(instructions)
                    matches = Match.parse_from_ofcapture(msg.of_msg.match)
                    flow = Flow(
                        cookie=hex(int(msg.of_msg.cookie)),
                        duration=0,
                        table=int(msg.of_msg.table_id),
                        priority=int(msg.of_msg.priority),
                        match=matches,
                        actions=instructions
                    )
                    switch = self.tracing_net.get_switch_from_dpid(msg.datapath_id)
                    table_repository.add_flow(msg.datapath_id, switch, flow, msg.timestamp)

            except EOFError:
                self.logger.debug("get EOFError from ofcapture")
                break


class TracingOFPipeline(AbstractTracingOFPipeline):

    def __init__(self):
        super(TracingOFPipeline, self).__init__()


#
# ↓ test code
#


def run_local():
    tracing = TracingOFPipeline()
    net = tracing.tracing_net
    tracing.start()
    controller = net.of_controller
    # start controller
    controller.cmd("ryu-manager test/ryu_controller/app/simple_switch_13.py &")
    s1 = net.add_switch('s0')
    # add_hostとリンクはセットにしないとエラー(インタフェースの設定がおかしくなる)
    h1 = net.add_host('h0')
    net.add_link('l2', 's0', 'h0')

    h2 = net.add_host('h1')
    net.add_link('l3', 's0', 'h1')

    net.add_switch('s1')
    net.add_link('l1', 's0', 's1')

    net.add_host('h2')
    net.add_link('l4', 's1', 'h2')

    net.add_host('h3')
    net.add_link('l5', 's1', 'h3')

    tracing.start_tracing()
    net.cli_run()
    tracing.stop_tracing()
    tracing.stop()


def run_local2():
    tracing = TracingOFPipeline()
    net = tracing.tracing_net
    tracing.start()
    controller = net.of_controller
    # start controller
    controller.cmd("ryu-manager test/ryu_controller/logging_app/simple_switch_13_with_log.py &")
    s1 = net.add_switch('s1')
    # add_hostとリンクはセットにしないとエラー(インタフェースの設定がおかしくなる)
    h1 = net.add_host('h1')
    net.add_link('l2', 's1', 'h1')

    s2 = net.add_switch('s2')
    net.add_link('l1', 's1', 's2')

    h2 = net.add_host('h2')
    net.add_link('l3', 's2', 'h2')

    net.add_host('h3')
    net.add_link('l4', 's1', 'h3')

    tracing.start_net()
    tracing.start_tracing()
    net.cli_run()
    tracing.stop_tracing()
    tracing.stop()

def run_local_router():
    tracing = TracingOFPipeline()
    net = tracing.tracing_net
    tracing.start()
    controller = net.of_controller
    # start controller
    # controller.cmd("ryu-manager test/ryu_controller/logging_app/simple_switch_13_with_log.py &")
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    h1 = net.addHost('h1', ip="192.168.1.2/24")
    h2 = net.addHost('h2', ip="192.168.3.2/24")

    net.addLink(s1, h1)
    net.addLink(s1, s2)
    net.addLink(s2, h2)

    # tracing.start_net()
    tracing.start_tracing()
    net.hosts[0].cmd("route add default gw 192.168.1.1")
    net.hosts[1].cmd("route add default gw 192.168.3.1")
    net.cli_run()
    tracing.stop_tracing()
    tracing.stop()


def run_local2_with_async():

    tracing = TracingOFPipeline()
    net = tracing.tracing_net
    tracing.start()
    controller = net.of_controller
    # start controller
    controller.cmd("ryu-manager test/ryu_controller/logging_app/simple_switch_13_with_log.py &")
    s1 = net.add_switch('s1')
    # add_hostとリンクはセットにしないとエラー(インタフェースの設定がおかしくなる)
    h1 = net.add_host('h1')
    net.add_link('l2', 's1', 'h1')

    s2 = net.add_switch('s2')
    net.add_link('l1', 's1', 's2')

    h2 = net.add_host('h2')
    net.add_link('l3', 's2', 'h2')

    net.add_host('h3')
    net.add_link('l4', 's1', 'h3')

    tracing.start_tracing()
    async def hello():
        print("hello")
        while True:
            await asyncio.sleep(5)
            print("print hello")
    print(asyncio.ensure_future(hello()))
    print(asyncio.all_tasks(asyncio.get_event_loop()))
    net.cli_run()
    tracing.stop_tracing()
    tracing.stop()


def run_with_web():
    tracing = TracingOFPipeline()
    net = tracing.tracing_net
    tracing.start()
    controller = net.of_controller
    # controller.cmd("ryu-manager test/ryu_controller/logging_app/simple_switch_13_with_log.py &")
    # net.start_tracing()

    # async def hello():
    #     print("hello")
    #     while True:
    #         await asyncio.sleep(5)
    #         print("print hello")
    # print(asyncio.ensure_future(hello()))
    # print(asyncio.all_tasks(asyncio.get_event_loop()))

    tracing.start_ws_and_cli()

    tracing.stop_tracing()
    tracing.stop()


if __name__ == '__main__':
    if conf.ENABLE_WS_SERVER:
        run_with_web()
    else:
        run_local_router()
