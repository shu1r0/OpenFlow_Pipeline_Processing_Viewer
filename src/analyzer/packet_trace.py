from abc import ABCMeta, abstractmethod


class PacketArc:
    """

    Attributes:
        src_switch_tables (str) :
        msg (Msg) : message
        dst_switch_tables (str) :
        dst_interface (str) :
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
        return self.src_switch_tables.switch_name

    @property
    def dst_switch(self):
        return self.dst_switch_tables.switch_name

    def set_src(self, switch_tables, msg):
        self.src_switch_tables = switch_tables
        self.msg = msg

    def set_dst(self, switch_tables, interface):
        self.dst_switch_tables = switch_tables
        self.dst_interface = interface

    @classmethod
    def get_packet_link(cls):
        pass


class AbstractPacketTrace(metaclass=ABCMeta):
    """This is the set of arc of packet.
    This class represents the trace of a packet.

    Attributes:
        arcs (list) : list of arcs
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


class PacketTrace(AbstractPacketTrace):

    def __init__(self):
        super(PacketTrace, self).__init__()
        self._is_finish = False

    def add_arc(self, arc):
        self.arcs.append(arc)
