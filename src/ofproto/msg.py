from scapy.layers.l2 import Ether, ARP, Dot1Q, Dot1AD
from scapy.layers.inet import IP, ICMP, TCP, UDP
from scapy.layers.inet6 import IPv6, _ICMPv6

from pyof.v0x04.common.port import PortNo

from src.tracing_net.ofproto.msg import MsgBase


class MsgForOFMsg(MsgBase):

    def __init__(self, ofmsg):
        super(MsgForOFMsg, self).__init__()
        self.ofmsg = ofmsg
        self.pkt = None
        self.in_port = PortNo.OFPP_CONTROLLER

    @property
    def sniff_timestamp(self):
        return self.ofmsg.timestamp

    @property
    def eth_dst(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.l2.html#scapy.layers.l2.Ether
        """
        if Ether in self.pkt:
            return self.pkt[Ether].dst
        else:
            return None

    @property
    def eth_src(self):
        if Ether in self.pkt:
            return self.pkt[Ether].src
        else:
            return None

    @property
    def eth_type(self):
        if Ether in self.pkt:
            return self.pkt[Ether].type
        else:
            return None

    @property
    def vlan_vid(self):
        if self.pushed_vlan:
            return self.pushed_vlan
        if Dot1Q in self.pkt:
            return self.pkt[Dot1Q].vlan
        if Dot1AD in self.pkt:
            return self.pkt[Dot1AD].vlan
        else:
            return None

    @property
    def vlan_pcp(self):
        if Dot1Q in self.pkt:
            return self.pkt[Dot1Q].prio
        if Dot1AD in self.pkt:
            return self.pkt[Dot1AD].prio
        else:
            return None

    @property
    def ip_dscp(self):
        try:
            return self.pkt[IP].tos & 0b11111100
        except AttributeError:
            return None

    @property
    def ip_ecn(self):
        try:
            return self.pkt[IP].tos & 0b00000011
        except AttributeError:
            return None

    @property
    def ip_proto(self):
        if IP in self.pkt:
            return self.pkt[IP].proto
        else:
            return None

    @property
    def ipv4_src(self):
        if IP in self.pkt:
            return self.pkt[IP].src
        else:
            return None

    @property
    def ipv4_dst(self):
        if IP in self.pkt:
            return self.pkt[IP].dst
        else:
            return None

    @property
    def tcp_src(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet.html#scapy.layers.inet.TCP
        """
        if TCP in self.pkt:
            return self.pkt[TCP].sport
        else:
            return None

    @property
    def tcp_dst(self):
        if TCP in self.pkt:
            return self.pkt[TCP].dport
        else:
            return None

    @property
    def udp_src(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet.html#scapy.layers.inet.UDP
        """
        if UDP in self.pkt:
            return self.pkt[UDP].sport
        else:
            return None

    @property
    def udp_dst(self):
        if UDP in self.pkt:
            return self.pkt[UDP].dport
        else:
            return None

    @property
    def sctp_src(self):
        return None

    @property
    def sctp_dst(self):
        return None

    @property
    def icmpv4_type(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet.html#scapy.layers.inet.ICMP
        """
        if ICMP in self.pkt:
            return self.pkt[ICMP].type
        else:
            return None

    @property
    def icmpv4_code(self):
        if ICMP in self.pkt:
            return self.pkt[ICMP].code
        else:
            return None

    @property
    def arp_op(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.l2.html#scapy.layers.l2.ARP
        """
        if ARP in self.pkt:
            return self.pkt[ARP].op
        else:
            return None

    @property
    def arp_spa(self):
        if ARP in self.pkt:
            return self.pkt[ARP].psrc
        else:
            return None

    @property
    def arp_tpa(self):
        if ARP in self.pkt:
            return self.pkt[ARP].pdst
        else:
            return None

    @property
    def arp_sha(self):
        if ARP in self.pkt:
            return self.pkt[ARP].hwsrc
        else:
            return None

    @property
    def arp_tha(self):
        if ARP in self.pkt:
            return self.pkt[ARP].hwdst
        else:
            return None

    @property
    def ipv6_src(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet6.html#scapy.layers.inet6.IPv6
        """
        if IPv6 in self.pkt:
            return self.pkt[IPv6].src
        else:
            return None

    @property
    def ipv6_dst(self):
        if IPv6 in self.pkt:
            return self.pkt[IPv6].dst
        else:
            return None

    @property
    def ipv6_flabel(self):
        if IPv6 in self.pkt:
            return self.pkt[IPv6].fl
        else:
            return None

    @property
    def icmpv6_type(self):
        """

        TODO:
            * verify later
        """
        for layer in self.pkt.layers():
            if isinstance(layer, _ICMPv6):
                return layer.type
        return None

    @property
    def icmpv6_code(self):
        for layer in self.pkt.layers():
            if isinstance(layer, _ICMPv6):
                return layer.code
        return None

    @property
    def ipv6_nd_target(self):
        pass

    @property
    def ipv6_nd_sll(self):
        pass

    @property
    def ipv6_nd_tll(self):
        pass

    @property
    def mpls_label(self):
        pass

    @property
    def mpls_tc(self):
        pass

    @property
    def mpls_bos(self):
        pass

    @property
    def pbb_isid(self):
        pass

    @property
    def tunnel_id(self):
        pass

    @property
    def ipv6_exthdr(self):
        pass

    @property
    def pbb_uca(self):
        pass

    @property
    def tcp_flags(self):
        pass

    @property
    def actset_output(self):
        pass

    def set_vlan(self, vlan_id):
        self.pushed_vlan = vlan_id

    def set_mpls(self, mpls_label):
        self.pushed_mpls = mpls_label

    def to_json(self):
        pass

