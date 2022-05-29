"""
See `wireshark <https://www.wireshark.org/docs/dfref/>`_ for mapping of packet objects to OpenFlow field

Notes:
    * Unable to get in_port

TODO:
    * tsharkとscapyの両方からパースできるようにする
    * 比較は基本INt，表示は16進数で
"""
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from src.config import conf
from src.api.proto import net_pb2


setLoggerClass(Logger)
logger = getLogger('vnet.msg')

# Notes:
#    * in_port and in_phy_port are not included
OpenFlowMatchingProperties = ["eth_dst", "eth_src", "eth_type", "vlan_vid", "vlan_pcp", "ip_dscp", "ip_ecn", "ip_proto",
                              "ipv4_src", "ipv4_dst", "tcp_src", "tcp_dst ", "udp_src", "udp_dst", "sctp_src",
                              "sctp_dst", "icmpv4_type", "icmpv4_code", "arp_op", "arp_spa", "arp_tpa", "arp_sha",
                              "arp_tha", "ipv6_src", "ipv6_dst", "ipv6_flabel", "icmpv6_type", "icmpv6_code",
                              "ipv6_nd_target", "ipv6_nd_sll", "ipv6_nd_tll", "mpls_label", "mpls_tc", "mpls_bos",
                              "pbb_isid", "tunnel_id", "ipv6_exthdr", "pbb_uca", "tcp_flags", "actset_output"]


class OpenFlowPacket(metaclass=ABCMeta):
    """OpenFlow packet"""

    def __init__(self):
        self.in_port = None
        self.in_phy_port = None
        self._properties = {}
        for p in OpenFlowMatchingProperties:
            self._properties[p] = None

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

    def set_properties(self, key, value):
        self._properties[key] = value

    def get_openflow_properties(self):
        """for debug"""
        properties = {}
        for p in OpenFlowMatchingProperties:
            v = getattr(self, p, None)
            properties[p] = v
        return properties


# todo: FlowPacketとかその辺の名前にする
class MsgBase(OpenFlowPacket, metaclass=ABCMeta):
    """packet wrapper """

    def __init__(self, pkt, timestamp):
        super(MsgBase, self).__init__()
        # pkt data
        self.pkt = pkt
        # timestamp
        self.timestamp = timestamp

        self.metadata = None

        self.pushed_vlan = None
        self.pushed_mpls = None

    def set_vlan(self, vlan_id):
        self.pushed_vlan = vlan_id

    def set_mpls(self, mpls_label):
        self.pushed_mpls = mpls_label

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.Packet
        """
        packet_msg = net_pb2.Packet()
        packet_msg.timestamp = self.timestamp
        packet_msg.in_port = str(self.in_port)
        packet_msg.in_phy_port = self.in_phy_port
        for p in OpenFlowMatchingProperties:
            v = getattr(self, p, None)
            if v:
                packet_msg.fields[p] = str(v)
        if self.metadata:
            packet_msg.fields["metadata"] = str(self.metadata)
        return packet_msg

    def is_equal_msg(self, other):
        """Compare OpenFlow properties."""
        if not isinstance(other, OpenFlowPacket):
            raise TypeError("It should be OpenFlow Packet")

        # todo: 本来はすべて判定すべき
        MatchingProperties = ["eth_dst", "eth_src", "eth_type",
                              "ip_proto", "ipv4_src", "ipv4_dst"]

        # Do the packet's attributes that can be handled by OpenFlow match?
        for p in MatchingProperties:
            p1 = digitable2int(getattr(self, p, None))
            p2 = digitable2int(getattr(other, p, None))

            if p1 is not None and p2 is not None and type(p1) != type(p2):
                raise TypeError("Property TypeError (pro={}, type1={}{}, type2={}{})"
                                .format(p, type(p1), p1, type(p2), p2))

            if p1 != p2:
                if conf.OUTPUT_PACKET_MATCHING_TO_LOGFILE:
                    logger.debug("Packet {} and packet {} have different {}. (self:{}, other:{})"
                                 .format(self, other, p, p1, p2))
                return False

        if conf.OUTPUT_PACKET_MATCHING_TO_LOGFILE:
            logger.debug("Packet {} and packet {} is equal. ".format(self, other))
        return True

    def __lt__(self, other):
        if other is None or not isinstance(other, MsgBase):
            return TypeError
        return int(self.timestamp) < int(self.timestamp)

    def __le__(self, other):
        if other is None or not isinstance(other, MsgBase):
            return TypeError
        return int(self.timestamp) <= int(self.timestamp)

    def __eq__(self, other):
        """
        Warnings:
            * メッセージのプロパティの比較はここでは行わない．(検索などでおかしくなるから)
            * 正しい比較方法で無いことに注意
        """
        if other is None or not isinstance(other, MsgBase):
            return False
        return self.is_equal_msg(other) and self.timestamp == other.timestamp and self.in_phy_port == other.in_phy_port

    def __gt__(self, other):
        if other is None or not isinstance(other, MsgBase):
            return TypeError
        return int(self.timestamp) > int(self.timestamp)

    def __ge__(self, other):
        if other is None or not isinstance(other, MsgBase):
            return TypeError
        return int(self.timestamp) >= int(self.timestamp)


class Msg(MsgBase):
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
        super(Msg, self).__init__(pkt=pkt, timestamp=sniff_timestamp)
        self.captured_interface = captured_interface
        # TODO: delete
        self.sniff_timestamp = sniff_timestamp

        self.in_port = in_port if in_port else self.captured_interface
        self.in_phy_port = in_phy_port if in_phy_port else self.captured_interface

    @property
    def eth_dst(self):
        if self._properties["eth_dst"]:
            return self._properties["eth_dst"]
        try:
            return str(self.pkt.eth.dst)
        except AttributeError:
            return None

    @property
    def dl_dst(self):
        """for ovs flow"""
        try:
            return str(self.pkt.eth.dst)
        except AttributeError:
            return None

    @property
    def eth_src(self):
        if self._properties["eth_src"]:
            return self._properties["eth_src"]
        try:
            return str(self.pkt.eth.src)
        except AttributeError:
            return None

    @property
    def dl_src(self):
        """for ovs flow"""
        try:
            return str(self.pkt.eth.src)
        except AttributeError:
            return None

    @property
    def eth_type(self):
        if self._properties["eth_type"]:
            return self._properties["eth_type"]
        try:
            return str(self.pkt.eth.type)
        except AttributeError:
            return None

    @property
    def vlan_vid(self):
        if self._properties["vlan_vid"]:
            return self._properties["vlan_vid"]
        try:
            if self.pushed_vlan:
                return self.pushed_vlan
            return str(self.pkt.vlan.id)
        except AttributeError:
            return None

    @property
    def vlan_pcp(self):
        if self._properties["vlan_pcp"]:
            return self._properties["vlan_pcp"]
        try:
            return str(self.pkt.vlan.priority)
        except AttributeError:
            return None

    @property
    def ip_dscp(self):
        if self._properties["ip_dscp"]:
            return self._properties["ip_dscp"]
        try:
            return str(self.pkt.ip.dsfield.dscp)
        except AttributeError:
            return None

    @property
    def ip_ecn(self):
        if self._properties["ip_ecn"]:
            return self._properties["ip_ecn"]
        try:
            return str(self.pkt.ip.dsfield.ecn)
        except AttributeError:
            return None

    @property
    def ip_proto(self):
        if self._properties["ip_proto"]:
            return self._properties["ip_proto"]
        try:
            return str(self.pkt.ip.proto)
        except AttributeError:
            return None

    @property
    def ipv4_src(self):
        if self._properties["ipv4_src"]:
            return self._properties["ipv4_src"]
        try:
            return str(self.pkt.ip.src)
        except AttributeError:
            return None
    @property
    def ipv4_dst(self):
        if self._properties["ipv4_dst"]:
            return self._properties["ipv4_dst"]
        try:
            return str(self.pkt.ip.dst)
        except AttributeError:
            return None

    @property
    def tcp_src(self):
        """TCP source port"""
        if self._properties["tcp_src"]:
            return self._properties["tcp_src"]
        try:
            return str(self.pkt.tcp.srcport)
        except AttributeError:
            return None

    @property
    def tcp_dst(self):
        """TCP destination port"""
        if self._properties["tcp_dst"]:
            return self._properties["tcp_dst"]
        try:
            return str(self.pkt.tcp.dstport)
        except AttributeError:
            return None

    @property
    def udp_src(self):
        if self._properties["udp_src"]:
            return self._properties["udp_src"]
        try:
            return str(self.pkt.udp.srcport)
        except AttributeError:
            return None

    @property
    def udp_dst(self):
        if self._properties["udp_dst"]:
            return self._properties["udp_dst"]
        try:
            return str(self.pkt.udp.dstport)
        except AttributeError:
            return None

    @property
    def sctp_src(self):
        if self._properties["sctp_src"]:
            return self._properties["sctp_src"]
        return None

    @property
    def sctp_dst(self):
        if self._properties["sctp_dst"]:
            return self._properties["sctp_dst"]
        return None

    @property
    def icmpv4_type(self):
        if self._properties["icmpv4_type"]:
            return self._properties["icmpv4_type"]
        try:
            return str(self.pkt.icmp.type)
        except AttributeError:
            return None

    @property
    def icmpv4_code(self):
        if self._properties["icmpv4_code"]:
            return self._properties["icmpv4_code"]
        try:
            return str(self.pkt.icmp.code)
        except AttributeError:
            return None

    @property
    def arp_op(self):
        if self._properties["arp_op"]:
            return self._properties["arp_op"]
        try:
            return str(self.pkt.arp.opcode)
        except AttributeError:
            return None

    @property
    def arp_spa(self):
        if self._properties["arp_spa"]:
            return self._properties["arp_spa"]
        try:
            return str(self.pkt.arp.src.proto_ipv4)
        except AttributeError:
            return None

    @property
    def arp_tpa(self):
        if self._properties["arp_tpa"]:
            return self._properties["arp_tpa"]
        try:
            return str(self.pkt.arp.dst.proto_ipv4)
        except AttributeError:
            return None

    @property
    def arp_sha(self):
        if self._properties["arp_sha"]:
            return self._properties["arp_sha"]
        try:
            return str(self.pkt.arp.src.hw_mac)
        except AttributeError:
            return None

    @property
    def arp_tha(self):
        if self._properties["arp_tha"]:
            return self._properties["arp_tha"]
        try:
            return str(self.pkt.arp.dst.hw_mac)
        except AttributeError:
            return None

    @property
    def ipv6_src(self):
        if self._properties["ipv6_src"]:
            return self._properties["ipv6_src"]
        try:
            return str(self.pkt.ipv6.src)
        except AttributeError:
            return None

    @property
    def ipv6_dst(self):
        if self._properties["ipv6_dst"]:
            return self._properties["ipv6_dst"]
        try:
            return str(self.pkt.ipv6.dst)
        except AttributeError:
            return None

    @property
    def ipv6_flabel(self):
        """IPv6 Flow Label"""
        if self._properties["ipv6_flabel"]:
            return self._properties["ipv6_flabel"]
        try:
            return str(self.pkt.ipv6.flow)
        except AttributeError:
            return None

    @property
    def icmpv6_type(self):
        if self._properties["icmpv6_type"]:
            return self._properties["icmpv6_type"]
        try:
            return str(self.pkt.icmpv6.type)
        except AttributeError:
            return None

    @property
    def icmpv6_code(self):
        if self._properties["icmpv6_code"]:
            return self._properties["icmpv6_code"]
        try:
            return str(self.pkt.icmpv6.code)
        except AttributeError:
            return None

    @property
    def ipv6_nd_target(self):
        if self._properties["ipv6_nd_target"]:
            return self._properties["ipv6_nd_target"]
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


def digitable2int(digitable):
    """

    Args:
        digitable:

    Returns:

    Notes:
        utilに移行
    """
    if isinstance(digitable, str):
        if digitable.isdigit():
            return int(digitable)
        elif len(digitable) >= 2 and digitable[0:2] == "0b":
            return int(digitable, 2)
        elif len(digitable) >= 2 and digitable[0:2] == "0x":
            return int(digitable, 16)
        else:
            return digitable
    return digitable


def field2bytes(field):
    """
    todo:
        将来的にマッチの計算はバイトで行う
    """
    pass
