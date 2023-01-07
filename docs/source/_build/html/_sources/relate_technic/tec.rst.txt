
===========
関連技術
===========

SDN
=======
#. アーキテクチャの概要
#. ノースバンドインターフェースについて

OpenFlow
==========
#. OpenFlowコントローラとOpenFlowスイッチの通信を規定したプロトコル．
#. だれがいつ作ったか．
#. 当初の目的は
#. 特徴
#. メリット・デメリット
#. OpenFlowの動作

OpenFlowはコントローラプレーンとデータプレーンの通信を規定したプロトコルです．
実験ネットワークを容易に作成することを目的としてスタンフォード大学で開発されました．[1]
現在はOpen Networking Foudation (ONF) [] が主導となりOpenFlowの仕様が取りまとめられています．

OpenFlowでは，イーサネットアドレスやVLANタグ，IPアドレス，TCP/UDPポートなどのパケットの特徴を「フロー」として扱い，それらの特徴をベースに経路選択やパケットの特徴を書き換えたりすることで，柔軟にパケットを操作できます．


OpenFlowコントローラ
-------------------

OpenFlowスイッチ
-------------------

OpenFlowの動作
--------------
OpenFlowでは

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


Mininet
------------




