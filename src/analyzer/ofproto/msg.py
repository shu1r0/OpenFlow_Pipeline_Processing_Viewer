"""

TODO:
    * メッセージの方が違うのでそこをどうにかする
"""

# from scapy.layers.l2 import Ether as , ARP, Dot1Q, Dot1AD
# from scapy.layers.inet import IP, ICMP, TCP, UDP
from scapy.layers.inet6 import _ICMPv6
from scapy.all import *

from pyof.v0x04.common.port import PortNo
from pyof.v0x04.common.header import Type

from src.vnet.ofproto.msg import MsgBase


class MsgForOFMsg(MsgBase):
    """
    It converts proxy messages into compatible messages.
    """

    def __init__(self, ofcapture_msg, pkt):
        """

        Args:
            ofcapture_msg (src.ofcapture.util.packet.OFMsg) : openflow message
            pkt: scapy packet data
        """
        super(MsgForOFMsg, self).__init__(pkt=pkt, timestamp=ofcapture_msg.timestamp)
        self.ofcapture_msg = ofcapture_msg
        # Packet inではin_portは使わないので，Packet outようにcontrollerにしている
        self.in_port = PortNo.OFPP_CONTROLLER
        # todo: 後で変える
        self.in_phy_port = "lo"

    @property
    def sniff_timestamp(self):
        return self.ofcapture_msg.timestamp

    @property
    def of_msg(self):
        """

        Returns:
            src.ofcapture.util.packet.OFMsg
        """
        return self.ofcapture_msg.of_msg

    @property
    def message_type(self):
        """OpenFlow Message Type"""
        return self.ofcapture_msg.message_type

    @property
    def eth_dst(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.l2.html#scapy.layers.l2.Ether
        """
        if self._properties["eth_dst"]:
            return self._properties["eth_dst"]
        if Ether in self.pkt:
            return self.pkt[Ether].dst
        else:
            return None

    @property
    def eth_src(self):
        if self._properties["eth_src"]:
            return self._properties["eth_src"]
        if Ether in self.pkt:
            return self.pkt[Ether].src
        else:
            return None

    @property
    def eth_type(self):
        if self._properties["eth_type"]:
            return self._properties["eth_type"]
        if Ether in self.pkt:
            return format(self.pkt[Ether].type, '#010x')
        else:
            return None

    @property
    def vlan_vid(self):
        if self._properties["vlan_vid"]:
            return self._properties["vlan_vid"]
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
        if self._properties["vlan_pcp"]:
            return self._properties["vlan_pcp"]
        if Dot1Q in self.pkt:
            return self.pkt[Dot1Q].prio
        if Dot1AD in self.pkt:
            return self.pkt[Dot1AD].prio
        else:
            return None

    @property
    def ip_dscp(self):
        if self._properties["ip_dscp"]:
            return self._properties["ip_dscp"]
        if IP in self.pkt:
            return self.pkt[IP].tos & 0b11111100
        else:
            return None

    @property
    def ip_ecn(self):
        if self._properties["ip_ecn"]:
            return self._properties["ip_ecn"]
        if IP in self.pkt:
            return self.pkt[IP].tos & 0b00000011
        else:
            return None

    @property
    def ip_proto(self):
        if self._properties["ip_proto"]:
            return self._properties["ip_proto"]
        if IP in self.pkt:
            return self.pkt[IP].proto
        else:
            return None

    @property
    def ipv4_src(self):
        if self._properties["ipv4_src"]:
            return self._properties["ipv4_src"]
        if IP in self.pkt:
            return self.pkt[IP].src
        else:
            return None

    @property
    def ipv4_dst(self):
        if self._properties["ipv4_dst"]:
            return self._properties["ipv4_dst"]
        if IP in self.pkt:
            return self.pkt[IP].dst
        else:
            return None

    @property
    def tcp_src(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet.html#scapy.layers.inet.TCP
        """
        if self._properties["tcp_src"]:
            return self._properties["tcp_src"]
        if TCP in self.pkt:
            return self.pkt[TCP].sport
        else:
            return None

    @property
    def tcp_dst(self):
        if self._properties["tcp_dst"]:
            return self._properties["tcp_dst"]
        if TCP in self.pkt:
            return self.pkt[TCP].dport
        else:
            return None

    @property
    def udp_src(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet.html#scapy.layers.inet.UDP
        """
        if self._properties["udp_src"]:
            return self._properties["udp_src"]
        if UDP in self.pkt:
            return self.pkt[UDP].sport
        else:
            return None

    @property
    def udp_dst(self):
        if self._properties["udp_dst"]:
            return self._properties["udp_dst"]
        if UDP in self.pkt:
            return self.pkt[UDP].dport
        else:
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
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet.html#scapy.layers.inet.ICMP
        """
        if self._properties["icmpv4_type"]:
            return self._properties["icmpv4_type"]
        if ICMP in self.pkt:
            return self.pkt[ICMP].type
        else:
            return None

    @property
    def icmpv4_code(self):
        if self._properties["icmpv4_code"]:
            return self._properties["icmpv4_code"]
        if ICMP in self.pkt:
            return self.pkt[ICMP].code
        else:
            return None

    @property
    def arp_op(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.l2.html#scapy.layers.l2.ARP
        """
        if self._properties["arp_op"]:
            return self._properties["arp_op"]
        if ARP in self.pkt:
            return self.pkt[ARP].op
        else:
            return None

    @property
    def arp_spa(self):
        if self._properties["arp_spa"]:
            return self._properties["arp_spa"]
        if ARP in self.pkt:
            return self.pkt[ARP].psrc
        else:
            return None

    @property
    def arp_tpa(self):
        if self._properties["arp_tpa"]:
            return self._properties["arp_tpa"]
        if ARP in self.pkt:
            return self.pkt[ARP].pdst
        else:
            return None

    @property
    def arp_sha(self):
        if self._properties["arp_sha"]:
            return self._properties["arp_sha"]
        if ARP in self.pkt:
            return self.pkt[ARP].hwsrc
        else:
            return None

    @property
    def arp_tha(self):
        if self._properties["arp_tha"]:
            return self._properties["arp_tha"]
        if ARP in self.pkt:
            return self.pkt[ARP].hwdst
        else:
            return None

    @property
    def ipv6_src(self):
        """
        https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet6.html#scapy.layers.inet6.IPv6
        """
        if self._properties["ipv6_src"]:
            return self._properties["ipv6_src"]
        if IPv6 in self.pkt:
            return self.pkt[IPv6].src
        else:
            return None

    @property
    def ipv6_dst(self):
        if self._properties["ipv6_dst"]:
            return self._properties["ipv6_dst"]
        if IPv6 in self.pkt:
            return self.pkt[IPv6].dst
        else:
            return None

    @property
    def ipv6_flabel(self):
        if self._properties["ipv6_flabel"]:
            return self._properties["ipv6_flabel"]
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
        if self._properties["icmpv6_type"]:
            return self._properties["icmpv6_type"]
        for layer in self.pkt.layers():
            if isinstance(layer, _ICMPv6):
                return layer.type
        return None

    @property
    def icmpv6_code(self):
        if self._properties["icmpv6_code"]:
            return self._properties["icmpv6_code"]
        for layer in self.pkt.layers():
            if isinstance(layer, _ICMPv6):
                return layer.code
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
        pass

    def __repr__(self):
        return "<{} (timestamp={} message_type={})>".format(self.__class__.__name__, self.timestamp, self.message_type)


def create_MsgForOFMsg(ofmsg):
    if ofmsg.message_type == Type.OFPT_PACKET_OUT or \
            ofmsg.message_type == Type.OFPT_PACKET_IN:
        pkt = Ether(_pkt=ofmsg.of_msg.data.value)
        net_msg = MsgForOFMsg(ofmsg, pkt)
        return net_msg
    else:
        raise TypeError


if __name__ == '__main__':
    test_data1 = b'33\x00\x00\x00\xfb\xbeS\xb1!\xed9\x86\xdd`\x00N(\x005\x11\xff\xfe\x80\x00\x00\x00\x00\x00\x00\xbcS\xb1\xff\xfe!\xed9\xff\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x14\xe9\x14\xe9\x005|\t\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x05_ipps\x04_tcp\x05local\x00\x00\x0c\x00\x01\x04_ipp\xc0\x12\x00\x0c\x00\x01'
    test_data2 = b'33\x00\x00\x00\x02\xb2\xcd\xdd\xe1\x87\x17\x86\xdd`\x00\x00\x00\x00\x10:\xff\xfe\x80\x00\x00\x00\x00\x00\x00\xb0\xcd\xdd\xff\xfe\xe1\x87\x17\xff\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x85\x00O\xa0\x00\x00\x00\x00\x01\x01\xb2\xcd\xdd\xe1\x87\x17'
    test_data3 = b'33\x00\x00\x00\x02\xe6\xaa*xNX\x86\xdd`\x00\x00\x00\x00\x10:\xff\xfe\x80\x00\x00\x00\x00\x00\x00\xe4\xaa*\xff\xfexNX\xff\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x85\x00\xc07\x00\x00\x00\x00\x01\x01\xe6\xaa*xNX'
    test_data4 = b'\xff\xff\xff\xff\xff\xff\xb2\xcd\xdd\xe1\x87\x17\x08\x06\x00\x01\x08\x00\x06\x04\x00\x01\xb2\xcd\xdd\xe1\x87\x17\n\x00\x00\x01\x00\x00\x00\x00\x00\x00\n\x00\x00\x02'
    test_data5 = b'\xb2\xcd\xdd\xe1\x87\x17\xe6\xaa*xNX\x08\x06\x00\x01\x08\x00\x06\x04\x00\x02\xe6\xaa*xNX\n\x00\x00\x02\xb2\xcd\xdd\xe1\x87\x17\n\x00\x00\x01'
    test_set = [test_data1, test_data2, test_data3, test_data4, test_data5]
    for data in test_set:
        net_msg = MsgForOFMsg(None, Ether(_pkt=data))
        print(net_msg.get_openflow_properties())

    pkt = Ether(_pkt=test_data1)
    print(Ether in pkt)
    print(IPv6 in pkt)
    print(pkt[IPv6].src)
