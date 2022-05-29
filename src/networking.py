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
from logging import getLogger, Logger, DEBUG, INFO, StreamHandler, Formatter, handlers, setLoggerClass
import datetime
import asyncio
import multiprocessing
import threading
import pickle

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

from src.vnet.flowtable.table_repository import table_repository
from src.vnet.utils.log import setup_tracingnet_logger
from src.vnet.net.net import NetworkGatheringInfo
from src.vnet.net.cli import WSCLIConnection
from src.vnet.ofproto.instruction import parse_from_obj
from src.vnet.ofproto.match import Match
from src.vnet.ofproto.table import Flow

from src.ofcapture.ofcapture import OFCaptureWithPipe
from src.analyzer.analyzer import Analyzer
from src.analyzer.packet_trace_handler import packet_trace_list
from src.api.ws_server import WSServer
from src.config import conf

from utils.log import get_log_handler, setup_logger


class OFNetworking:

    def __init__(self):
        # conf obj
        self.conf = conf
        self.event_loop = asyncio.get_event_loop()

        # ofcapture
        ofc_parent_conn, ofc_child_conn = multiprocessing.Pipe()
        default_logfile = self.conf.LOGFILE_OFCAPTURE

        self.ofcapture = OFCaptureWithPipe(log_file=default_logfile,
                                           local_port=self.conf.LOCAL_PORT,
                                           controller_ip=self.conf.CONTROLLER_IP,
                                           controller_port=self.conf.CONTROLLER_PORT,
                                           event_loop=asyncio.new_event_loop(),
                                           parent_conn=ofc_parent_conn,
                                           log_level=self.conf.LOGLEVEL_OFCAPTURE)

        self._ofc_process = multiprocessing.Process(target=self.ofcapture.start_server, daemon=True)
        self._ofc_child_conn_thread = threading.Thread(target=self._handle_ofc_child_conn, args=(ofc_child_conn, ))

        # mininet network
        log_file = self.conf.LOGFILE_NETWORKING
        if log_file:
            setup_tracingnet_logger(log_level=self.conf.LOGLEVEL_NETWORKING, log_handler=get_log_handler(log_file))
            setup_logger(log_level=self.conf.LOGLEVEL_NETWORKING, log_handler=get_log_handler(log_file))

        # WS CLI
        cli_connection = WSCLIConnection(output_stdout=conf.WS_CLI_OUTPUT_STDOUT, event_loop=self.event_loop)
        self.net = NetworkGatheringInfo(controller_port=self.conf.LOCAL_PORT,
                                        mininet_log_level=self.conf.MININET_LOG_LEVEL,
                                        cli_connection=cli_connection,
                                        event_loop=self.event_loop)

        # websocket server
        self.ws_server = WSServer(networking=self, net=self.net, ip=conf.WS_SERVER_IPADDRESS, port=conf.WS_SERVER_PORT)

        # analyzer
        self.analyzer = Analyzer(self.net,
                                 self.ofcapture,
                                 self.net.packet_repo(),
                                 self.net.table_repo(),
                                 self.ofcapture.capture.get_packet_in_out_repo())

        # logger
        setLoggerClass(Logger)
        self.logger = getLogger('tracing_of_pipeline')

    def start(self, analyzer: bool = False):
        """start all server """
        self.logger.info("OpenFlow Networking Start")
        self.net.start()
        self._start_gathering()
        if analyzer:
            self.analyzer.start_analyzing()

    def stop(self):
        self.logger.info("OpenFlow Networking Stop")

        self.stop_tracing()

        if conf.OUTPUT_TRACES_WHEN_SYSTEM_IS_FINISHED:
            packet_trace_list.print()

        self._ofc_process.terminate()

        self.net.stop()

    def stop_tracing(self):
        self.analyzer.stop_analyzing()
        self.net.stop_gathering()
        if conf.OUTPUT_FLOWTABLES_TO_FILE:
            table_repository.output()
        if conf.OUTPUT_PACKET_PROCESSING_TO_FILE:
            packet_trace_list.output()

    def _start_gathering(self):
        if not self.net.is_mininet_start:
            raise Exception("mininet does not start")
        # proxy start
        self._ofc_process.start()
        self._ofc_child_conn_thread.daemon = True
        self._ofc_child_conn_thread.start()

        self.net.start_gathering()

    def start_ws_interface(self):
        self.event_loop.run_until_complete(asyncio.gather(*[
            self.ws_server.start_coro(),
            self.net.run_ws_cli()
        ]))

    def run_local_cli(self):
        self.net.run_cli()

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
                    switch = self.net.get_switch_from_dpid(msg.datapath_id)
                    table_repository.add_flow(msg.datapath_id, switch, flow, msg.timestamp)

            except EOFError:
                self.logger.debug("get EOFError from ofcapture")
                break


def run_networking(loglevel=None, controller_ip=None, controller_port=None, ws_port=None, flow_monitor_interval=None,
                   controller_init="ryu-manager test/ryu_controller/app/simple_switch_13.py &"):
    if loglevel:
        conf.LOGLEVEL_NETWORKING = loglevel
    if controller_ip:
        conf.CONTROLLER_IP = controller_ip
    if controller_port:
        conf.CONTROLLER_PORT = controller_port
    if ws_port:
        conf.WS_SERVER_PORT = ws_port
    if flow_monitor_interval:
        conf.FLOW_MONITOR_INTERVAL = flow_monitor_interval

    networking = OFNetworking()
    networking.net.of_controller.cmd(controller_init)

    try:
        networking.start_ws_interface()
    except KeyboardInterrupt:
        networking.stop()


def run_three_topo(loglevel=None, controller_ip=None, controller_port=None, flow_monitor_interval=None,
                   controller_init="ryu-manager test/ryu_controller/app/simple_switch_13.py &"):
    if loglevel:
        conf.LOGLEVEL_NETWORKING = loglevel
    if controller_ip:
        conf.CONTROLLER_IP = controller_ip
    if controller_port:
        conf.CONTROLLER_PORT = controller_port
    if flow_monitor_interval:
        conf.FLOW_MONITOR_INTERVAL = flow_monitor_interval

    networking = OFNetworking()
    net = networking.net
    net.of_controller.cmd(controller_init)
    net.add_switch('s0')
    net.add_host('h0')
    net.add_host('h1')

    net.add_link('l0', 's0', 'h0')
    net.add_link('l1', 's0', 'h1')

    networking.start(analyzer=True)
    networking.run_local_cli()
    networking.stop()


#
# ↓ test code
#


def run_local_router():
    tracing = OFNetworking()
    net = tracing.net
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
    tracing.start()
    net.hosts[0].cmd("route add default gw 192.168.1.1")
    net.hosts[1].cmd("route add default gw 192.168.3.1")
    tracing.run_local_cli()
    tracing.stop_tracing()
    tracing.stop()


if __name__ == '__main__':
    run_networking()
