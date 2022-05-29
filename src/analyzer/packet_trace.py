"""
Models of packet trace
"""

from abc import ABCMeta, abstractmethod
from google.protobuf.json_format import MessageToDict

from src.vnet.ofproto.table import FlowTables
from src.api.proto import net_pb2


class PacketArc:
    """Packet arc between src to dst

    Attributes:
        src (str or FlowTables) :
        msg (Msg) : message
        dst (str or FlowTables) :
        dst_interface (str) :
        packet_processing (PacketProcessing) : パケットの処理内容

    TODO:
        * 今後，マッチしたリストなども保存する必要がある
        * プロトコルに対するインターフェースを追加
        * BFSを実行したcounterを用意して，バグが無いかを確かめる
    """

    def __init__(self, src=None, msg=None, edge=None, dst=None, dst_interface=None):
        # Host or Controller or flow table
        self.src = src
        self.msg = msg
        self.edge = edge
        self.dst = dst
        self.dst_interface = dst_interface

        self.packet_processing = None

    @property
    def src_interface(self):
        return self.msg.in_phy_port

    @property
    def src_switch(self):
        """src switch
        Notes:
            * 現場，switchにしか機能しない？？？
        """
        return self.src.switch_name

    @property
    def dst_switch(self):
        """dst switch
        Notes:
            * 現場，switchにしか機能しない？？？
        """
        return self.dst.switch_name

    @property
    def timestamp(self):
        """msg timestamp"""
        if getattr(self.msg, 'sniff_timestamp', None):
            return self.msg.sniff_timestamp
        elif getattr(self.msg, 'timestamp', None):
            return self.msg.timestamp

    @property
    def protocol(self):
        """ethernet type"""
        return self.msg.eth_type

    @classmethod
    def get_packet_link(cls):
        pass

    def to_dict(self):
        """this arc converts to dict"""
        # src and dst
        src = self.src
        dst = self.dst
        if isinstance(self.src, FlowTables):
            src = self.src.switch_name
        if isinstance(self.dst, FlowTables):
            dst = self.dst.switch_name

        # msg
        msg = self.msg
        if getattr(msg, 'pkt', None):
            msg = self.msg.pkt.__repr__()  # TODO to json
        elif getattr(msg, 'of_msg', None):
            msg = self.msg.of_msg.__repr__()

        # dict
        d = {
            'src': src,  # TODO to json
            'msg': msg,  # TODO to json
            'edge': self.edge,
            'dst': dst,  # TODO to json
        }
        return d

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.PacketArc
        """
        arc_msg = net_pb2.PacketArc()
        # src and dst
        src = self.src
        dst = self.dst
        if isinstance(self.src, FlowTables):
            src = self.src.switch_name
        if isinstance(self.dst, FlowTables):
            dst = self.dst.switch_name
        arc_msg.src = src
        arc_msg.dst = dst
        if self.edge:
            arc_msg.edge = self.edge
        if self.dst_interface:
            arc_msg.dst_interface = self.dst_interface
        arc_msg.pkt.CopyFrom(self.msg.get_protobuf_message())
        if self.packet_processing:
            arc_msg.packet_processing.CopyFrom(self.packet_processing.get_protobuf_message())
        return arc_msg

    def __str__(self):
        src = self.src
        dst = self.dst
        if isinstance(self.src, FlowTables):
            src = self.src.switch_name
        if isinstance(self.dst, FlowTables):
            dst = self.dst.switch_name
        return "({}, {})".format(src, dst)

    def __repr__(self):
        return "(src={}, msg={}, edge={}, dst={}, dst_interface={})".format(self.src, self.msg, self.edge, self.dst,
                                                                            self.dst_interface)


class AbstractPacketTrace(metaclass=ABCMeta):
    """This is the set of arc of packet.
    This class represents the trace of a packet.

    Attributes:
        arcs (list) : list of arcs

    TODO:
        * ノードのリストを保持し，それをpacketprocessingにする
    """

    def __init__(self):
        self.arcs: list[PacketArc] = []
        # identifier for trace list
        self.id = -1

    @abstractmethod
    def add_arc(self, arc):
        """

        Args:
            arc (PacketArc) :
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def timestamp(self):
        """This is the timestamp at the beginning of the list of arcs"""
        raise NotImplementedError


class PacketTrace(AbstractPacketTrace):
    """Packet Trace"""

    def __init__(self):
        super(PacketTrace, self).__init__()
        self.is_finish = False

        self.packet_trace_id = -1

    def add_arc(self, arc):
        self.arcs.append(arc)

    @property
    def timestamp(self):
        """This is the timestamp at the beginning of the list of arcs"""
        if len(self.arcs) >= 1:
            return self.arcs[0].timestamp

    @property
    def protocol(self):
        """ethernet type"""
        if len(self.arcs) >= 1:
            return self.arcs[0].protocol

    def to_dict(self):
        return MessageToDict(self.get_protobuf_message())

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.PacketTrace
        """
        packet_trace_msg = net_pb2.PacketTrace()
        packet_trace_msg.timestamp = self.timestamp
        packet_trace_msg.protocol = str(self.protocol)
        for a in self.arcs:
            packet_trace_msg.arcs.append(a.get_protobuf_message())
        return packet_trace_msg

    def __lt__(self, other):
        if not isinstance(other, PacketTrace):
            raise TypeError
        return self.timestamp < other.timestamp

    def __le__(self, other):
        if not isinstance(other, PacketTrace):
            raise TypeError
        return self.timestamp <= other.timestamp

    def __gt__(self, other):
        if not isinstance(other, PacketTrace):
            raise TypeError
        return self.timestamp > other.timestamp

    def __ge__(self, other):
        if not isinstance(other, PacketTrace):
            raise TypeError
        return self.timestamp >= other.timestamp

    def __str__(self):
        string = "{} : ".format(self.protocol)
        for arc in self.arcs:
            string = string + str(arc)
        return string

    def __repr__(self):
        return "<PacketTrace {}>".format(self.arcs)


class PacketProcessing:
    """OpenFlow Pipeline Processing

     * This Class holds the content done inside the switch.
     * msgやflowentryはフローのマッチの計算後，フローを適用した直後に更新される．よって，マッチしない場合は更新されない．

    Attributes:
        switch (str) : switch name
            処理されたスイッチの名前．
        flow_table (FlowTables) : 処理されたときのフローテーブル
        msg_list (list) : processing message.
            これを処理前から順番に持たせるか，処理後を順番に持たせるかは検討中
        matched_flowentry_list (list) : matched flow entries.
            これは，マッチしたフローのidの集合です．各テーブルごとに存在する必要がある．
        # out_port : TODO: どこかで，どのテーブルでoutportするかを保存してもいい

    TODO:
        * add metadata and outport
        * 現状はAction Setについては実装できていない
    """

    def __init__(self, switch: str, flow_table: FlowTables = None):
        self.switch = switch
        self.flow_table = flow_table
        self.msg_list = []
        self.matched_flowentry_list = []

        self.action_set = None
        self.packet_after_action_set = None
        self.outport2msg = []

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.PacketProcessing
        """
        packet_processing = net_pb2.PacketProcessing()
        packet_processing.switch = self.switch
        packet_processing.flow_table.CopyFrom(self.flow_table.get_protobuf_message())
        packet_processing.action_set.CopyFrom(self.action_set.get_protobuf_message())
        packet_processing.packet_after_action_set.CopyFrom(self.packet_after_action_set.get_protobuf_message())
        for m in self.msg_list:
            packet_processing.pkts.append(m.get_protobuf_message())
        for f_i in self.matched_flowentry_list:
            packet_processing.matched_flows.append(f_i)
        for p2m in self.outport2msg:
            packet_processing.outs[str(p2m[0])].CopyFrom(p2m[1].get_protobuf_message())
        return packet_processing

    def to_dict(self):
        return MessageToDict(self.get_protobuf_message())

    def add_msg(self, msg, table_id):
        """処理されたパケット．
        * 処理対象と処理後のパケットの列
        * 始めのパケットは table_id = -1

        Args:
            msg (Msg) :
            table_id (int) : todo
        """
        self.msg_list.append(msg)

    def add_flowentry(self, flow_id: int):
        """パケットにマッチしたフローエントリのid

        Args:
            flow_id (int) :
        """
        self.matched_flowentry_list.append(flow_id)


packet_trace_id = 0
def get_packet_trace_id():
    global packet_trace_id
    packet_trace_id += 1
    return packet_trace_id

