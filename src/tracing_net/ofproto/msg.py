"""
See `wireshark <https://www.wireshark.org/docs/dfref/>`_ for mapping of packet objects to OpenFlow field

Notes:
    * Unable to get in_port
"""
from logging import getLogger, setLoggerClass, Logger


setLoggerClass(Logger)
logger = getLogger('tracing_net.msg')


class Msg:
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
        raise NotImplementedError

    @property
    def ipv6_nd_sll(self):
        raise NotImplementedError

    @property
    def ipv6_nd_tll(self):
        raise NotImplementedError

    @property
    def mpls_label(self):
        """

        Todo:
            * self.pushed_mpls
        """
        raise NotImplementedError

    @property
    def mpls_tc(self):
        raise NotImplementedError

    @property
    def mpls_bos(self):
        raise NotImplementedError

    @property
    def pbb_isid(self):
        raise NotImplementedError

    @property
    def tunnel_id(self):
        raise NotImplementedError

    @property
    def ipv6_exthdr(self):
        raise NotImplementedError

    @property
    def pbb_uca(self):
        raise NotImplementedError

    @property
    def tcp_flags(self):
        raise NotImplementedError

    @property
    def actset_output(self):
        raise NotImplementedError

    # def __eq__(self, other):
    #     raise NotImplementedError

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
