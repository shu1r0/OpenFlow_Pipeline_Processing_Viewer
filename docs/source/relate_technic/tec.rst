
===========
関連技術
===========

OpenFlow
==========

============ ====================================
fields       description
============ ====================================
in_port      Switch input port
in_phy_port  Switch phyical input port
metadata     Metadata passed between tables
eth_dst      Ethernet destination address
eth_src      Ethernet source address
eth_type     Ethernet frame type
vlan_vid     VLAN id
vlan_pcp     VLAN priority
ip_dscp      IP DSCP
ip_ecm       IP ECM
ip_proto     IP protocol
ipv4_src
ipv4_dst
tcp_src
tcp_dst
udp_src
udp_dst
sctp_src
sctp_dst
icmpv4_type
icmpv4_code
arp_op
arp_spa
arp_tpa
arp_sha
arp_tha
ipv6_src
ipv6_dst
ipv6_flabel
icmpv6_type
icmpv6_code
ipv6_nd_target
ipv6_nd_sll
ipv6_nd_tll
mpls_label
mpls_tc
mpls_bos
pbb_isid
tunnel_id
ipv6_exthdr




Flowtable
------------

* match fields, counters, instructions から成る
* Flowエントリのマッチについて
    Flow entries match packets in priority order,
    with the first matching entry in each table being used.