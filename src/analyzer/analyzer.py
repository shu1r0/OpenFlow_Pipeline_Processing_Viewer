from abc import ABCMeta, abstractmethod
import datetime
import copy
# unix
import signal
import time
from logging import getLogger, setLoggerClass, Logger

from pyof.foundation.basic_types import UBInt32
from pyof.v0x04.common.header import Type
from pyof.v0x04.common.port import PortNo

from src.ofcapture.ofcapture import OFCaptureBase
from src.tracing_net.net.net import TracingNet
from src.tracing_net.packet.packet_repository import PacketRepository
from src.tracing_net.flowtable.table_repository import TableRepository
from src.tracing_net.ofproto.table import FlowTables
from src.tracing_net.ofproto.msg import Msg
from src.ofcapture.capture.of_msg_repository import PacketInOutRepository
from src.ofproto.pipeline import apply_pipeline
from src.analyzer.packet_trace import PacketArc, PacketTrace
from src.analyzer.trace_repository import packet_trace_repository


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
            of_capture (OFCaptureBase) :
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
        """analyzing trace"""
        raise NotImplementedError

    @abstractmethod
    def start_analyzing(self, call_back=None):
        """start analyzing

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
        self._interval = 2
        self.start_time = None
        self.count = 0
        # tmp repo
        self.tmp_packets = {}
        self.tmp_flowtable = {}
        self.tmp_packetinout = {}

        self.on_the_way_trace = []

    def start_analyzing(self, call_back=None):
        self.start_time = datetime.datetime.now().timestamp()

        # set interval
        signal.signal(signal.SIGALRM, self.analyze)
        signal.setitimer(signal.ITIMER_REAL, self._interval, self._interval)

    def analyze(self, *args):
        # update tmp repository
        self._polling(self.count)

        # get packet out
        for s, p_io in self.tmp_packetinout.items():
            if p_io:
                for p in p_io:
                    if p.message_type == Type.OFPT_PACKET_OUT:

                        # TODO: move to a method handling packet out
                        logger.debug("I will processing packetout({})".format(p))
                        if isinstance(p.of_msg.actions[0].port, UBInt32):
                            if int(p.of_msg.actions[0].port) in list(PortNo):
                                p.of_msg.actions[0].port = PortNo(int(p.of_msg.actions[0].port))
                            else:
                                logger.warning("not flooding packet out")
                        if p.of_msg.actions[0].port == PortNo.OFPP_FLOOD:
                            logger.debug("packet out's in_port {}".format(p.of_msg.in_port))
                            queue = []
                            ports_to_edges = self._get_flooding_ports_and_edges(s, int(p.of_msg.in_port))
                            # logger.debug("ports_to_edges {}".format(ports_to_edges))
                            for intf, next_and_edge in ports_to_edges.items():
                                # packet traces
                                trace = PacketTrace()
                                packet_arc = PacketArc(src="controller",
                                                       msg=p,
                                                       edge=None,
                                                       dst=s,
                                                       dst_interface="")
                                trace.add_arc(packet_arc)

                                next_node, next_port, edge = next_and_edge
                                msg = self._pop_packet(edge, p.timestamp)
                                if msg:
                                    self._update_msg(msg, next_port=next_port)
                                    if self._is_terminal_edge(edge):
                                        packet_arc = PacketArc(src=s,
                                                               msg=msg,
                                                               edge=edge,
                                                               dst=next_node,
                                                               dst_interface=next_port)
                                        trace.add_arc(packet_arc)
                                    else:
                                        pass
                                else:
                                    logger.warning("msg not found")
                                packet_trace_repository.add(trace)
                        # self._update_msg(msg, next_port=next_port)
                        # self._enqueue(queue, src_node, msg, first_edge, next_tables, next_port)

        # packet
        for edge, pkts in self.tmp_packets.items():
            intf = self.tracing_net.get_interface_from_link(edge)

            if pkts:
                for p in pkts:
                    get_next_and_edge = self._get_next_and_edge(intf)
                    if get_next_and_edge:
                        _, _, edge = get_next_and_edge
                        if self._is_terminal_edge(edge):
                            host, switch, switch_port = self.tracing_net.get_terminal_edge(edge)
                            logger.debug("terminal edge host={}, switch={}, switch_port={}".format(host, switch, switch_port))

                            self._update_msg(p, next_port=switch_port)
                            flow_table = self._get_flowtable(switch, p.sniff_timestamp)

                            queue = []
                            self._enqueue(queue, host, p, edge, flow_table, switch_port)

                            trace = self.BFS(queue)
                            packet_trace_repository.add(trace)
                        else:
                            logger.warning("Packet {} is not terminal edge".format(p))
                    else:
                        logger.warning("Failed to get ({})'s next switch, port and edge ".format(intf))
            else:
                logger.warning("Fuck!!!!!!!! {}".format(intf))

        self.count += 1

    def BFS(self, queue):
        """BFS"""
        # packet traces
        trace = PacketTrace()
        # visited edges
        visited = []

        # BFS loop
        while queue:
            # get processing data from queue
            # init packet arc
            src_node, msg, edge, dst_node, dst_port = queue.pop(0)

            logger.debug("processing msg {}".format(msg))
            visited.append(edge)

            # Packet Arc
            packet_arc = PacketArc(src=src_node, msg=msg)
            msg: Msg = msg
            # update arc
            packet_arc.edge = edge
            packet_arc.dst = dst_node
            packet_arc.dst_interface = dst_port

            trace.add_arc(copy.deepcopy(packet_arc))
            # trace.add_arc(packet_arc)

            # next node is Switch
            if isinstance(dst_node, FlowTables):
                # next ports
                ports_to_msg: list[tuple[str, Msg]] = apply_pipeline(msg, flowtables=dst_node)
                logger.debug("After applyed pipeline, out_ports to msg {}".format(ports_to_msg))

                # next nodes
                for p, m in ports_to_msg:
                    # next switch, port, edge
                    next_switch, next_port, next_edge = None, None, None
                    # convert interface
                    p = self._ofport_to_interface(dst_node.switch_name, p)
                    if not self._is_controller(p):
                        next_switch, next_port, next_edge = self._get_next_and_edge(p)
                    else:  # TODO controller
                        next_switch = "controller"

                    # set next switch and port
                    if isinstance(next_switch, str) and self._is_switch(next_switch):  # switch
                        self._update_msg(msg, next_port=next_port)
                        if next_edge not in visited:  # loop?
                            # get packet
                            msg = self._pop_packet(next_edge, m.sniff_timestamp)
                            # get flowtable
                            flowtable = self._get_flowtable(next_switch, m.sniff_timestamp)
                            self._enqueue(queue, src_node=dst_node, msg=msg, first_edge=next_edge, next_tables=flowtable, next_port=next_port)
                        else:
                            logger.warning("already visited edge {}".format(next_edge))
                    else:  # not switch
                        # set finish
                        if next_switch == "controller":  # TODO: controller
                            logger.debug("to controller message")
                            packet_arc = PacketArc(src=dst_node,
                                                   msg=msg,
                                                   edge=next_edge,
                                                   dst="controller",
                                                   dst_interface="")
                            trace.add_arc(copy.deepcopy(packet_arc))
                        elif self._is_terminal_edge(edge):
                            # next host
                            packet_arc = PacketArc(src=dst_node,
                                                   msg=msg,
                                                   edge=next_edge,
                                                   dst=next_switch,
                                                   dst_interface=next_port)
                            trace.add_arc(copy.deepcopy(packet_arc))
                        else:
                            logger.warning("next switch is no matching device ({})".format(next_switch))
            else:  # not switch
                logger.debug("dst {} is not flowtable".format(dst_node))
        return trace

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
        msg.in_port = self.tracing_net.get_ofport_from_interface(next_port.split("-")[0], next_port)

    # def start_polling(self):
    #     pass

    def _polling(self, count):
        # logger.debug("{}, {}".format(self.tracing_net.name_to_link.get_edges(), self.tracing_net.get_switch_names()))
        tmp_packets = self._poll_packet_repo(count=count, edges=self.tracing_net.name_to_link.get_edges())
        for e, pkts in tmp_packets.items():
            self.tmp_packets.setdefault(e, [])
            if pkts:
                self.tmp_packets[e].extend(pkts)
        # self.tmp_flowtable = self._poll_table_repo(count=count, switches=self.tracing_net.get_switch_names())
        tmp_packetinout = self._poll_packet_inout_repo(count=count, switches=self.tracing_net.get_switch_names())
        for s, pkts in tmp_packetinout.items():
            self.tmp_packetinout.setdefault(s, [])
            # logger.debug("s={}, pkts={}".format(s, pkts))
            if pkts:
                self.tmp_packetinout[s].extend(pkts)
        logger.debug("polled (start_time={}, until={}) values = {} {} {}"
                     .format(self.start_time, self.count, self.tmp_packets, self.tmp_flowtable, self.tmp_packetinout))

    def _poll_packet_repo(self, count, edges):
        packets = {}
        until = self.start_time + self._interval * count
        for edge in edges:
            interface = self.tracing_net.name_to_link.get_int_name_pairs(edge)[0]
            tmp_packets = self.packet_repo.pop(interface, until=until)
            packets[edge] = tmp_packets
        return packets

    # def _poll_table_repo(self, count, switches):
    #     tables = {}
    #     until = self.start_time + self._interval * count
    #     for switch in switches:
    #         tmp_table = self.table_repo.pop(switch=switch, until=until)
    #         tables[switch] = tmp_table
    #     return tables

    def _poll_packet_inout_repo(self, count, switches):
        packet_inouts = {}
        until = self.start_time + self._interval * count
        for switch in switches:
            s_dpid = int(self.tracing_net.get_datapath_id(switch))
            if s_dpid:
                tmp_p = self.packet_inout_repo.pop(s_dpid, until=until)
                logger.debug("tmp_p = {}, s_dpip = {}".format(tmp_p, s_dpid))
                packet_inouts[switch] = tmp_p
            else:
                logger.error("Failed to get datapath_id {}".format(switch))
        return packet_inouts

    def _get_topo(self):
        topo = self.tracing_net.get_topo()
        return topo

    # def get_port(self, switch):
    #     datapath_id = self.tracing_net.get_datapath_id(switch)
    #     return self.of_capture.capture.get_port(datapath_id)

    def _get_next_and_edge(self, interface):
        return self.tracing_net.name_to_link.get_next_and_edge(interface)

    def _pop_packet(self, edge, timestamp, msg=None):
        """

        Args:
            edge (str) :
            timestamp (float) :
            msg (Msg) :

        Returns:

        Notes:
            * to implement a check for match
        """
        if self.tmp_packets[edge]:
            for p in self.tmp_packets[edge]:
                if p.sniff_timestamp >= timestamp:
                    return p

    # def _pop_flowtable(self, switch, timestamp):
    #     if self.tmp_flowtable[switch]:
    #         for table in self.tmp_flowtable[switch]:
    #             if table.timestamp > timestamp:
    #                 return table

    def _get_flowtable(self, switch, timestamp):
        return self.table_repo.get(switch, timestamp)

    def _pop_packet_in(self, switch, timestamp):
        if self.tmp_packetinout[switch]:
            for p in self.tmp_packetinout[switch]:
                if p.message_type == Type.OFPT_PACKET_IN:
                    if p.timestamp > timestamp:
                        return p

    def _is_switch(self, switch):
        return self.tracing_net.is_switch(switch)

    def _is_controller(self, port: str):
        if isinstance(port, str) and port.isdigit():
            port = int(port)
        if isinstance(port, int) and port > 1000:
            return True
        return False

    def _is_terminal_edge(self, edge):
        return self.tracing_net.is_terminal_edge(edge)

    def _enqueue(self, queue, src_node, msg, first_edge, next_tables, next_port):
        queue.append((src_node, msg, first_edge, next_tables, next_port))

    def _ofport_to_interface(self, switch, ofport):
        if isinstance(ofport, str) and ofport.isdigit():
            ofport = int(ofport)
        if isinstance(ofport, int) and ofport < 1000:
            return self.tracing_net.get_interface_from_ofport(switch, ofport)
        return ofport

    def _get_flooding_ports_and_edges(self, switch, of_port):
        """

        Args:
            switch:
            of_port:

        Returns:
            dict[str, (str, str, str)]
        """
        pe = {}
        for intf, port in self.tracing_net.get(switch).ports.items():
            if port != of_port:
                if intf.name != 'lo':
                    pe[intf.name] = self._get_next_and_edge(intf.name)
        return pe
