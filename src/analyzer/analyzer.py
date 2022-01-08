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
    * applyed pipelineの前にUpdate MSGができているかを確認する
"""

from abc import ABCMeta, abstractmethod
import datetime
import copy

# only unix
import signal
from logging import getLogger, setLoggerClass, Logger

from pyof.v0x04.common.header import Type
from pyof.v0x04.common.port import PortNo

from src.ofcapture.ofcapture import OFCaptureBase
from src.tracing_net.net.net import TracingNet
from src.tracing_net.packet.packet_repository import PacketRepository
from src.tracing_net.flowtable.table_repository import TableRepository
from src.tracing_net.ofproto.table import FlowTables
from src.tracing_net.ofproto.msg import Msg
from src.ofcapture.capture.of_msg_repository import PacketInOutRepository
from src.analyzer.ofproto.pipeline import apply_pipeline, apply_pipeline_for_packetout
from src.analyzer.ofproto.msg import create_MsgForOFMsg
from src.analyzer.packet_trace import PacketArc, PacketTrace
from src.analyzer.packet_trace_handler import packet_trace_list
from src.config import conf


setLoggerClass(Logger)
logger = getLogger('tracing_of_pipeline.analyzer')


DELAY = 1  # [s]


class BFSQueue:
    """queue for BFS"""

    def __init__(self):
        self._queue = []

    def enqueue(self, src_node, msg, edge, next_tables, next_port, packet_processing=None):
        """append to queue

        Args:
            src_node (FlowTables or str) :
            msg (Msg) :
            edge (str) : edge name
            next_tables (FlowTables or str) :
            next_port (str) : port name (e.g. h2-eth1)
        """
        self._queue.append((src_node, msg, edge, next_tables, next_port, packet_processing))

    def dequeue(self):
        """dequeue"""
        return self._queue.pop(0)

    def is_empty(self):
        """Is this queue empty?"""
        return len(self._queue) == 0


class AbstractAnalyzer(metaclass=ABCMeta):
    """This integrates information and computes packet trace.

    Attributes:
        tracing_net (TracingNet) : Mininet
        of_capture (OFCaptureBase) : Proxy
        packet_repo (PacketRepository) : Packet repository
        table_repo (TableRepository) : Flow Table repository
        packet_inout_repo (PacketInOutRepository) : Packet In/Out repository
    """

    def __init__(self, tracing_net, of_capture, packet_repo, table_repo, packet_inout_repo):
        """Init

        Args:
            tracing_net (TracingNet) : Mininet
            of_capture (OFCaptureBase) : Proxy
            packet_repo (PacketRepository) : Packet repository
            table_repo (TableRepository) : Flow Table repository
            packet_inout_repo (PacketInOutRepository) : Packet In/Out repository
        """
        self.tracing_net = tracing_net
        self.of_capture = of_capture
        self.packet_repo = packet_repo
        self.table_repo = table_repo
        self.packet_inout_repo = packet_inout_repo

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

        self.start_time = 0
        self.count = 0

        # tmp repo
        self.tmp_packets = {}
        self.tmp_packetinout = {}

    def start_analyzing(self):
        self.start_time = datetime.datetime.now().timestamp()
        logger.info("start analyzing interval (start_time = {}, interval = {})".format(self.start_time, self._interval))

        # set interval
        signal.signal(signal.SIGALRM, self.analyze)
        signal.setitimer(signal.ITIMER_REAL, self._interval, self._interval)

    def stop_analyzing(self, analyze_rest=True):
        """stop the analyzing interval"""
        logger.info("stop analyzing interval. (last count = {})".format(self.count))
        signal.alarm(0)
        if analyze_rest:
            self.analyze_rest()

    def analyze_rest(self, clear=True):
        """This analyzes the rest of the packets.

         * This function assumes that the remaining packets will be analyzed at the end of the system
             and all packets will be analyzed at once.
        """
        self.analyze(analyze_all=True)
        logger.info("These packets could not be analyzed. {}".format(self.tmp_packets))
        logger.info("These OpenFlowMessage could not be analyzed. {}".format(self.tmp_packetinout))
        if clear:
            self.tmp_packets.clear()
            self.tmp_packetinout.clear()

    def analyze(self, Signals=None, FrameType=None, analyze_all=False):
        """

        Analyzing...
        1. poll from repository
        2. analyze packet out
        3. analyze packet
            1. get flow table
            2. run BFS
        2. search from packets sent by a host
        3. get next switch and flowtable
        4. execute BFS
        5. loop 2 ~ 4

        Args:
            Signals:
            FrameType:
            analyze_all(bool): analyze all packet?

        Notes:
            * The starting point of the search is determined by this function.
        """
        # update tmp repository
        if analyze_all:
            self._polling(count=-1, get_all=True)  # poll all
        else:
            self._polling(self.count)

        if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
            logger.debug("Analyzing 1... polled repository (count={})".format(self.count))

        # Search from packet out.
        for s, p_io in self.tmp_packetinout.items():
            if p_io:
                for p in p_io:
                    if p.message_type == Type.OFPT_PACKET_OUT:
                        if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                            logger.debug("Analyzing 2... analyze packet out (count={}, target={})".format(self.count, p))
                        analyzed = self._analyze_packet_out(p, s)
                        if analyzed:
                            self.tmp_packetinout[s].remove(analyzed)

        # Search from packets sent by a host
        for edge, pkts in self.tmp_packets.items():
            if pkts:  # Do the packets exist?
                if self._is_terminal_edge(edge):
                    host, switch, switch_port = self.tracing_net.get_terminal_edge(edge)

                    for p in pkts:
                        if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                            logger.debug("Analyzing 3... analyze packet (count={}, target={})".format(self.count, p))

                        # compare Mac address
                        if p.eth_src == self.tracing_net.get(host).MAC():  # Is the packet from the host?
                            # set next port
                            self._update_msg(p, next_port=switch_port)
                            flow_table = self._get_flowtable(switch, p.sniff_timestamp)
                            if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                logger.debug("Analyzing 3.1... get flowtable (count={}, flow table={})".format(self.count, flow_table))

                            if flow_table:
                                queue = BFSQueue()
                                queue.enqueue(host, p, edge, flow_table, switch_port)

                                trace = self.BFS(queue)
                                if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                    logger.debug("Analyzing 5.1... After BFS (count={}, trace={})".format(self.count, trace))

                                if trace.is_finish:
                                    packet_trace_list.append(trace)
                                    self._del_tmp_packet(trace)
                                    if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                        logger.debug("Analyzing 5.2... Trace is finish. (count={}, trace={})".format(self.count, trace))
                                else:
                                    # todo: 失敗時の処理はこれでいいの？
                                    if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                        logger.debug("Analyzing 5.2... trace is not finished (count={}, trace={})".format(self.count, trace))
                        else:
                            logger.warning("Packet {} is not from host. "
                                           "The analysis done before may not have been done properly. "
                                           "(host_mac={}, packet_ethsrc={})".format(p, self.tracing_net.get(host).MAC(), p.eth_src))
                else:
                    logger.warning("edge {} is not terminal edge. "
                                   "The analysis done before may not have been done properly.".format(edge))
            else:
                if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                    logger.debug("Analyzing 1... No packet in edge {}".format(edge))

        self.count += 1

    def _analyze_packet_out(self, packet_msg, switch):
        """

        Args:
            packet_msg (MsgForOFMsg) :
            switch (str) :

        Returns:
            成功した場合はそのpacket_msgが帰る．失敗はNone
        """
        # apply action
        applied_result = apply_pipeline_for_packetout(packet_msg)
        out_ports = applied_result["port_to_msg"]
        if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
            logger.debug("Analyzing 2.1... analyze packet out, get out_ports (count={}, out_ports={})"
                         .format(self.count, out_ports))

        next_and_edges = []

        # todo:  for文で実装 or FLOODなどを変換する仕組みの実装
        if out_ports[0][0] == PortNo.OFPP_FLOOD:
            packet_msg = out_ports[0][1]
            if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                logger.debug("Analyzing 2.2... get packer msg (count={}, packer msg={})"
                             .format(self.count, out_ports))

            ports_to_edges = self._get_flooding_ports_and_edges(switch, int(packet_msg.of_msg.in_port))
            # logger.debug("ports_to_edges {}".format(ports_to_edges))
            next_and_edges = ports_to_edges.values()
        else:
            for p, m in out_ports:
                next_and_edges.append(self._get_next_and_edge(self._ofport_to_interface(switch, p)))

        # 次のポートとインターフェース
        for next_and_edge in next_and_edges:
            # packet traces
            trace = PacketTrace()
            packet_arc = PacketArc(src="controller",
                                   msg=packet_msg,  # action に setfieldがない場合
                                   edge=None,
                                   dst=switch,
                                   dst_interface="")
            trace.add_arc(packet_arc)

            # get next and OFMsg obj
            next_node, next_port, edge = next_and_edge

            msg = self._get_packet(edge, packet_msg)

            if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                logger.debug("Analyzing 2.3... get packet (count={}, edge={}, packet={})"
                             .format(self.count, edge, msg))
            if msg:
                self._update_msg(msg, next_port=next_port)

                if self._is_terminal_edge(edge):
                    packet_arc = PacketArc(src=switch,
                                           msg=msg,
                                           edge=edge,
                                           dst=next_node,
                                           dst_interface=next_port)
                    if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                        logger.debug("Analyzing 2.4... next_node is host. the trace is finish (count={}, next node={})"
                                     .format(self.count, next_node))
                    trace.add_arc(packet_arc)
                    trace.is_finish = True
                    packet_trace_list.append(trace)
                    self._del_tmp_packet(trace)
                    return packet_msg
                else:
                    # The edge is not terminal edge. Run BFS and complete the trace.
                    # logger.debug("Msg is not in terminal edge. ")
                    queue = BFSQueue()
                    visited_edges = [edge]
                    flow_table = self._get_flowtable(switch, msg.sniff_timestamp)
                    next_table = self._get_flowtable(next_node, msg.sniff_timestamp)
                    if flow_table and next_table:
                        queue.enqueue(src_node=flow_table, msg=msg, edge=edge,
                                      next_tables=next_table, next_port=next_port)
                        if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                            logger.debug("Analyzing 2.4... next_node is switch. run BFS (count={}, next node={})"
                                         .format(self.count, next_node))
                        trace = self.BFS(queue=queue, trace=trace, visited_edges=visited_edges)
                        if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                            logger.debug("Analyzing 2.5... After BFS (count={}, trace={})"
                                         .format(self.count, next_node))
                        if trace.is_finish:
                            if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                logger.debug("Analyzing 2.5... After BFS, trace is finish (count={}, trace={})"
                                             .format(self.count, next_node))
                            packet_trace_list.append(trace)
                            self._del_tmp_packet(trace)
                            return packet_msg
                        else:
                            # todo: 失敗時の処理はこれでいいの？
                            if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                logger.warning("Analyzing 2.4... packet out BFS is not finished (count={})".format(self.count))
                    else:
                        logger.warning("Flowtable wasn't got. "
                                       "At this stage, we need to be able to retrieve the flow table. "
                                       "If the flow table is not available, "
                                       "this process will be skipped and the next packet analysis will be affected.")
            else:
                if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                    logger.warning("Analyzing 2.3... cannot pop pakcet (count={} next_edge={} m={})".format(self.count, edge, packet_msg))
                # TODO:
                #   * If there is no matching packet, it is analyzed in the next interval
                return None
        if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
            logger.warning("Analyzing 2.3... no flooding ports")


    def BFS(self, queue, trace=None, visited_edges=None):
        """BFS

        * queueのnext_nodeからパケットを幅優先で探索し，経路を特定します．
        * traceを返しますが，成功していな場合trace.is_finishedはFalseです．
        * queueのnext_nodeは予めswitchで有ることを確かめるようにしたほうがよい

        Args:
            queue (BFSQueue) : queue
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

        if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
            logger.debug("Analyzing 4... start BFS (count={})".format(self.count))

        # BFS loop
        while not queue.is_empty():
            # get processing data from queue
            src_node, msg, edge, dst_node, dst_port, pp = queue.dequeue()
            if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                logger.debug("Analyzing 4.1... processing msg (count={}, msg={})".format(self.count, msg))
            visited_edges.append(edge)

            # Packet Arc
            packet_arc = PacketArc(src=src_node, msg=msg, edge=edge, dst=dst_node, dst_interface=dst_port)
            packet_arc.packet_processing = pp
            msg: Msg = msg
            trace.add_arc(copy.deepcopy(packet_arc))
            # trace.add_arc(packet_arc)

            # next node is Switch
            if isinstance(dst_node, FlowTables):
                if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                    logger.debug("Analyzing 4.1... dst_node is FlowTables (count={})".format(self.count))

                # Perform OpenFlow processing and get the port for the next packet
                applied_pipeline_result = apply_pipeline(msg, flowtables=dst_node)
                # todo : Floodingなどの処理を追加
                ports_to_msg: list[tuple[str, Msg]] = applied_pipeline_result["port_to_msg"]
                pp = applied_pipeline_result["packet_processing"]

                if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                    logger.debug("Analyzing 4.2... After applied pipeline (count={}, out_ports_to_msg={})".format(self.count, ports_to_msg))

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

                    if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                        logger.debug("Analyzing 4.3... get next of dst_node (count={}, next_switch={})".format(self.count, next_switch))

                    # set next switch and port
                    # If the next node is a switch, it computes the OpenFlow processing and add it to the queue.
                    if isinstance(next_switch, str) and self._is_switch(next_switch):  # switch
                        # self._update_msg(msg, next_port=next_port)  # とりま廃止

                        if next_edge not in visited_edges:  # loop?
                            # get packet
                            msg = self._get_packet(next_edge, m)

                            if msg:
                                # get flowtable
                                flowtable = self._get_flowtable(next_switch, m.sniff_timestamp)
                                if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                    logger.debug("Analyzing 4.4... get flowtable (count={}, flow_table={})"
                                                 .format(self.count, flowtable))
                                # todo: flowtableがNoneのときの処理
                                if flowtable:
                                    self._update_msg(msg, next_port=next_port)
                                    queue.enqueue(src_node=dst_node, msg=msg, edge=next_edge,
                                                  next_tables=flowtable, next_port=next_port, packet_processing=pp)
                                    # continue explicitly
                                    continue
                                else:
                                    if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                        logger.warning("Analyzing 4.4.. Getting flow_table is fail. "
                                                       "Although the packets are captured, the flow table is not got."
                                                       "This could be an error.  (count={})".format(self.count))
                            else:
                                if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                    logger.warning("Analyzing 4.4... cannot pop packet. Therefore the trace is not finished (count={} next_edge={} m={})"
                                                 .format(self.count, next_edge, m))
                                trace.is_finish = False
                                return trace
                        else:
                            if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                logger.warning("Analyzing 4.4... already visited edge (count={}, next_edge={})".format(self.count, next_edge))
                            # TODO:
                            #   * Terminate the analysis or throw an error
                    else:  # switch or controller or other

                        # If next node is not switch, it is considered as an endpoint adn add to PacketTrace.
                        if next_switch == "controller":
                            # TODO: get packet in
                            #   まだ，packet_inメッセージの取得ができていない
                            if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                logger.debug("Analyzing 4.4... next switch is controller. Therefore trace is finished. "
                                             "(count={}, next_switch={})".format(self.count, next_switch))
                            packet_arc = PacketArc(src=dst_node,
                                                   msg=msg,
                                                   edge=next_edge,
                                                   dst="controller",
                                                   dst_interface="")
                            packet_arc.packet_processing = pp
                            trace.add_arc(copy.deepcopy(packet_arc))
                            trace.is_finish = True
                            return trace
                        elif self._is_terminal_edge(next_edge):
                            if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                logger.debug("Analyzing 4.4... next switch is host. Therefore trace is finished. (count={}, next_switch={})"
                                             .format(self.count, next_switch))
                            # next host
                            packet_arc = PacketArc(src=dst_node,
                                                   msg=msg,
                                                   edge=next_edge,
                                                   dst=next_switch,
                                                   dst_interface=next_port)
                            packet_arc.packet_processing = pp
                            trace.add_arc(copy.deepcopy(packet_arc))
                            trace.is_finish = True  # todo Flooding
                            return trace
                        else:
                            if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                                logger.error("Analyzing 4.4... next switch is no matching device ({})".format(next_switch))
                            trace.is_finish = False
                            return trace
                else:
                    if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                        logger.warning("Analyzing 4.2... no outports (count={}, applied_pipeline_result={})".format(self.count, applied_pipeline_result))

            else:  # not switch
                if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                    logger.warning("Analyzing 4.1... dst is not flowtable(count={}, dst_node={})".format(self.count, dst_node))
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
            count (int) : polling interval counte
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

        if conf.OUTPUT_ANALYZING_POLLING_TO_LOGFILE:
            logger.debug("polled repository (start_time={}, until={}) values = {} {}"
                         .format(self.start_time, self.count, self.tmp_packets, self.tmp_packetinout))

    def _poll_packet_repo(self, count, edges, get_all=False):
        """poll packet repository

        Args:
            count (int) : interval count
            edges (list) : edges list

        Returns:
            dict[str, list[Msg]] : edge to msgs
        """
        packets = {}
        until = get_until_time(self.start_time, self._interval, count)
        if get_all:
            until = None

        for edge in edges:
            tmp_packets = none2emptylist(self.packet_repo.pop(edge, until=until))
            packets[edge] = tmp_packets
        return packets

    def _poll_packet_inout_repo(self, count, switches, get_all=False):
        """polling packetIn/Out repository

        Args:
            count (int) : polling interval count
            switches (list[str]) : polled switches

        Returns:
            dict[str, list[MsgForOFMsg]] : switch to packets

        Notes:
            * This function converts a packet to Msg object
        """
        packet_inouts = {}
        until = get_until_time(self.start_time, self._interval, count)
        if get_all:
            until = None

        for switch in switches:
            # get datapath id
            s_dpid = int(self.tracing_net.get_datapath_id(switch), 16)
            if s_dpid is not None:
                tmp_p = none2emptylist(self.packet_inout_repo.pop(s_dpid, until=until))
                if conf.OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE:
                    logger.debug("Analyzing 1.2... tmp_p = {}, s_dpip = {}".format(tmp_p, s_dpid))

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
                if conf.JUDGE_PACKETS_ONLY_BY_TIME:
                    if p.timestamp >= msg.timestamp:
                        return p
                else:
                    if p.timestamp >= msg.timestamp and p.is_equal_msg(msg):
                        return p

    def _del_tmp_packet(self, packet_trace: PacketTrace):
        """Deletes the messages on the trace from tmp_packet

        Args:
            packet_trace (PacketTrace) : packet trace
        """
        removed = []
        for arc in packet_trace.arcs:
            for packets in self.tmp_packets.values():
                for p in packets:
                    if arc.msg == p:
                        removed.append(arc.msg)
                        packets.remove(arc.msg)
                        break
                    else:
                        # packet_in_outなら削除されない
                        # logger.warning("msg didn't remove from tmp_packets")
                        pass
                if len(removed) > 1:
                    break
        if len(removed) == 0:
            logger.warning("No packer are removed. (count={} packet_trace={})"
                           "This may be a bug.".format(self.count, packet_trace))

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
        """pop packet in message

        Args:
            switch (str) :
            timestamp (str) :

        Returns:

        """
        packet = None
        if self.tmp_packetinout[switch]:
            for p in self.tmp_packetinout[switch]:
                if p.message_type == Type.OFPT_PACKET_IN:
                    if p.timestamp >= timestamp:
                        packet = p
                        break
            if packet is not None:
                self.tmp_packetinout[switch].remove(packet)
        return packet

    def _is_switch(self, switch):
        return self.tracing_net.is_switch(switch)

    def _is_controller(self, port: str):
        """Is the port connected controller?

        todo:
            * 1000の判定をどうにかする
        """
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
        """

        Returns:
            list[str] : mac addresses
        """
        hosts = self.tracing_net.hosts
        mac_addresses = [host.MAC() for host in hosts]
        return mac_addresses

    def _get_flooding_ports_and_edges(self, switch, of_port):
        """

        Args:
            switch:
            of_port:

        Returns:
            dict[str, (str, str, str)] : interface to (next node, next interface, next edge)
        """
        pe = {}
        for intf, port in self.tracing_net.get(switch).ports.items():
            if port != of_port and intf.name != 'lo':
                pe[intf.name] = self._get_next_and_edge(intf.name)
        return pe


def none2emptylist(obj):
    if isinstance(obj, list):
        return obj
    elif obj is None:
        return []
    else:
        return []


def get_until_time(start_time, interval, count):
    """calculate until time"""
    return start_time + interval*count - DELAY

