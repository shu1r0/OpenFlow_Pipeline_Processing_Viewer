"""
Analyze packet

## パケットの解析について


TODO:
    * check trace is finished before trace is appended to packet_trace_list
    * パケットの解析が途中のものは，もう一度1から解析直したほうが楽
        * つまり，失敗した場合 => tmpリストから削除しない and traceとして保存しない
        * ただし，traceは破棄されるので，どこにその情報を保存するのか？？

    * インターバルの時間設定
    * analyze allの追加

Warnings:
    * PacketTraceに追加するパケットは実際に流れたパケットのオブジェクトでないと行けない
    * trace_listに追加するタイミングを気をつける
    * 送信されたパケットについて，ホストかの判定にmacアドレスを使用していることに注意
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
    def stop_analyzing(self, analyze_rest=True):
        """stop analyzing

        Args:
            analyze_rest(bool): analyze packets that have not been analyzed?
        """
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
        self.tmp_packetinout = {}

    def start_analyzing(self):
        logger.info("start analyzing")
        self.start_time = datetime.datetime.now().timestamp()

        # set interval
        signal.signal(signal.SIGALRM, self.analyze)
        signal.setitimer(signal.ITIMER_REAL, self._interval, self._interval)

    def stop_analyzing(self, analyze_rest=True):
        """stop the analyzing interval"""
        signal.alarm(0)
        if analyze_rest:
            self.analyze_rest()

    def analyze_rest(self):
        self.analyze(analyze_all=True)
        logger.info("These packets could not be analyzed. {}".format(self.tmp_packets))
        logger.info("These OpenFlowMessage could not be analyzed. {}".format(self.tmp_packetinout))

    def analyze(self, Signals=None, FrameType=None, analyze_all=False):
        """

        1. poll from repository
        2. search from packets sent by a host
        3. get next switch and flowtable
        4. execute BFS
        5. loop 2 ~ 4

        Args:
            Signals:
            FrameType:
            analyze_all(bool): analyze all packet?

        Returns:

        """
        # update tmp repository
        if analyze_all:
            self._polling(count=-1, get_all=True)
        else:
            self._polling(self.count)

        # Search from packet out.
        for s, p_io in self.tmp_packetinout.items():
            if p_io:
                for p in p_io:
                    if p.message_type == Type.OFPT_PACKET_OUT:
                        analyzed = self._analyze_packet_out(p, s)
                        if analyzed:
                            self.tmp_packetinout[s].remove(analyzed)

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
                            if flow_table:
                                queue = []
                                self._enqueue(queue, host, p, edge, flow_table, switch_port)

                                trace = self.BFS(queue)
                                if trace.is_finish:
                                    packet_trace_list.append(trace)
                                    self._del_tmp_packet(trace)
                                else:
                                    # todo: 失敗時の処理はこれでいいの？
                                    logger.warning("packet BFS is not finished")
                        else:
                            logger.warning("Packet {} is not from host. "
                                           "The analysis done before may not have been done properly.".format(p))
                else:
                    logger.warning("edge {} is not terminal edge. "
                                   "The analysis done before may not have been done properly.".format(edge))
            else:
                logger.warning("No packet in edge {}".format(edge))

        self.count += 1

    def _analyze_packet_out(self, packet_msg, switch):
        """

        Args:
            packet_msg (MsgForOFMsg) :
            switch (str) :

        Returns:
            成功した場合はそのpacket_msgが帰る．失敗はNone
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
            
            # これが，PacketOutで出力されるパケットのポート(将来的に 置き換える)
            ports_to_edges = self._get_flooding_ports_and_edges(switch, int(packet_msg.of_msg.in_port))
            # logger.debug("ports_to_edges {}".format(ports_to_edges))

            # 次のポートとインターフェース
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

                msg = self._get_packet(edge, packet_msg)
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
                        self._del_tmp_packet(trace)
                        return packet_msg
                    else:
                        # The edge is not terminal edge. Run BFS and complete the trace.
                        # logger.debug("Msg is not in terminal edge. ")
                        queue = []
                        visited_edges = [edge]
                        flow_table = self._get_flowtable(switch, msg.sniff_timestamp)
                        next_table = self._get_flowtable(next_node, msg.sniff_timestamp)
                        if flow_table and next_table:
                            self._enqueue(queue=queue, src_node=flow_table, msg=msg, edge=edge,
                                          next_tables=next_table, next_port=next_port)
                            trace = self.BFS(queue=queue, trace=trace, visited_edges=visited_edges)
                            if trace.is_finish:
                                packet_trace_list.append(trace)
                                self._del_tmp_packet(trace)
                                return packet_msg
                            else:
                                # todo: 失敗時の処理はこれでいいの？
                                logger.warning("packet out BFS is not finished")
                        else:
                            logger.warning("Flowtable wasn't got. "
                                           "At this stage, we need to be able to retrieve the flow table. "
                                           "If the flow table is not available, "
                                           "this process will be skipped and the next packet analysis will be affected.")
                else:
                    logger.warning("cannot pop pakcet next_edge={} m={}".format(edge, packet_msg))
                    # TODO:
                    #   * If there is no matching packet, it is analyzed in the next interval
                    return None

    def BFS(self, queue, trace=None, visited_edges=None):
        """BFS

        * queueのnext_nodeからパケットを幅優先で探索し，経路を特定します．
        * traceを返しますが，成功していな場合trace.is_finishedはFalseです．
        * queueのnext_nodeは予めswitchで有ることを確かめるようにしたほうがよい

        Args:
            queue (list) : queue
            trace (PacketTrace) : packet trace
            visited_edges (list) : visited switch and node list

        Returns:
            PacketTrace : trace

        TODO:
            失敗したときは経路を返さない or Falseを設定する
            引数のtraceとvisited_edgesの廃止
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
                applied_pipeline_result = apply_pipeline(msg, flowtables=dst_node)
                # todo : Floodingなどの処理を追加
                ports_to_msg: list[tuple[str, Msg]] = applied_pipeline_result["port_to_msg"]
                logger.debug("After applied pipeline, out_ports to msg {}".format(ports_to_msg))

                # out_portsから，次に向かうノードを特定する．
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
                            msg = self._get_packet(next_edge, m)
                            if msg:
                                # get flowtable
                                flowtable = self._get_flowtable(next_switch, m.sniff_timestamp)
                                # todo: flowtableがNoneのときの処理
                                if flowtable:
                                    self._enqueue(queue, src_node=dst_node, msg=msg, edge=next_edge,
                                                  next_tables=flowtable, next_port=next_port)
                                    # continue explicitly
                                    continue
                                else:
                                    logger.warning("Getting flow_table is fail. "
                                                   "Although the packets are captured, the flow table is not got."
                                                   "This could be an error")
                            else:
                                logger.debug("cannot pop pakcet next_edge={} m={}".format(next_edge, m))
                                trace.is_finish = False
                                return trace
                        else:
                            logger.warning("already visited edge {}".format(next_edge))
                            # TODO:
                            #   * Terminate the analysis or throw an error
                    else:  # switch or controller or other

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
                            return trace
                        elif self._is_terminal_edge(edge):
                            # next host
                            packet_arc = PacketArc(src=dst_node,
                                                   msg=msg,
                                                   edge=next_edge,
                                                   dst=next_switch,
                                                   dst_interface=next_port)
                            trace.add_arc(copy.deepcopy(packet_arc))
                            trace.is_finish = True
                            return trace
                        else:
                            logger.error("next switch is no matching device ({})".format(next_switch))
                            trace.is_finish = False
                            return trace
            else:  # not switch
                logger.warning("dst {} is not flowtable".format(dst_node))
                # Note: then, the analysis done before may not have been done properly.
                #    * この場合，BFSをする必要がないので，BFSする前に処理しておくべき．
                #    * よって，warningだけ出す
        return trace

    def _update_msg(self, msg, next_port):
        """

        Args:
            msg:
            next_port(str) : (e.g. "h0-eth1")

        Returns:

        Todo:
            * update in_port
        """
        msg.in_phy_port = next_port
        msg.in_port = self.tracing_net.get_ofport_from_interface(next_port.split("-")[0], next_port)

    #
    #  Poller
    #

    def _polling(self, count,  get_all=False):
        """polling packet_repo and packet_inout_repo

        Args:
            count (int) : polling count
        """
        # Packet
        tmp_packets = self._poll_packet_repo(count=count, edges=self.tracing_net.name_to_link.get_edges(), get_all=get_all)
        for e, pkts in tmp_packets.items():
            self.tmp_packets.setdefault(e, [])
            if pkts:
                self.tmp_packets[e].extend(pkts)
                self.tmp_packets[e].sort()

        # Packet Out and Packet In
        tmp_packetinout = self._poll_packet_inout_repo(count=count, switches=self.tracing_net.get_switch_names(), get_all=get_all)
        for s, pkts in tmp_packetinout.items():
            self.tmp_packetinout.setdefault(s, [])
            if pkts:
                self.tmp_packetinout[s].extend(pkts)
                # It's already sorted, but it's sorted just in case.
                self.tmp_packetinout[s].sort()

        logger.debug("polled repository (start_time={}, until={}) values = {} {}"
                     .format(self.start_time, self.count, self.tmp_packets, self.tmp_packetinout))

    def _poll_packet_repo(self, count, edges, get_all=False):
        """

        Args:
            count:
            edges:

        Returns:
            dict[str, list[Msg]]
        """
        packets = {}
        until = get_until_time(self.start_time, self._interval, count)
        if get_all:
            until = None

        for edge in edges:
            interface = self.tracing_net.get_interface_from_link(edge)
            tmp_packets = none2emptylist(self.packet_repo.pop(interface, until=until))
            packets[edge] = tmp_packets
        return packets

    def _poll_packet_inout_repo(self, count, switches, get_all=False):
        """

        Args:
            count (int) : polling count
            switches (list[str]) : polled switches

        Returns:
            dict[str, list[MsgForOFMsg]] : switch to packets
        """
        packet_inouts = {}
        until = get_until_time(self.start_time, self._interval, count)
        if get_all:
            until = None

        for switch in switches:
            # get datapath id
            s_dpid = int(self.tracing_net.get_datapath_id(switch))
            if s_dpid is not None:
                tmp_p = none2emptylist(self.packet_inout_repo.pop(s_dpid, until=until))
                logger.debug("tmp_p = {}, s_dpip = {}".format(tmp_p, s_dpid))

                # Msg to MsgForOFMsg
                packet_inouts[switch] = []
                for p in tmp_p:
                    packet_inouts[switch].append(create_MsgForOFMsg(p))
            else:
                logger.error("Failed to get datapath_id {}".format(switch))
        return packet_inouts

    #
    # get from network or ofcapture
    #

    def _get_topo(self):
        """get nodes and links"""
        topo = self.tracing_net.get_topo()
        return topo

    def _get_next_and_edge(self, interface):
        """get next node, interface, edge name"""
        return self.tracing_net.name_to_link.get_next_and_edge(interface)

    def _get_packet(self, edge, msg):
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
                # todo: 多分 p==msgがおかしい
                if p.sniff_timestamp >= msg.sniff_timestamp:
                    return p

    def _del_tmp_packet(self, packet_trace: PacketTrace):
        for arc in packet_trace.arcs:
            for packets in self.tmp_packets.values():
                if arc.msg in packets:
                    packets.remove(arc.msg)
                else:
                    # packet_in_outなら削除されない
                    # logger.warning("msg didn't remove from tmp_packets")
                    pass

    def _get_flowtable(self, switch, timestamp):
        """

        Args:
            switch:
            timestamp:

        Returns:
            list or None : 取得できていない場合はNone
        """
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


def none2emptylist(obj):
    if isinstance(obj, list):
        return obj
    elif obj is None:
        return []
    else:
        return []


def get_until_time(start_time, interval, count):
    delay = 1
    return start_time + interval*count - delay

