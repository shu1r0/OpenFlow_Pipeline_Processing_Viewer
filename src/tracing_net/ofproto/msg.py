"""
See `wireshark <https://www.wireshark.org/docs/dfref/>`_ for mapping of packet objects to OpenFlow field

Notes:
    * Unable to get in_port
"""
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger


setLoggerClass(Logger)
logger = getLogger('tracing_net.msg')

# Notes:
#    * do not include in_port and in_phy_port
OpenFlowMatchingProperties = ["eth_dst", "eth_src", "eth_type", "vlan_vid", "vlan_pcp", "ip_dscp", "ip_ecn", "ip_proto", "ipv4_src", "ipv4_dst", "tcp_src", "tcp_dst ", "udp_src", "udp_dst", "sctp_src", "sctp_dst", "icmpv4_type", "icmpv4_code", "arp_op", "arp_spa", "arp_tpa", "arp_sha", "arp_tha", "ipv6_src", "ipv6_dst", "ipv6_flabel", "icmpv6_type", "icmpv6_code", "ipv6_nd_target", "ipv6_nd_sll", "ipv6_nd_tll", "mpls_label", "mpls_tc", "mpls_bos", "pbb_isid", "tunnel_id", "ipv6_exthdr", "pbb_uca", "tcp_flags", "actset_output"]


class OpenFlowPacket(metaclass=ABCMeta):
    """OpenFlow packet"""

    def __init__(self):
        self.in_port = None
        self.in_phy_port = None

    @property
    @abstractmethod
    def eth_dst(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def eth_src(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def eth_type(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def vlan_vid(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def vlan_pcp(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ip_dscp(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ip_ecn(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ip_proto(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ipv4_src(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ipv4_dst(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def tcp_src(self):
        """TCP source port"""
        raise NotImplementedError

    @property
    @abstractmethod
    def tcp_dst(self):
        """TCP destination port"""
        raise NotImplementedError

    @property
    @abstractmethod
    def udp_src(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def udp_dst(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def sctp_src(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def sctp_dst(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def icmpv4_type(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def icmpv4_code(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def arp_op(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def arp_spa(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def arp_tpa(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def arp_sha(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def arp_tha(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ipv6_src(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ipv6_dst(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ipv6_flabel(self):
        """IPv6 Flow Label"""
        raise NotImplementedError

    @property
    @abstractmethod
    def icmpv6_type(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def icmpv6_code(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ipv6_nd_target(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ipv6_nd_sll(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ipv6_nd_tll(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def mpls_label(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def mpls_tc(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def mpls_bos(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def pbb_isid(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def tunnel_id(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def ipv6_exthdr(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def pbb_uca(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def tcp_flags(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def actset_output(self):
        raise NotImplementedError

    @abstractmethod
    def to_json(self):
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, OpenFlowPacket):
            return False

        for p in OpenFlowMatchingProperties:
            p1 = getattr(self, p, None)
            p2 = getattr(other, p, None)
            if p1 != p2:
                return False
        return True


class Msg(OpenFlowPacket):
    """Packet message
    This is an abstraction of the packets of flowing in the data plane.

    Attributes:
         captured_interface (str) :
         sniff_timestamp (str) : unix timestamp
         pkt (packet) :
         in_port (str) :
         in_phy_port (str) :

    Notes:
        ``in_port`` represents the interface on the switch, not the OpenFlow port.
        This is due to the OVS data specification.

    Todo:
        * provide two in_ports
    """

    def __init__(self, captured_interface, sniff_timestamp, pkt, in_port=None, in_phy_port=None):
        super(Msg, self).__init__()
        self.captured_interface = captured_interface
        self.sniff_timestamp = sniff_timestamp
        self.pkt = pkt
        self.metadata = None
        self.in_port = in_port if in_port else self.captured_interface
        self.in_phy_port = in_phy_port if in_phy_port else self.captured_interface
        self.pushed_vlan = None
        self.pushed_mpls = None

    @property
    def eth_dst(self):
        try:
            return self.pkt.eth.dst
        except AttributeError:
            return None

    @property
    def dl_dst(self):
        """for ovs flow"""
        try:
            return self.pkt.eth.dst
        except AttributeError:
            return None

    @property
    def eth_src(self):
        try:
            return self.pkt.eth.src
        except AttributeError:
            return None

    @property
    def dl_src(self):
        """for ovs flow"""
        try:
            return self.pkt.eth.src
        except AttributeError:
            return None

    @property
    def eth_type(self):
        try:
            return self.pkt.eth.type
        except AttributeError:
            return None

    @property
    def vlan_vid(self):
        try:
            if self.pushed_vlan:
                return self.pushed_vlan
            return self.pkt.vlan.id
        except AttributeError:
            return None

    @property
    def vlan_pcp(self):
        try:
            return self.pkt.vlan.priority
        except AttributeError:
            return None

    @property
    def ip_dscp(self):
        try:
            return self.pkt.ip.dsfield.dscp
        except AttributeError:
            return None

    @property
    def ip_ecn(self):
        try:
            return self.pkt.ip.dsfield.ecn
        except AttributeError:
            return None

    @property
    def ip_proto(self):
        try:
            return self.pkt.ip.proto
        except AttributeError:
            return None

    @property
    def ipv4_src(self):
        try:
            return self.pkt.ip.src
        except AttributeError:
            return None
    @property
    def ipv4_dst(self):
        try:
            return self.pkt.ip.dst
        except AttributeError:
            return None

    @property
    def tcp_src(self):
        """TCP source port"""
        try:
            return self.pkt.tcp.srcport
        except AttributeError:
            return None

    @property
    def tcp_dst(self):
        """TCP destination port"""
        try:
            return self.pkt.tcp.dstport
        except AttributeError:
            return None

    @property
    def udp_src(self):
        try:
            return self.pkt.udp.srcport
        except AttributeError:
            return None

    @property
    def udp_dst(self):
        try:
            return self.pkt.udp.dstport
        except AttributeError:
            return None

    @property
    def sctp_src(self):
        raise NotImplementedError

    @property
    def sctp_dst(self):
        raise NotImplementedError

    @property
    def icmpv4_type(self):
        try:
            return self.pkt.icmp.type
        except AttributeError:
            return None

    @property
    def icmpv4_code(self):
        try:
            return self.pkt.icmp.code
        except AttributeError:
            return None

    @property
    def arp_op(self):
        try:
            return self.pkt.arp.opcode
        except AttributeError:
            return None

    @property
    def arp_spa(self):
        try:
            return self.pkt.arp.src.proto_ipv4
        except AttributeError:
            return None

    @property
    def arp_tpa(self):
        try:
            return self.pkt.arp.dst.proto_ipv4
        except AttributeError:
            return None

    @property
    def arp_sha(self):
        try:
            return self.pkt.arp.src.hw_mac
        except AttributeError:
            return None

    @property
    def arp_tha(self):
        try:
            return self.pkt.arp.dst.hw_mac
        except AttributeError:
            return None

    @property
    def ipv6_src(self):
        try:
            return self.pkt.ipv6.src
        except AttributeError:
            return None

    @property
    def ipv6_dst(self):
        try:
            return self.pkt.ipv6.dst
        except AttributeError:
            return None

    @property
    def ipv6_flabel(self):
        """IPv6 Flow Label"""
        try:
            return self.pkt.ipv6.flow
        except AttributeError:
            return None

    @property
    def icmpv6_type(self):
        try:
            return self.pkt.icmpv6.type
        except AttributeError:
            return None

    @property
    def icmpv6_code(self):
        try:
            return self.pkt.icmpv6.code
        except AttributeError:
            return None

    @property
    def ipv6_nd_target(self):
        return None

    @property
    def ipv6_nd_sll(self):
        return None

    @property
    def ipv6_nd_tll(self):
        return None

    @property
    def mpls_label(self):
        """

        Todo:
            * self.pushed_mpls
        """
        return None

    @property
    def mpls_tc(self):
        return None

    @property
    def mpls_bos(self):
        return None

    @property
    def pbb_isid(self):
        return None

    @property
    def tunnel_id(self):
        return None

    @property
    def ipv6_exthdr(self):
        return None

    @property
    def pbb_uca(self):
        return None

    @property
    def tcp_flags(self):
        return None

    @property
    def actset_output(self):
        return None

    def set_vlan(self, vlan_id):
        self.pushed_vlan = vlan_id

    def set_mpls(self, mpls_label):
        self.pushed_mpls = mpls_label

    def to_json(self):
        raise NotImplementedError

    def __repr__(self):
        return "<Msg captured_interface={}, sniff_timestamp={}, pkt={}, in_port={}, in_phy_port={}>"\
            .format(self.captured_interface, self.sniff_timestamp, self.pkt.__repr__(), self.in_port, self.in_phy_port)


#
# Methods for validation
#
def packet_to_dict(pkt):
    """packet to dict

    Args:
        pkt (Packet): packet
    """
    dict_fields = {}
    for layer in pkt.layers:
        dict_fields[layer.layer_name] = layer_to_dict(layer)['_all_fields']
    return dict_fields


def layer_to_dict(obj, expect_raw=True):
    """layer object to dict

    Args:
        obj (pyshark.packet.layer.Layer) : packet layer
        expect_raw (bool) : expect raw data?

    Returns:
        dict
    """
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            k = k.split(".")  # layer field name
            k = k[len(k)-1]
            if expect_raw and k.split("_")[-1] == "raw":
                continue
            else:
                data[k] = layer_to_dict(v, expect_raw)
        return data
    elif hasattr(obj, "_ast"):
        return layer_to_dict(obj._ast(), expect_raw)
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [layer_to_dict(v, expect_raw) for v in obj]
    elif hasattr(obj, "__dict__"):
        return layer_to_dict(vars(obj), expect_raw)
    elif hasattr(obj, "__slots__"):
        data = layer_to_dict(dict((name, getattr(obj, name)) for name in getattr(obj, "__slots__")), expect_raw)
        return data
    else:
        return obj
