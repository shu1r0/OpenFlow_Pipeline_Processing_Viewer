from src.api.proto import net_pb2

from pyof.v0x04.common.flow_match import OxmMatchFields, OxmOfbMatchField, OxmTLV

import macaddress
import ipaddress

from src.tracing_net.ofproto.msg import digitable2int


class Match:
    """A OpenFlow Match Class


    TODO:
        * __eq__ を実装
    """

    def __init__(self, field_name=None, value=None, mask=None):
        self.field_name = field_name
        self.value = value if isinstance(value, int) else digitable2int(value)
        self.mask = mask

    @property
    def masked_value(self):
        """
           * IPアドレスのマスクをどう実装するか？？？
           * 値をどうするのか
        Returns:
            int or
        """
        raise NotImplementedError

    def is_match(self, value):
        """Does the value match?

        Returns:
            bool

        todo:
            mask
            * isdigitをどうにかする
        """
        if value is None:
            return False

        if self.field_name in ["ipv4_src", "ipv4_dst"]:
            if self.mask is None:
                self.mask = "32"
            ip_net = ipaddress.IPv4Network(str(self.value) + "/" + str(self.mask))
            target_ip = ipaddress.IPv4Address(value)
            return target_ip in ip_net
        elif self.field_name == "metadata":
            self.value = digitable2int(self.value)
            self.mask = digitable2int(self.mask)
            if self.mask:
                value1 = self.value & self.mask
                value2 = value & self.mask
                return value1 == value2
            else:
                return self.value == value
        else:
            value = digitable2int(value)
            self.value = digitable2int(self.value)
            return value == self.value

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.Match
        """
        match = net_pb2.Match()
        match.field_name = self.field_name
        match.value = str(self.value)
        match.mask = str(self.mask)
        return match

    def __repr__(self):
        return "<{}, {}/{}>".format(self.field_name, self.value, self.mask)

    @classmethod
    def parse_from_ofcapture(cls, of_match):
        """

        Args:
            of_match:

        Returns:
            list[Match]

        todo:
            * add match mask
        """
        matches = []
        for match_field in of_match.oxm_match_fields:
            match_field: OxmTLV = match_field
            oxm_field: OxmOfbMatchField = match_field.oxm_field
            if isinstance(oxm_field, OxmOfbMatchField):
                field_name = OxmOfbMatchField2stringfield(oxm_field)
                value = match_field.oxm_value  # todo これはbytes
                mask = None
                if not isinstance(value, bytes):
                    raise TypeError("expect bytes, but type = {}".format(type(value)))

                if field_name in ["eth_dst", "eth_src"]:
                    value = mac_address2str(value)
                elif field_name in ["ipv4_src", "ipv4_dst"]:
                    value, mask = ipv4address2str(value, mask=match_field.oxm_hasmask)
                elif field_name in ["ipv6_src", "ipv6_dst"]:
                    value = ipv6address2str(value)
                else:
                    value = int.from_bytes(value, byteorder="big")
                match = cls(field_name=field_name, value=value, mask=mask)
                matches.append(match)
        return matches


def OxmOfbMatchField2stringfield(oxm_field):
    oxm_field = OxmOfbMatchField(int(oxm_field))
    field_name = oxm_field.name[11:].lower()
    return field_name


def mac_address2str(byte):
    addr = macaddress.MAC(byte)
    return str(addr).replace('-', ':').lower()


def ipv4address2str(byte, mask=False):
    """

    todo:
        * ip address mask をどうにかする

    Args:
        byte:

    Returns:
        str
    """
    if mask:
        addr_mask = str(ipaddress.IPv4Address(byte[4:]))
        addr_net = ipaddress.IPv4Network((byte[:4], addr_mask))
        addr = str(addr_net.network_address)
        pre = addr_net.prefixlen
    else:
        addr = str(ipaddress.IPv4Address(byte))
        pre = None
    return addr, pre


def ipv6address2str(byte):
    addr = ipaddress.IPv6Address(byte)
    return str(addr)
