"""
Polling switch

TODO:
    * Implement a process for when a flow change event is received.
"""

import subprocess
import re
import datetime
import signal
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from src.config import conf
from src.tracing_net.ofproto.ovs_flow import parse_dump_flows, parse_flow_monitor
from src.tracing_net.ofproto.table import FlowTables

setLoggerClass(Logger)
logger = getLogger('tracing_net.flowtable.flow_monitor')


class Poller(metaclass=ABCMeta):
    """Base class for polling the flow

    Attributes:
        parent_conn (Connection) : parent_conn
    """

    def __init__(self, parent_conn):
        self.parent_conn = parent_conn

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
        logger.debug("exec dump flows on {}".format(self.switch))
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
        if conf.OUTPUT_DUMPFLOWS_TO_LOGFILE:
            logger.debug("get result for dump flows {} : {}".format(time_stamp, result))
        if len(result) >= 2:
            flows = parse_dump_flows(result[1:])
            table = FlowTables(switch_name=self.switch, timestamp=time_stamp, flows=flows)
            self.parent_conn.send([self.switch, table])
            if conf.OUTPUT_DUMPFLOWS_TO_LOGFILE:
                logger.debug("parsed dump flows result to table {} : {}".format(time_stamp, table))
        else:
            if conf.OUTPUT_DUMPFLOWS_TO_LOGFILE:
                logger.warning("No result dump flows")

    def flow_monitor(self):
        """flow monitor

        Returns:
              int : monitor popen return code
        """
        monitor_cmd = "ovs-ofctl monitor " + self.switch + " watch:"
        monitor_popen = subprocess.Popen(monitor_cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        while monitor_popen.poll() is None:
            monitor_result = monitor_popen.stdout.readline().decode().strip()
            monitor_result_dict = parse_flow_monitor(monitor_result)
            if 'event' in monitor_result_dict.keys():
                pass  # TODO: update flow table
            if conf.OUTPUT_FLOWMONITOR_TO_LOGFILE:
                logger.debug("flow monitor get result {}".format(monitor_result))
        return monitor_popen.returncode
