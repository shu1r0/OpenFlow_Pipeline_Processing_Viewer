import datetime
import multiprocessing
import threading
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from .table_repository import table_repository
from .flow_monitor import FlowMonitor


setLoggerClass(Logger)
logger = getLogger('tracing_net.flowtable.flow_table_manager')


class AbstractFlowTableManager(metaclass=ABCMeta):
    """This class manages flow table pollers.
    Pollers periodically collects flow tables and stores them in the repository.

    Attributes:
        repository (FlowTableRepository) : repository
    """

    def __init__(self, repository):
        self.repository = repository

    @abstractmethod
    def start_poller(self, switch):
        """start polling switch

        Args:
            switch (str) :
        """
        raise NotImplementedError

    @abstractmethod
    def start_pollers(self, switches):
        """start polling switches

        Args:
            switches (list[str]) :
        """
        raise NotImplementedError

    @abstractmethod
    def stop_poller(self, switch):
        """stop polling

        Args:
            switch (str) :
        """
        raise NotImplementedError

    @abstractmethod
    def stop_all_poller(self):
        """stop polling all"""
        raise NotImplementedError

    @abstractmethod
    def is_polling(self, switch):
        """Is this polling switch?

        Args:
            switch (str) :
        """
        raise NotImplementedError


class FlowTableManager(AbstractFlowTableManager):
    """Flow Table Manager

    Attributes:
        event_loop (EventLoop) : event loop
        pollers (dict) : switch name to poller
    """

    def __init__(self, event_loop):
        super(FlowTableManager, self).__init__(table_repository)
        self.event_loop = event_loop
        self.pollers = {}

    def start_poller(self, switch):
        poller = self._create_poller(switch)
        poller.start()

    def start_pollers(self, switches):
        for switch in switches:
            self.start_poller(switch)

    def _create_poller(self, switch):
        parent_conn, child_conn = multiprocessing.Pipe()
        monitor = FlowMonitor(switch, parent_conn, event_loop=self.event_loop)
        p = multiprocessing.Process(target=monitor.start_poll)
        t = threading.Thread(target=self._receive_data, args=(child_conn,))
        t.start()
        p.daemon = True
        self.pollers[switch] = p
        return p

    def stop_poller(self, switch):
        self.pollers[switch].terminate()
        logger.debug("poller process ({}:{}) terminated".format(switch, self.pollers[switch].pid))

    def stop_all_poller(self):
        for switch in self.pollers.keys():
            self.stop_poller(switch)

    def is_polling(self, switch):
        raise NotImplementedError

    async def _receive_data(self, child_conn):
        while True:
            data = child_conn.recv()
            self.repository.add(*data)

#
# class FlowTablePoller():
#     pass

# class FlowTableManager():
#     """flow table manager for flow monitor"""
#
#     def __init__(self):
#         self.flow_table = FlowTable()
#         self.flow_table_archive = []
#         self.flow_table_max = 100
#
#     def add(self, flow, timestamp):
#         if self.flow_table.timestamp == timestamp:
#             self.flow_table.flows.append(flow)
#         else:
#             self.table_change(timestamp)
#             self.flow_table.flows.append(flow)
#
#     def delete(self, flow, timestamp):
#         if self.flow_table.timestamp == timestamp:
#             self.flow_table.flows.remove(flow)
#         else:
#             self.table_change(timestamp)
#             self.flow_table.flows.remove(flow)
#
#     def set_table(self, table):
#         if len(table['flows']) == len(table['flows']):
#
#
#     def get_table(self, table_id, at_time=None):
#         pass
#
#     def get_tables(self, at_time=None):
#         pass
#
#     def table_change(self, timestamp):
#         self.flow_table_archive.append(self.flow_table)
#         self.flow_table = self.flow_table.copy()
#         self.flow_table['timestamp'] = timestamp

