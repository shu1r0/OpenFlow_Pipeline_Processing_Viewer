"""
Models of packet trace
"""

from abc import ABCMeta, abstractmethod

from src.tracing_net.ofproto.table import FlowTables


class PacketArc:
    """Packet arc between src to dst

    Attributes:
        src (str or FlowTables) :
        msg (Msg) : message
        dst (str or FlowTables) :
        dst_interface (str) :

    TODO:
        * 今後，マッチしたリストなども保存する必要がある
    """

    def __init__(self, src=None, msg=None, edge=None, dst=None, dst_interface=None):
        # Host or Controller or flow table
        self.src = src
        self.msg = msg
        self.edge = edge
        self.dst = dst
        self.dst_interface = dst_interface

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

    def __repr__(self):
        return "(src={}, msg={}, edge={}, dst={}, dst_interface={})".format(self.src, self.msg, self.edge, self.dst, self.dst_interface)


class AbstractPacketTrace(metaclass=ABCMeta):
    """This is the set of arc of packet.
    This class represents the trace of a packet.

    Attributes:
        arcs (list) : list of arcs

    TODO:
        * ノードのリストを保持し，それをpacketprocessingにする
    """

    def __init__(self):
        self.arcs = []

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

    def add_arc(self, arc):
        self.arcs.append(arc)

    @property
    def timestamp(self):
        """This is the timestamp at the beginning of the list of arcs"""
        if len(self.arcs) >= 1:
            return self.arcs[0].timestamp

    def to_dict(self):
        l = []
        for arc in self.arcs:
            l.append(arc.to_dict())
        return l

    def __repr__(self):
        return "<PacketTrace {}>".format(self.arcs)


class PacketProcessing:

    pass
