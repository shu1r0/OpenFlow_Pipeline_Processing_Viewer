from abc import ABCMeta, abstractmethod
import datetime
import copy
# unix
import signal
import time
from logging import getLogger, setLoggerClass, Logger

from pyof.v0x04.common.header import Type

from src.ofcapture.ofcapture import OFCapture
from src.tracing_net.net.net import TracingNet
from src.tracing_net.packet.packet_repository import PacketRepository
from src.tracing_net.flowtable.table_repository import TableRepository
from src.tracing_net.ofproto.table import FlowTables
from src.tracing_net.ofproto.msg import Msg
from src.ofcapture.capture.of_msg_repository import PacketInOutRepository
from src.ofproto.pipeline import apply_pipeline
from src.analyzer.packet_trace import PacketArc, PacketTrace


setLoggerClass(Logger)
logger = getLogger('tracing_of_pipeline.analyzer')

class AbstractAnalyzer(metaclass=ABCMeta):
    """This integrates information and computes packet trace.

    Attributes:
        tracing_net (TracingNet) :
        packet_repo (PacketRepository) :
        table_repo (TableRepository) :
        packet_inout_repo (PacketInOutRepository) :
    """

    def __init__(self, tracing_net, of_capture, packet_repo, table_repo, packet_inout_repo):
        """Init

        Args:
            tracing_net (TracingNet) :
            of_capture (OFCapture) :
            packet_repo (PacketRepository) :
            table_repo (TableRepository) :
            packet_inout_repo (PacketInOutRepository) :
        """
        self.tracing_net = tracing_net
        self.of_capture = of_capture
        self.packet_repo = packet_repo
        self.table_repo = table_repo
        self.packet_inout_repo = packet_inout_repo

    @abstractmethod
    def analyze(self, *args):
        """start analyzing"""
        raise NotImplementedError

    @abstractmethod
    def start_analyzing(self, call_back=None):
        """

        Args:
            call_back (Callable[[AbstractPacketTrace], None]) : a function with a list of packet trace as argument
        """
        raise NotImplementedError


class Analyzer(AbstractAnalyzer):
    """
    This computes the path of a packet.
    """

    def __init__(self, tracing_net, of_capture, packet_repo, table_repo, packet_inout_repo):
        super(Analyzer, self).__init__(tracing_net, of_capture, packet_repo, table_repo, packet_inout_repo)
        self._interval = 1
        self.start_time = None
        self.count = 0
        self.tmp_packets = {}
        self.tmp_flowtable = {}
        self.tmp_packetinout = {}

    def start_analyzing(self, call_back=None):
        self.start_time = datetime.datetime.now().timestamp()
        signal.signal(signal.SIGALRM, self.analyze)
        signal.setitimer(signal.ITIMER_REAL, 1, 1)

    def analyze(self, *args):
        self._polling(self.count)
        for s, p_io in self.tmp_packetinout.items():
            if p_io:
                if p_io.message_type == Type.OFPT_PACKET_OUT:
                    name = self.of_capture.capture.get_port_name(self.get_port(s), p_io.of_msg.actions.port)
                    logger.debug("I will processing packetout({}), port({})".format(p_io, name))
        self.count += 1

    def BFS(self, src_node, msg, edge, first_edge, next_tables, next_port):
        """BFS"""
        # packet traces
        trace = PacketTrace()
        # visited edges
        visited = []
        # never visited edges
        queue = []
        # append (edge, node, port)
        queue.append((src_node, msg, first_edge, next_tables, next_port))  # 仮

        visited.append(first_edge)
        # set in_port
        self._update_msg(msg, next_port=next_port)
        while queue:
            logger.debug("processing msg {}".format(msg))
            src_node, msg, edge, dst_node, dst_port = queue.pop(0)
            packet_arc = PacketArc(src=src_node, msg=msg)
            msg: Msg = msg
            # update arc
            packet_arc.edge = edge
            packet_arc.dst = dst_node
            packet_arc.dst_interface = dst_port

            trace.add_arc(copy.deepcopy(packet_arc))
            # next
            if isinstance(dst_node, FlowTables):
                # next ports
                ports_to_msg: list[tuple[str, Msg]] = apply_pipeline(msg, flowtables=dst_node)
                # This m is used only to get the msg
                for p, m in ports_to_msg:
                    # next switch, port, edge
                    next_switch, next_port, next_edge = self._get_next_and_edge(p)
                    if self._is_switch(next_switch):
                        self._update_msg(msg, next_port=next_port)
                        if next_edge not in visited:  # loop?
                            # get packet
                            msg = self._pop_packet(next_edge, msg, m.sniff_timestamp)
                            # get flowtable
                            flowtable = self._pop_flowtable(next_switch, m.sniff_timestamp)
                            # queue update
                            queue.append((msg, next_edge, flowtable, next_port))
                        else:
                            logger.debug("already visited edge")
                    else:
                        if next_port > 1000:  #TODO: controller
                            logger.debug("to controller message")
                            # get packet_in

    def _update_msg(self, msg, next_port):
        """

        Args:
            instruction_result:
            msg:

        Returns:

        Todo:
            * update in_port
        """
        msg.in_phy_port = next_port
        msg.in_port = next_port

    # def start_polling(self):
    #     pass

    def _polling(self, count):
        # TODO: このままだと前のやつが消える
        logger.debug("{}, {}".format(self.tracing_net.name_to_link.get_edges(), self.tracing_net.get_switch_names()))
        self.tmp_packets = self._poll_packet_repo(count=count, edges=self.tracing_net.name_to_link.get_edges())
        self.tmp_flowtable = self._poll_table_repo(count=count, switches=self.tracing_net.get_switch_names())
        self.tmp_packetinout = self._poll_packet_inout_repo(count=count, switches=self.tracing_net.get_switch_names())
        logger.debug("polled (start_time={}, until={}) values = {} {} {}".format(self.start_time, self.count, self.tmp_packets, self.tmp_flowtable, self.tmp_packetinout))

    def _poll_packet_repo(self, count, edges):
        packets = {}
        until = self.start_time + self._interval * count
        for edge in edges:
            interface = self.tracing_net.name_to_link.get_int_name_pairs(edge)[0]
            tmp_packets = self.packet_repo.pop(interface, until=until)
            packets[edge] = tmp_packets
        return packets

    def _poll_table_repo(self, count, switches):
        tables = {}
        until = self.start_time + self._interval * count
        for switch in switches:
            tmp_table = self.table_repo.pop(switch=switch, until=until)
            tables[switch] = tmp_table
        return tables

    def _poll_packet_inout_repo(self, count, switches):
        packet_inouts = {}
        until = self.start_time + self._interval * count
        for switch in switches:
            s_port = self.get_port(switch)
            tmp_p = self.packet_inout_repo.pop(port=s_port, until=until)
            packet_inouts[switch] = tmp_p
        return packet_inouts

    def _get_topo(self):
        topo = self.tracing_net.get_topo()
        return topo

    def get_port(self, switch):
        datapath_id = self.tracing_net.get_datapath_id(switch)
        return self.of_capture.capture.get_port(datapath_id)

    def _get_next_and_edge(self, interface):
        return self.tracing_net.name_to_link.get_next_and_edge(interface)

    def _pop_packet(self, edge, msg, timestamp):
        """

        Args:
            edge (str) :
            msg (Msg) :
            timestamp (float) :

        Returns:

        Notes:
            * to implement a check for match
        """
        for p in self.tmp_packets[edge]:
            if p.sniff_timestamp > timestamp:
                return p

    def _pop_flowtable(self, switch, timestamp):
        for table in self.tmp_flowtable[switch]:
            if table.timestamp > timestamp:
                return table

    def _pop_packet_in(self, switch, timestamp):
        for p in self.tmp_packetinout[switch]:
            if p.message_type == Type.OFPT_PACKET_IN:
                if p.timestamp > timestamp:
                    return p

    def _is_switch(self, switch):
        return self.tracing_net.is_switch(switch)
