"""
Analyze packet


TODO:
    * check trace is finished before trace is appended to packet_trace_list
    * パケットinoutをカプセル化する
"""

from abc import ABCMeta, abstractmethod
import datetime
import copy
# only unix
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
from src.ofproto.msg import create_MsgForOFMsg, MsgForOFMsg
from src.analyzer.packet_trace import PacketArc, PacketTrace
from src.analyzer.packet_trace_handler import packet_trace_list


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
    def start_analyzing(self):
        """start analyzing"""
        raise NotImplementedError

    @abstractmethod
    def stop_analyzing(self):
        """stop analyzing"""
        raise NotImplementedError


class Analyzer(AbstractAnalyzer):
    """
    This computes the path of a packet.
    """

    def __init__(self, tracing_net, of_capture, packet_repo, table_repo, packet_inout_repo):
        super(Analyzer, self).__init__(tracing_net, of_capture, packet_repo, table_repo, packet_inout_repo)
        # analyzing interval
        self._interval = 2
        self.start_time = None
        self.count = 0
        # tmp repo
        self.tmp_packets = {}
        self.tmp_flowtable = {}
        self.tmp_packetinout = {}

        self.on_the_way_trace = []

    def start_analyzing(self):
        self.start_time = datetime.datetime.now().timestamp()

        # set interval
        signal.signal(signal.SIGALRM, self.analyze)
        signal.setitimer(signal.ITIMER_REAL, self._interval, self._interval)

    def stop_analyzing(self):
        """stop the analyzing interval"""
        signal.alarm(0)

    def analyze(self, *args):
        # update tmp repository
        self._polling(self.count)

        # Search from packet out.
        for s, p_io in self.tmp_packetinout.items():
            if p_io:
                for p in p_io:
                    if p.message_type == Type.OFPT_PACKET_OUT:
                        self._analyze_packet_out(p, s)

        # Search from packets sent by a host
        for edge, pkts in self.tmp_packets.items():
            if pkts:  # Do the packets exist?
                if self._is_terminal_edge(edge):
                    host, switch, switch_port = self.tracing_net.get_terminal_edge(edge)

                    for p in pkts:
                        if p.eth_src in self._get_hosts_mac():  # Is the packet from the host?
                            # set next port
                            self._update_msg(p, next_port=switch_port)
                            flow_table = self._get_flowtable(switch, p.sniff_timestamp)

                            queue = []
                            self._enqueue(queue, host, p, edge, flow_table, switch_port)

                            trace = self.BFS(queue)
                            packet_trace_list.append(trace)
                        else:
                            logger.warning("Packet {} is not from host. The analysis done before may not have been done properly.".format(p))
                else:
                    logger.warning("edge {} is not terminal edge. The analysis done before may not have been done properly.".format(edge))
            else:
                logger.warning("No packet in edge {}".format(edge))

        self.count += 1

    def _analyze_packet_out(self, packet_msg, switch):
        """

        Args:
            packet_msg (MsgForOFMsg) :
            switch (str) :
        """
        logger.debug("I will processing packetout({})".format(packet_msg))

        # port convert
        if isinstance(packet_msg.of_msg.actions[0].port, UBInt32):
            # port is specific port? (e.g. OFPP_FLOOD)
            tmp_port = int(packet_msg.of_msg.actions[0].port)
            if tmp_port in list(PortNo):
                packet_msg.of_msg.actions[0].port = PortNo(tmp_port)
            else:
                packet_msg.of_msg.actions[0].port = tmp_port

        # packet analyze
        # todo: packet_msg.of_msg.actions[0].port ==> instruction_result outport
        if packet_msg.of_msg.actions[0].port == PortNo.OFPP_FLOOD:
            logger.debug("packet out's in_port {}".format(packet_msg.of_msg.in_port))

            ports_to_edges = self._get_flooding_ports_and_edges(switch, int(packet_msg.of_msg.in_port))
            # logger.debug("ports_to_edges {}".format(ports_to_edges))

            for intf, next_and_edge in ports_to_edges.items():
                # packet traces
                trace = PacketTrace()
                packet_arc = PacketArc(src="controller",
                                       msg=packet_msg,
                                       edge=None,
                                       dst=switch,
                                       dst_interface="")
                trace.add_arc(packet_arc)

                # get next and OFMsg obj
                next_node, next_port, edge = next_and_edge
                net_msg = create_MsgForOFMsg(packet_msg)

                msg = self._pop_packet(edge, net_msg)
                if msg:
                    self._update_msg(msg, next_port=next_port)

                    if self._is_terminal_edge(edge):
                        packet_arc = PacketArc(src=switch,
                                               msg=msg,
                                               edge=edge,
                                               dst=next_node,
                                               dst_interface=next_port)
                        trace.add_arc(packet_arc)
                        trace.is_finish = True
                        packet_trace_list.append(trace)
                    else:
                        # The edge is not terminal edge. Run BFS and complete the trace.
                        # logger.debug("Msg is not in terminal edge. ")
                        queue = []
                        visited_edges = [edge]
                        flow_table = self._get_flowtable(switch, msg.sniff_timestamp)
                        self._enqueue(queue=queue, src_node=flow_table, msg=msg, edge=edge,
                                      next_tables=next_node, next_port=next_port)
                        trace = self.BFS(queue=queue, trace=trace, visited_edges=visited_edges)
                        packet_trace_list.append(trace)
                else:
                    logger.warning("cannot pop pakcet next_edge={} m={}".format(edge, net_msg))
                    # TODO:
                    #   * If there is no matching packet, it is analyzed in the next interval

    def BFS(self, queue, trace=None, visited_edges=None):
        """BFS

        Args:
            queue (list) : queue
            trace (PacketTrace) : packet trace
            visited_edges (list) : visited switch and node list

        Returns:
            PacketTrace : trace
        """
        # packet traces
        if trace is None:
            trace = PacketTrace()
        # visited edges (However, the controller is not included.)
        if visited_edges is None:
            visited_edges = []

        # BFS loop
        while queue:
            # get processing data from queue
            src_node, msg, edge, dst_node, dst_port = queue.pop(0)

            logger.debug("processing msg {}".format(msg))
            visited_edges.append(edge)

            # Packet Arc
            packet_arc = PacketArc(src=src_node, msg=msg, edge=edge, dst=dst_node, dst_interface=dst_port)
            msg: Msg = msg
            trace.add_arc(copy.deepcopy(packet_arc))
            # trace.add_arc(packet_arc)

            # next node is Switch
            if isinstance(dst_node, FlowTables):
                # Perform OpenFlow processing and get the port for the next packet
                ports_to_msg: list[tuple[str, Msg]] = apply_pipeline(msg, flowtables=dst_node)
                logger.debug("After applyed pipeline, out_ports to msg {}".format(ports_to_msg))

                # next nodes
                for p, m in ports_to_msg:
                    # next switch, port, edge
                    next_switch, next_port, next_edge = None, None, None
                    # convert interface
                    p = self._ofport_to_interface(dst_node.switch_name, p)

                    # get where packet is going next.
                    if not self._is_controller(p):
                        next_switch, next_port, next_edge = self._get_next_and_edge(p)
                    else:
                        #@Note:
                        # This will eventually be an enumerate
                        next_switch = "controller"

                    # set next switch and port
                    # If the next node is a switch, it computes the OpenFlow processing and add it to the queue.
                    if isinstance(next_switch, str) and self._is_switch(next_switch):  # switch
                        self._update_msg(msg, next_port=next_port)

                        if next_edge not in visited_edges:  # loop?
                            # get packet
                            msg = self._pop_packet(next_edge, m)
                            if msg:
                                # get flowtable
                                flowtable = self._get_flowtable(next_switch, m.sniff_timestamp)
                                self._enqueue(queue, src_node=dst_node, msg=msg, edge=next_edge,
                                              next_tables=flowtable, next_port=next_port)
                            else:
                                logger.warning("cannot pop pakcet next_edge={} m={}".format(next_edge, m))
                                # TODO:
                                #   * If there is no matching packet, it is analyzed in the next interval
                                #    そのためにはもう一度enqueueする必要があることに注意
                                # self.on_the_way_trace.append((msg, trace, queue, visited))
                        else:
                            logger.warning("already visited edge {}".format(next_edge))
                            # TODO:
                            #   * Terminate the analysis or throw an error
                    else:
                        # If next node is not switch, it is considered as an endpoint adn add to PacketTrace.
                        if next_switch == "controller":
                            # TODO: get packet in
                            #   まだ，packet_inメッセージがカプセル化されていないのでそこを考える
                            packet_arc = PacketArc(src=dst_node,
                                                   msg=msg,
                                                   edge=next_edge,
                                                   dst="controller",
                                                   dst_interface="")
                            trace.add_arc(copy.deepcopy(packet_arc))
                            trace.is_finish = True
                        elif self._is_terminal_edge(edge):
                            # next host
                            packet_arc = PacketArc(src=dst_node,
                                                   msg=msg,
                                                   edge=next_edge,
                                                   dst=next_switch,
                                                   dst_interface=next_port)
                            trace.add_arc(copy.deepcopy(packet_arc))
                            trace.is_finish = True
                        else:
                            logger.warning("next switch is no matching device ({})".format(next_switch))
            else:  # not switch
                logger.warning("dst {} is not flowtable".format(dst_node))
                # Note: then, the analysis done before may not have been done properly.
        return trace

    def _update_msg(self, msg, next_port):
        """

        Args:
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
        """polling packet_repo and packet_inout_repo

        Args:
            count (int) : polling count
        """
        # Packet
        tmp_packets = self._poll_packet_repo(count=count, edges=self.tracing_net.name_to_link.get_edges())
        for e, pkts in tmp_packets.items():
            self.tmp_packets.setdefault(e, [])
            if pkts:
                self.tmp_packets[e].extend(pkts)

        # Packet Out and Packet In
        tmp_packetinout = self._poll_packet_inout_repo(count=count, switches=self.tracing_net.get_switch_names())
        for s, pkts in tmp_packetinout.items():
            self.tmp_packetinout.setdefault(s, [])
            # logger.debug("s={}, pkts={}".format(s, pkts))
            if pkts:
                self.tmp_packetinout[s].extend(pkts)

        logger.debug("polled repository (start_time={}, until={}) values = {} {} {}"
                     .format(self.start_time, self.count, self.tmp_packets, self.tmp_flowtable, self.tmp_packetinout))

    def _poll_packet_repo(self, count, edges):
        packets = {}
        until = self.start_time + self._interval * count
        for edge in edges:
            interface = self.tracing_net.get_interface_from_link(edge)
            tmp_packets = self.packet_repo.pop(interface, until=until)
            packets[edge] = tmp_packets
        return packets

    def _poll_packet_inout_repo(self, count, switches):
        """

        Args:
            count:
            switches:

        Returns:
            dict

        TODO:
            * オブジェクトを変換しておく
        """
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
        """get nodes and links"""
        topo = self.tracing_net.get_topo()
        return topo

    def _get_next_and_edge(self, interface):
        """get next node, interface, edge name"""
        return self.tracing_net.name_to_link.get_next_and_edge(interface)

    def _pop_packet(self, edge, msg):
        """Get the same packet as the msg.
        The msg attributes and timestamp are used to determine if it is the same packet.

        Args:
            edge (str) :
            msg (Msg) :

        Returns:
            Msg : same packet as the msg
        """
        if self.tmp_packets[edge]:
            for p in self.tmp_packets[edge]:
                if p.sniff_timestamp >= msg.sniff_timestamp and p == msg:
                    return p

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
        """Is the port connected controller?"""
        if isinstance(port, str) and port.isdigit():
            port = int(port)
        if isinstance(port, int) and port > 1000:
            return True
        return False

    def _is_terminal_edge(self, edge):
        return self.tracing_net.is_terminal_edge(edge)

    def _enqueue(self, queue, src_node, msg, edge, next_tables, next_port):
        """append to queue

        Args:
            queue: target queue
            src_node (FlowTables or str) :
            msg (Msg) :
            edge (str) : edge name
            next_tables (FlowTables or str) :
            next_port (str) : port name (e.g. h2-eth1)
        """
        queue.append((src_node, msg, edge, next_tables, next_port))

    def _ofport_to_interface(self, switch, ofport):
        """ofport to interface

        Args:
            switch (str) : switch name
            ofport (int or str) : of port number

        Returns:
            str : interface (e.g. "s1-eth0")
        """
        if isinstance(ofport, str) and ofport.isdigit():
            ofport = int(ofport)

        if isinstance(ofport, int) and ofport < 1000:
            return self.tracing_net.get_interface_from_ofport(switch, ofport)
        return ofport

    def _get_hosts_mac(self):
        hosts = self.tracing_net.hosts
        mac_addresses = [host.MAC() for host in hosts]
        return mac_addresses

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
