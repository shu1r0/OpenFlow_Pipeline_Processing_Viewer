"""
This is a module for Open vSwitch flow.

TODO:
  * implement parse flow monitor
"""

import re
from logging import getLogger, setLoggerClass, Logger

from src.tracing_net.ofproto import action, instruction
from src.tracing_net.ofproto.match import Match
from src.tracing_net.ofproto.table import Flow


setLoggerClass(Logger)
logger = getLogger('tracing_net.ovs_flow')

# FLOW ENTRY ELEMENTS
# The words appear in the ovs ctl result in OVS.
# word : regular expression
OVS_FLOW_OUTPUT = {
    'table': r'table=(?P<table>\w+)',
    'duration': r'duration=(?P<duration>[\w.]+)s',
    'n_packets': r'n_packets=(?P<n_packets>\w*)',
    'n_bytes': r'n_bytes=(?P<n_bytes>\w+)',
    'actions': r'actions=(?P<actions>[\w,./\->=:;()"]+)',
    'cookie': r'cookie=(?P<cookie>\w+)',
    'priority': r'priority=((?P<priority>\w*)(,(?P<match>[\w,./\->=:;()"]*))?)',
    'idle_timeout': r'idle_timeout=(?P<idle_timeout>\w+)',
    'hard_timeout': r'hard_timeout=(?P<hard_timeout>\w+)',
    'idle_age': r'idle_timeout=(?P<idle_age>\w+)',
    'hard_age': r'hard_timeout=(?P<hard_age>\w+)',
    'importance': r'importance=(?P<importance>\w+)',
    # flags
    'send_flow_rem': r'(?P<send_flow_rem>send_flow_rem)',
    'check_overlap': r'(?P<check_overlap>check_overlap)',
    'reset_counts': r'(?P<reset_counts>reset_counts)',
    'no_packet_counts': r'(?P<no_packet_counts>no_packet_counts)',
    'no_byte_counts': r'(?P<no_byte_counts>no_byte_counts)',
    'out_port': r'out_port=(?P<out_port>\w+)',
    'out_group': r'out_group=(?P<out_group>=\w+)'
}
# ovs-ofctl result
re_flow_entry = OVS_FLOW_OUTPUT['cookie'] + r'[\s,.]+' \
                + OVS_FLOW_OUTPUT['duration'] + r'[\s,.]+' \
                + OVS_FLOW_OUTPUT['table'] + r'[\s,.]+' \
                + OVS_FLOW_OUTPUT['n_packets'] + r'[\s,.]+' \
                + OVS_FLOW_OUTPUT['n_bytes'] + r'[\s,.]+' \
                + '[' + OVS_FLOW_OUTPUT['send_flow_rem'] + r'[\s,.]+' + ']*' \
                + OVS_FLOW_OUTPUT['priority'] + r'[\s,.]+' \
                + OVS_FLOW_OUTPUT['actions']

re_flow_monitor = r'event=(?P<event>\w+)' + r'[\s,.]+' \
                + OVS_FLOW_OUTPUT['table'] + r'[\s,.]+' \
                + OVS_FLOW_OUTPUT['cookie'] + r'[\s,.]+' \
                + '(' + r'(?P<match>[\w,./\->=:;()"]*)' + r'[\s,.]+' + ')?' \
                + OVS_FLOW_OUTPUT['actions']


# link: https://man7.org/linux/man-pages/man7/ovs-actions.7.html
# Actions can be taken with OVS.
# The parser converts the action into an object
# and takes the value obtained from the regular expression as an argument.
OVS_ACTIONS = {
    'drop': {
        're': 'drop',
        'parser': action.ActionDrop.parser
    },
    'output': {
        're': r'((?P<port1>(^\d+|in_port|local)+)|output:"?(?P<port2>[\w\-]+)"?)', #todo
        'parser': action.ActionOutput.parser
    },
    'controller': {
        're': r'(CONTROLLER:(?P<controller>\d+))',#todo
        'parser': action.ActionOutput.parser
    },
    'enqueue': {
        're': None,
        'parser': None
    },
    'bundle': {
        're': None,
        'parser': None
    },
    'group': {
        're': None,
        'parser': None
    },
    'strip_vlan': {
        're': r'strip_vlan',
        'parser': None
    },
    'pop_vlan': {
        're': r'pop_vlan',
        'parser': None
    },
    'push_vlan': {
        're': r'push_vlan:(?P<ethertype>\w+)',
        'parser': action.ActionPush.parser_vlan
    },
    'push_mpls': {
        're': r'push_mpls:(?P<ethertype>\w+)',
        'parser': action.ActionPush.parser_mpls
    },
    'pop_mpls': {
        're': r'pop_mpls:(?P<ethertype>\w+)',
        'parser': None
    },
    'encap': {
        're': None,
        'parser': None
    },
    'decap': {
        're': None,
        'parser': None
    },
    'set_field': {
        're': r'(set_field|load):((?P<value>[\w:.]*)(/(?P<mask>[\w:.]*))?->(?P<dst>[\w\[\].]+))',
        'parser': action.ActionSetField.parser
    },
    'move': {
        're': r'move:(?P<src>[\w:.]*->(?P<dst>[\w:.]))',
        'parser': None
    },
    'mod_dl_src': {
        're': r'mod_dl_src:(?P<mac>[\w:]+)',
        'parser': None
    },
    'mod_dl_dst': {
        're': r'mod_dl_dst:(?P<mac>[\w:]+)',
        'parser': None
    },
    'mod_nw_src': {
        're': r'mod_nw_src:(?P<ip>[\w.]+)',
        'parser': None
    },
    'mod_nw_dst': {
        're': r'mod_nw_dst:(?P<ip>[\w.]+)',
        'parser': None
    },
    'mod_nw_tos': {
        're': r'mod_nw_tos:(?P<tos>[\w]+)',
        'parser': None
    },
    'mod_nw_ecn': {
        're': r'mod_nw_ecn:(?P<ecn>[\w]+)',
        'parser': None
    },
    'mod_tp_src': {
        're': r'mod_tp_src:(?P<port>[\w]+)',
        'parser': None
    },
    'mod_tp_dst': {
        're': r'mod_tp_dst:(?P<port>[\w]+)',
        'parser': None
    },
    'dec_ttl': {
        're': r'dec_ttl(\((?P<id>[\w,]*)\))',
        'parser': None
    },
    'set_mpls_label': {
        're': None,
        'parser': None
    },
    'set_mpls_tc': {
        're': None,
        'parser': None
    },
    'set_mpls_ttl': {
        're': None,
        'parser': None
    },
    'dec_mpls_ttl': {
        're': None,
        'parser': None
    },
    'dec_nsh_ttl': {
        're': None,
        'parser': None
    },
    'check_pkt_larger': {
        're': None,
        'parser': None
    },
    'set_tunnel': {
        're': None,
        'parser': None
    },
    'set_tunnel64': {
        're': None,
        'parser': None
    },
    'set_queue': {
        're': None,
        'parser': None
    },
    'pop_queue': {
        're': None,
        'parser': None
    },
    'ct': {
        're': None,
        'parser': None
    },
    'ct_clear': {
        're': None,
        'parser': None
    },
    'fin_timeout': {
        're': None,
        'parser': None
    },
    'learn': {
        're': None,
        'parser': None
    },
    'resubmit': {
        're': r'resubmit[(:](?P<port>\w+)?,(?P<table>\w+)?(,(?P<ct>\w+))?\)?',
        'parser': None
    },
    'clone': {
        're': None,
        'parser': None
    },
    'push': {
        're': None,
        'parser': None
    },
    'pop': {
        're': None,
        'parser': None
    },
    'exit': {
        're': r'exit',
        'parser': None
    },
    'multipath': {
        're': None,
        'parser': None
    },
    'conjunction': {
        're': None,
        'parser': None
    },
    'note': {
        're': None,
        'parser': None
    },
    'sample': {
        're': None,
        'parser': None
    },
}

# openflow instructions
OVS_INSTRUCTIONS = {
    'meter': {
        're': None,
        'parser': instruction.InstructionMeter.parser
        },
    'apply_actions': {
        're': None,  # No explicitly written in OVS.
        'parser': instruction.InstructionApplyAction.parser
        },
    'clear_actions': {
        're': r'clear_actions',
        'parser': instruction.InstructionClearAction.parser
        },
    'write_actions': {
        're': r'write_actions\((?P<actions>[\w,./\->=:;()"]+)\)',
        'parser': instruction.InstructionWriteAction.parser
        },
    'write_metadata': {
        're': r'write_metadata:(?P<metadata>\w+)(/(?P<mask>\w+))',
        'parser': instruction.InstructionWriteMetadata.parser
        },
    'stat_trigger': {
        're': None,
        'parser': None
        },
    'goto_table': {
        're': r'goto_table:(?P<table>\w+)',
        'parser': instruction.InstructionGotoTable.parser
        }
}

# omitted symbols
OVS_MATCH_ETH = {
    # "eth": "packet_type=(0,0)", #todo
    "ip": "eth_type=0x0800",
    'ipv6': 'eth_type=0x86dd',
    'icmp': 'eth_type=0x0800,ip_proto=1',
    'icmp6': 'eth_type=0x86dd,ip_proto=58',
    'tcp': 'eth_type=0x0800,ip_proto=6',
    'tcp6': 'eth_type=0x86dd,ip_proto=6',
    'udp': 'eth_type=0x0800,ip_proto=17',
    'udp6': 'eth_type=0x86dd,ip_proto=17',
    'sctp': 'eth_type=0x0800,ip_proto=132',
    'sctp6': 'eth_type=0x86dd,ip_proto=132',
    'arp': 'eth_type=0x0806',
    'rarp': 'eth_type=0x8035',
    'mpls': 'eth_type=0x8847',
    'mplsm': 'eth_type=0x8848'
}


def parse_actions(actions):
    re_action_entry = r'[^,()]+\([^()]*\)|[^,()]+'
    actions_list = re.findall(re_action_entry, actions)
    obj_actions = []
    re_actions = {}
    re_actions.update(**OVS_INSTRUCTIONS, **OVS_ACTIONS)

    for action in actions_list:
        for key, value in re_actions.items():  # value is re and parser
            # action match
            match = re.search(value['re'], action) if value['re'] else None
            if match is not None:
                params = match.groupdict()
                if key == 'write_actions':
                    params = parse_actions(params['actions'])
                # convert the action into an object
                if value['parser']:
                    parser = value['parser']
                    if isinstance(params, dict):
                        obj_actions.append(parser(**params))
                    elif isinstance(params, list):  # action list. e.g.) write_actions
                        obj_actions.append(parser(params))
                    else:  # no params actions
                        obj_actions.append(parser())
                else:
                    logger.warning("no parser (action: {})".format(key))
                break
    return obj_actions


# openflow properties
convert_match_key = {
    "nw_dst": "ipv4_dst",
    "nw_src": "ipv4_src"
}

def match_to_obj(match):
    """

    Args:
        match:

    Returns:
        list
    """
    list_match = match.split(',')
    list_match_obj = []
    # omitted words
    for i in range(len(list_match)):
        if list_match[i] in OVS_MATCH_ETH.keys():
            ovs_m = OVS_MATCH_ETH[list_match[i]].split(',')
            list_match.pop(i)
            for o in ovs_m:
                list_match.append(o)

    for m in list_match:
        key, value = m.split('=')
        if value[0] == '"':
            value = value[1:-1]
        value = value.split('/')
        if key in convert_match_key.keys():
            key = convert_match_key[key]
        obj_match = Match(field_name=key)
        if len(value) == 1:
            obj_match.value = _value_to_int(value[0])
        else:
            obj_match.value = _value_to_int(value[0])
            obj_match.mask = value[1]
        list_match_obj.append(obj_match)

    return list_match_obj


def _value_to_int(value):
    if isinstance(value, str):
        if value.isdigit():
            return int(value)
    return value


def parse_dump_flow(output_flow):
    """parse a flow of ovs-ofctl dump-flows result

    Args:
        output_flow (str) : ovs-ofctl dump-flow

    Returns:
        dict
    """
    m = re.search(re_flow_entry, output_flow)
    if m:
        dict_entry = m.groupdict()
        if 'actions' in dict_entry.keys():
            if dict_entry['actions']:
                actions = parse_actions(dict_entry['actions'])
                action_list = []
                instructions = []
                for a in actions:
                    if not isinstance(a, instruction.Instruction):
                        action_list.append(a)
                    else:
                        instructions.append(a)
                apply_actions_parser = OVS_INSTRUCTIONS['apply_actions']['parser']
                if len(action_list) > 0:
                    dict_entry['actions'] = [apply_actions_parser(action_list)] + instructions
                else:
                    dict_entry['actions'] = instructions
        if 'match' in dict_entry.keys():
            if dict_entry['match']:
                dict_entry['match'] = match_to_obj(dict_entry['match'])
            else:
                dict_entry['match'] = {}  # all match
        return dict_entry
    else:
        raise Exception("False to parse flow entry")


def parse_dump_flows(flows):
    """ovs-ofctl dump-flows result parser

    Args:
        flows (list[str]) : ovs-ofctl dump-flows

    Returns:
        list[Flow] :

    TODO:
        * fix example

    Examples:
        result = ['cookie=0x0, duration=12.851s, table=0, n_packets=21, n_bytes=1571, priority=0 actions=goto_table:5',
               ' cookie=0x0, duration=12.841s, table=5, n_packets=8, n_bytes=372, priority=1,arp actions=goto_table:10',
               ' cookie=0x0, duration=12.841s, table=5, n_packets=9, n_bytes=882, priority=1,ip actions=goto_table:20',
               ' cookie=0x0, duration=12.841s, table=10, n_packets=2, n_bytes=84, priority=1,arp,in_port="s1-eth1",arp_tpa=192.168.1.1,arp_op=1 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=10, n_packets=4, n_bytes=168, priority=1,arp,in_port="s1-eth1",arp_tpa=192.168.1.1,arp_op=2 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=10, n_packets=1, n_bytes=60, priority=1,arp,in_port="s1-eth2",arp_tpa=192.168.2.1,arp_op=1 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=10, n_packets=1, n_bytes=60, priority=1,arp,in_port="s1-eth2",arp_tpa=192.168.2.1,arp_op=2 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=20, n_packets=0, n_bytes=0, priority=58364,ip,nw_dst=192.168.2.0/24 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=20, n_packets=4, n_bytes=392, priority=58364,ip,nw_dst=192.168.1.0/24 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=20, n_packets=5, n_bytes=490, priority=58360,ip,nw_dst=192.168.3.0/24 actions=write_actions(output:"s1-eth2"),write_metadata:0xc0a80202/0xffffffff,goto_table:30',
               ' cookie=0x0, duration=12.841s, table=20, n_packets=0, n_bytes=0, priority=0 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=9.481s, table=30, n_packets=3, n_bytes=294, priority=16,ip,metadata=0xc0a80202/0xffffffff actions=set_field:1e:2c:3d:36:ff:3d->eth_src,set_field:2a:0c:db:9c:46:e5->eth_dst,goto_table:100',
               ' cookie=0x0, duration=3.820s, table=30, n_packets=0, n_bytes=0, priority=16,ip,metadata=0xc0a80102/0xffffffff actions=set_field:2a:5d:49:62:93:9f->eth_src,set_field:fa:bc:93:fb:5c:d0->eth_dst,goto_table:100',
               ' cookie=0x0, duration=12.841s, table=30, n_packets=2, n_bytes=196, priority=0,ip actions=CONTROLLER:65509,clear_actions',
               ' cookie=0x0, duration=12.841s, table=100, n_packets=3, n_bytes=294, priority=0 actions=drop']
        pased_result = parse_dump_flows(result)
        print(parsed_result)
        [<Flow(table=0, priority=0, match={}, actions=[<InstructionApplyAction type=4>, <InstructionGotoTable type=1>])>,
        <Flow(table=5, priority=1, match={'eth_type': {'value': '0x0806', 'mask': None}}, actions=[<InstructionApplyAction type=4>, <InstructionGotoTable type=1>])>,
        <Flow(table=5, priority=1, match={'eth_type': {'value': '0x0800', 'mask': None}}, actions=[<InstructionApplyAction type=4>, <InstructionGotoTable type=1>])>,
        <Flow(table=10, priority=1, match={'in_port': {'value': 's1-eth1', 'mask': None}, 'arp_tpa': {'value': '192.168.1.1', 'mask': None}, 'arp_op': {'value': 1, 'mask': None}, 'eth_type': {'value': '0x0806', 'mask': None}}, actions=[<InstructionApplyAction type=4>])>,
        <Flow(table=10, priority=1, match={'in_port': {'value': 's1-eth1', 'mask': None}, 'arp_tpa': {'value': '192.168.1.1', 'mask': None}, 'arp_op': {'value': 2, 'mask': None}, 'eth_type': {'value': '0x0806', 'mask': None}}, actions=[<InstructionApplyAction type=4>])>,
        <Flow(table=10, priority=1, match={'in_port': {'value': 's1-eth2', 'mask': None}, 'arp_tpa': {'value': '192.168.2.1', 'mask': None}, 'arp_op': {'value': 1, 'mask': None}, 'eth_type': {'value': '0x0806', 'mask': None}}, actions=[<InstructionApplyAction type=4>])>,
        <Flow(table=10, priority=1, match={'in_port': {'value': 's1-eth2', 'mask': None}, 'arp_tpa': {'value': '192.168.2.1', 'mask': None}, 'arp_op': {'value': 2, 'mask': None}, 'eth_type': {'value': '0x0806', 'mask': None}}, actions=[<InstructionApplyAction type=4>])>,
        <Flow(table=20, priority=58364, match={'nw_dst': {'value': '192.168.2.0', 'mask': '24'}, 'eth_type': {'value': '0x0800', 'mask': None}}, actions=[<InstructionApplyAction type=4>])>,
        <Flow(table=20, priority=58364, match={'nw_dst': {'value': '192.168.1.0', 'mask': '24'}, 'eth_type': {'value': '0x0800', 'mask': None}}, actions=[<InstructionApplyAction type=4>])>,
        <Flow(table=20, priority=58360, match={'nw_dst': {'value': '192.168.3.0', 'mask': '24'}, 'eth_type': {'value': '0x0800', 'mask': None}}, actions=[<InstructionApplyAction type=4>, <InstructionWriteAction type=3>, <InstructionWriteMetadata type=2>, <InstructionGotoTable type=1>])>,
        <Flow(table=20, priority=0, match={}, actions=[<InstructionApplyAction type=4>])>,
        <Flow(table=30, priority=16, match={'metadata': {'value': '0xc0a80202', 'mask': '0xffffffff'}, 'eth_type': {'value': '0x0800', 'mask': None}}, actions=[<InstructionApplyAction type=4>, <InstructionGotoTable type=1>])>,
        <Flow(table=30, priority=16, match={'metadata': {'value': '0xc0a80102', 'mask': '0xffffffff'}, 'eth_type': {'value': '0x0800', 'mask': None}}, actions=[<InstructionApplyAction type=4>, <InstructionGotoTable type=1>])>,
        <Flow(table=30, priority=0, match={'eth_type': {'value': '0x0800', 'mask': None}}, actions=[<InstructionApplyAction type=4>, <InstructionClearAction type=5>])>,
        <Flow(table=100, priority=0, match={}, actions=[<InstructionApplyAction type=4>])>]
    """
    parsed_flows = []
    for f in flows:
        parsed_flow = parse_dump_flow(f)
        cookie = parsed_flow.get('cookie', '')
        duration = parsed_flow.get('duration', 0)
        table = parsed_flow.get('table', -1)
        n_packets = parsed_flow.get('n_packets', 0)
        n_bytes = parsed_flow.get('n_bytes', 0)
        priority = parsed_flow.get('priority', 0)
        match = parsed_flow.get('match', 0)
        actions = parsed_flow.get('actions', None)
        flow = Flow(cookie, duration, table, n_packets, n_bytes, priority, match, actions)
        parsed_flows.append(flow)
    return parsed_flows


def _parse_flow_monitor(result):
    m = re.search(re_flow_monitor, result)
    if m:
        dict_entry = m.groupdict()
        if 'actions' in dict_entry.keys():
            if dict_entry['actions']:
                actions = parse_actions(dict_entry['actions'])
                action_list = []
                instructions = []
                for a in actions:
                    if not isinstance(a, instruction.Instruction):
                        action_list.append(a)
                    else:
                        instructions.append(a)
                apply_actions_parser = OVS_INSTRUCTIONS['apply_actions']['parser']
                if len(action_list) > 0:
                    dict_entry['actions'] = [apply_actions_parser(action_list)] + instructions
                else:
                    dict_entry['actions'] = instructions
        if 'match' in dict_entry.keys():
            if dict_entry['match']:
                dict_entry['match'] = match_to_obj(dict_entry['match'])
            else:
                dict_entry['match'] = {}  # all match
        else:
            dict_entry['match'] = {}  # all match
        return dict_entry
    else:
        raise Exception("False to parse flow entry")


def parse_flow_monitor(result):
    """parse flow monitor result

    Args:
        result (str) :

    Returns:
        tuple(str, str, list) : tuple(event, xid, flow)

    TODO:
        * まだ移行しただけで，何も変えてない

    """
    result_list = result.split()
    if len(result_list) > 0 and result_list[0] == "NXST_FLOW_MONITOR":
        xid = re.search(r'0x\d', result_list[2]).group()
        return {"msg_type": result_list[0], "type": result_list[1], "xid": xid}
    elif len(result_list) > 0 and result_list[0].split("=")[0] == 'event':
        flow_dict = _parse_flow_monitor(result)
        # for r in result:
        #     r = r.split("=")
        #     if len(r) >= 2:
        #         flow_dict[r[0]] = r[1]
        return flow_dict
    else:
        return {'result': result}


if __name__ == '__main__':
    # result1 = ['cookie=0x0, duration=10.143s, table=0, n_packets=0, n_bytes=0, priority=0 actions=CONTROLLER:65535']
    result2 = [' cookie=0x100007a585b6f, duration=2.162s, table=0, n_packets=1, n_bytes=139, send_flow_rem priority=40000,dl_type=0x8942 actions=CONTROLLER:65535,clear_actions',
               ' cookie=0x100009465555a, duration=2.162s, table=0, n_packets=1, n_bytes=139, send_flow_rem priority=40000,dl_type=0x88cc actions=CONTROLLER:65535,clear_actions',
               ' cookie=0x10000ea6f4b8e, duration=2.162s, table=0, n_packets=0, n_bytes=0, send_flow_rem priority=40000,arp actions=CONTROLLER:65535,clear_actions']
    result3 = ['OFPST_FLOW reply (OF1.3) (xid=0x2):',
               ' cookie=0x100007a585b6f, duration=4.838s, table=0, n_packets=3, n_bytes=417, send_flow_rem priority=40000,dl_type=0x8942 actions=CONTROLLER:65535,clear_actions',
               ' cookie=0x10000ea6f4b8e, duration=4.837s, table=0, n_packets=0, n_bytes=0, send_flow_rem priority=40000,arp actions=CONTROLLER:65535,clear_actions',
               ' cookie=0x100009465555a, duration=4.837s, table=0, n_packets=3, n_bytes=417, send_flow_rem priority=40000,dl_type=0x88cc actions=CONTROLLER:65535,clear_actions']
    result4 = ['OFPST_FLOW reply (OF1.3) (xid=0x2):',
               ' cookie=0x0, duration=11.178s, table=0, n_packets=5, n_bytes=331, priority=0 actions=goto_table:5',
               ' cookie=0x0, duration=11.178s, table=5, n_packets=2, n_bytes=84, priority=1,arp actions=goto_table:10',
               ' cookie=0x0, duration=11.178s, table=5, n_packets=0, n_bytes=0, priority=1,ip actions=goto_table:20',
               ' cookie=0x0, duration=11.178s, table=10, n_packets=0, n_bytes=0, priority=1,arp,in_port=1,arp_tpa=192.168.1.1,arp_op=1 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=11.178s, table=10, n_packets=0, n_bytes=0, priority=1,arp,in_port=1,arp_tpa=192.168.1.1,arp_op=2 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=11.178s, table=10, n_packets=0, n_bytes=0, priority=1,arp,in_port=2,arp_tpa=192.168.2.1,arp_op=1 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=11.178s, table=10, n_packets=0, n_bytes=0, priority=1,arp,in_port=2,arp_tpa=192.168.2.1,arp_op=2 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=11.178s, table=20, n_packets=0, n_bytes=0, priority=58364,ip,nw_dst=192.168.2.0/24 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=11.178s, table=20, n_packets=0, n_bytes=0, priority=58364,ip,nw_dst=192.168.1.0/24 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=11.178s, table=20, n_packets=0, n_bytes=0, priority=58360,ip,nw_dst=192.168.3.0/24 actions=write_actions(output:2),write_metadata:0xc0a80202/0xffffffff,goto_table:30',
               ' cookie=0x0, duration=11.178s, table=20, n_packets=0, n_bytes=0, priority=0 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=11.178s, table=30, n_packets=0, n_bytes=0, priority=0,ip actions=CONTROLLER:65509,clear_actions',
               ' cookie=0x0, duration=11.178s, table=100, n_packets=0, n_bytes=0, priority=0 actions=drop']
    result5 = ['cookie=0x0, duration=12.851s, table=0, n_packets=21, n_bytes=1571, priority=0 actions=goto_table:5',
               ' cookie=0x0, duration=12.841s, table=5, n_packets=8, n_bytes=372, priority=1,arp actions=goto_table:10',
               ' cookie=0x0, duration=12.841s, table=5, n_packets=9, n_bytes=882, priority=1,ip actions=goto_table:20',
               ' cookie=0x0, duration=12.841s, table=10, n_packets=2, n_bytes=84, priority=1,arp,in_port="s1-eth1",arp_tpa=192.168.1.1,arp_op=1 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=10, n_packets=4, n_bytes=168, priority=1,arp,in_port="s1-eth1",arp_tpa=192.168.1.1,arp_op=2 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=10, n_packets=1, n_bytes=60, priority=1,arp,in_port="s1-eth2",arp_tpa=192.168.2.1,arp_op=1 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=10, n_packets=1, n_bytes=60, priority=1,arp,in_port="s1-eth2",arp_tpa=192.168.2.1,arp_op=2 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=20, n_packets=0, n_bytes=0, priority=58364,ip,nw_dst=192.168.2.0/24 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=20, n_packets=4, n_bytes=392, priority=58364,ip,nw_dst=192.168.1.0/24 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=12.841s, table=20, n_packets=5, n_bytes=490, priority=58360,ip,nw_dst=192.168.3.0/24 actions=write_actions(output:"s1-eth2"),write_metadata:0xc0a80202/0xffffffff,goto_table:30',
               ' cookie=0x0, duration=12.841s, table=20, n_packets=0, n_bytes=0, priority=0 actions=CONTROLLER:65509',
               ' cookie=0x0, duration=9.481s, table=30, n_packets=3, n_bytes=294, priority=16,ip,metadata=0xc0a80202/0xffffffff actions=set_field:1e:2c:3d:36:ff:3d->eth_src,set_field:2a:0c:db:9c:46:e5->eth_dst,goto_table:100',
               ' cookie=0x0, duration=3.820s, table=30, n_packets=0, n_bytes=0, priority=16,ip,metadata=0xc0a80102/0xffffffff actions=set_field:2a:5d:49:62:93:9f->eth_src,set_field:fa:bc:93:fb:5c:d0->eth_dst,goto_table:100',
               ' cookie=0x0, duration=12.841s, table=30, n_packets=2, n_bytes=196, priority=0,ip actions=CONTROLLER:65509,clear_actions',
               ' cookie=0x0, duration=12.841s, table=100, n_packets=3, n_bytes=294, priority=0 actions=drop']
    # pased = parse_dump_flows(result1)
    # print(pased)
    # pased = parse_dump_flows(result2)
    # print(pased)
    print(re_flow_entry)
    target = 'cookie=0x100009465555a, duration=2.162s, table=0, n_packets=1, n_bytes=139, send_flow_rem priority=40000,dl_type=0x88cc actions=CONTROLLER:65535,clear_actions'
    m = re.search(re_flow_entry, target)
    print(m.groupdict())
    for r in result2[1:]:
        print(parse_dump_flow(r))
    for r in result3[1:]:
        print(parse_dump_flow(r))
    for r in result4[1:]:
        print(parse_dump_flow(r))
    for r in result5[1:]:
        print(parse_dump_flow(r))
    print(parse_dump_flows(result5))
