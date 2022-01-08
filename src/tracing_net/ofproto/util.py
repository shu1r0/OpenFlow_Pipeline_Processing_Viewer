# import ipaddress
#
#
# def matching(m_value, m_mask, target_value, type="") -> bool:
#     if type == "ipv4":
#         if m_mask is None:
#             m_mask = "32"
#         ip_net = ipaddress.IPv4Network(str(m_value) + "/" + str(m_mask))
#         target_ip = ipaddress.IPv4Address(target_value)
#         return target_ip in ip_net
#     if type == "eth":
#         # todo
#
#
#
# def parse_value(value, type=""):
#     pass
#
#
# def digitable2int(digitable):
#     """
#
#     Args:
#         digitable:
#
#     Returns:
#     """
#     if isinstance(digitable, str):
#         if digitable.isdigit():
#             return int(digitable)
#         elif len(digitable) >= 2 and digitable[0:2] == "0b":
#             return int(digitable, 2)
#         elif len(digitable) >= 2 and digitable[0:2] == "0x":
#             return int(digitable, 16)
#         else:
#             return digitable
#     return digitable
#
#
# def ipv4address2str(byte, mask=True):
#     """
#
#     todo:
#         * ip address mask をどうにかする
#
#     Args:
#         byte:
#
#     Returns:
#         str
#     """
#     if(mask):
#         addr_net = ipaddress.IPv4Network(byte)
#         addr = str(addr_net.network_address)
#         pre = addr_net.prefixlen
#     else:
#         addr = ipaddress.IPv4Address(byte)
#         pre = None
#     return addr, pre
#
#
# def ipv6address2str(byte):
#     addr = ipaddress.IPv6Address(byte)
#     return str(addr)