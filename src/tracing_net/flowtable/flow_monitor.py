"""
Polling switch

TODO:
    * Implement a process for when a flow change event is received.
    * Design a new parser for flow monitor result.
"""

import subprocess
import re
import datetime
import signal
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from src.tracing_net.ofproto.ovs_flow import parse_dump_flows
from src.tracing_net.ofproto.table import FlowTables

setLoggerClass(Logger)
logger = getLogger('tracing_net.flowtable.flow_monitor')


class Poller(metaclass=ABCMeta):
    """フローをポーリングする基底クラス"""

    def __init__(self, repository):
        self.repository = repository

    @abstractmethod
    def start_poll(cls):
        """start polling"""
        raise NotImplementedError


class FlowMonitor(Poller):
    """
    フローテーブルをポーリングする
    """

    def __init__(self, switch, repository, event_loop=None):
        super().__init__(repository)
        logger.info("flow monitor start : {}".format(switch))
        self.switch = str(switch)
        self.event_loop = event_loop

    def start_poll(self):
        signal.signal(signal.SIGALRM, self.dump_flows)
        signal.setitimer(signal.ITIMER_REAL, 1, 1)
        self.flow_monitor()

    def dump_flows(self, *args):
        """exec dump flow command"""
        logger.debug("dump flows on {}".format(self.switch))
        dump_flows_cmd = "ovs-ofctl -O OpenFlow13 dump-flows " + self.switch
        # ['OFPST_FLOW reply (OF1.3) (xid=0x2):', ' cookie=0x0, duration=10.143s, table=0, n_packets=0, n_bytes=0, priority=0 actions=CONTROLLER:65535']
        dump_flows_popen = subprocess.Popen(dump_flows_cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        time_stamp = datetime.datetime.now().timestamp()
        self.read_dump_flow(time_stamp, dump_flows_popen)

    def read_dump_flow(self, time_stamp, popen):
        """parse dump flow and store to repository

        Args:
            time_stamp (float) :
            popen (Popen) :
        """
        popen.wait()
        result = popen.stdout.read().decode().strip().split('\n')
        logger.debug("get result for dump flow {} : {}".format(time_stamp, result))
        if len(result) >= 2:
            flows = parse_dump_flows(result[1:])
            table = FlowTables(switch_name=self.switch, timestamp=time_stamp, flows=flows)
            self.repository.add(self.switch, table)
            logger.debug("parsed result to table {} : {}".format(time_stamp, table))

    def flow_monitor(self):
        """flow monitor"""
        monitor_cmd = "ovs-ofctl monitor " + self.switch + " watch:"
        monitor_popen = subprocess.Popen(monitor_cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        while monitor_popen.poll() is None:
            monitor_result = monitor_popen.stdout.readline().decode().strip()
            monitor_result_dict = parse_flow_monitor(monitor_result)
            if 'event' in monitor_result_dict.keys():
                pass  # TODO: update flow table
            logger.debug("flow monitor get result {}".format(monitor_result_dict))
        logger.debug("flow monitor end returned is {}".format(str(monitor_popen.returncode)))


# # ovs_flow.pyに移行
# def parse_dump_flows(flows):
#     """parse ovs-ofctl dump-flows result
#
#     Args:
#         flows (str) : dump-flows
#
#     Returns:
#         list[Flow] : list of flows
#     """
#     parsed_flows = []
#     for flow in flows:
#         parsed_flow = Flow()
#         for entry in flow.strip().split():  # each element of the flow entry
#             # actions
#             if entry.find('actions') != -1:
#                 # to parse resubmit(,2) etc
#                 resubmit = re.search(r'resubmit\(*(\w,)\)', entry)
#                 if resubmit is not None:
#                     parsed_flow.actions.append(resubmit.group())
#                     entry = entry[:resubmit.start()] + entry[resubmit.end():]  # remove resubmit
#
#                 actions = entry.split('=')[1].split(',')
#                 for action in actions:
#                     parsed_flow.actions.append(action)
#             # priority and matching field
#             elif entry.find('priority') != -1:
#                 match = {}
#                 entry = entry.split(',')
#                 for e in entry:
#                     e = e.split('=')
#                     if e[0] == 'priority':
#                         parsed_flow.priority = e[1]
#                     else:
#                         if len(e) >= 2:
#                             match[e[0]] = e[1]
#                         else:
#                             # TODO: make sure it's really eth_type
#                             match['eth_type'] = e[0]
#                 parsed_flow.match = match
#             else:
#                 entry = entry.split(',')
#                 for e in entry:
#                     if e != '':
#                         e = e.split('=')
#                         if len(e) >= 2:
#                             setattr(parsed_flow, e[0], e[1])
#                         else:
#                             parsed_flow.other_options.append(e[0])
#         parsed_flows.append(parsed_flow)
#     return parsed_flows


def parse_flow_monitor(result):
    """parse flow monitor result

    Args:
        result (str) :

    Returns:
        tuple(str, str, list) : tuple(event, xid, flow)
    """
    result = result.split()
    if result[0] == "NXST_FLOW_MONITOR":
        xid = re.search(r'0x\d', result[2]).group()
        return {"msg_type": result[0], "type": result[1], "xid": xid}
    elif result[0].split("=")[0] == 'event':
        flow_dict = {}
        for r in result:
            r = r.split("=")
            if len(r) >= 2:
                flow_dict[r[0]] = r[1]
        return flow_dict
    else:
        return {'result': result}

#
# if __name__ == '__main__':
#     result1 = ['cookie=0x0, duration=10.143s, table=0, n_packets=0, n_bytes=0, priority=0 actions=CONTROLLER:65535']
#     result2 = [' cookie=0x100007a585b6f, duration=2.162s, table=0, n_packets=1, n_bytes=139, send_flow_rem priority=40000,dl_type=0x8942 actions=CONTROLLER:65535,clear_actions',
#                ' cookie=0x100009465555a, duration=2.162s, table=0, n_packets=1, n_bytes=139, send_flow_rem priority=40000,dl_type=0x88cc actions=CONTROLLER:65535,clear_actions',
#                ' cookie=0x10000ea6f4b8e, duration=2.162s, table=0, n_packets=0, n_bytes=0, send_flow_rem priority=40000,arp actions=CONTROLLER:65535,clear_actions']
#     pased = parse_dump_flows(result1)
#     print(pased)
#     pased = parse_dump_flows(result2)
#     print(pased)