import datetime
import yaml
import copy
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from src.config import conf
from src.tracing_net.ofproto.table import FlowTables

setLoggerClass(Logger)
logger = getLogger('tracing_net.flowtable.table_repository')


class AbstractTableRepository(metaclass=ABCMeta):
    """Abstract Table Repository

    This temporarily stores the flow table.

    Attributes:
        repository (dict) : flow table repository
    """

    def __init__(self):
        self.repository = {}

    @abstractmethod
    def add(self, switch, new_table):
        """add flow table to repository

        Args:
            switch (str) : switch name
            new_table (FlowTable) :
        """
        raise NotImplementedError

    @abstractmethod
    def add_flow(self, datapath_id, switch, flow, timestamp=None):
        """add flow to current flow table

        Args:
            switch (str) :
            flow (Flow) :
        """
        raise NotImplementedError

    @abstractmethod
    def remove_flow(self, switch, flow, timestamp=None):
        """remove flow from current flow table

        Args:
            switch (str) :
            flow (Flow) :
        """
        raise NotImplementedError

    @abstractmethod
    def pop(self, switch, until=None, count=None):
        """

        Args:
            switch (str) : target switch name
            until (float) : unix timestamp
            count (int) : pop flow count

        Returns:
            list[FlowTable] : flow tables
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, switch, at_time=None):
        """

        Args:
            switch (str) : target switch name
            at_time (float) : unix timestamp

        Returns:
            list[FlowTable] : flow tables
        """
        raise NotImplementedError


class TableRepository(AbstractTableRepository):
    """Table Repository"""

    def __init__(self):
        super(TableRepository, self).__init__()

    def add(self, switch, new_table):
        self.repository.setdefault(switch, [])
        if self._is_new_table(switch, new_table):
            self.repository[switch].append(new_table)
            if conf.OUTPUT_FLOW_TABLE_UPDATE_TO_LOGFILE:
                logger.debug("flow table update to new_table={} on switch = {}".format(new_table, switch))

    def _is_new_table(self, switch, new_table):
        """Is not the new_table different from last entry of repository"""
        if len(self.repository[switch]) > 0 and self.repository[switch][-1] == new_table:
            return False
        else:
            return True

    def add_flow(self, datapath_id, switch, flow, timestamp=None):
        flow_tables = self.repository.setdefault(switch, [])
        if len(flow_tables) == 0:
            flow_table = FlowTables(datapath_id, switch, timestamp, flows=[flow])
            self.repository[switch].append(flow_table)
            return

        if timestamp is None:
            last_table: FlowTables = self.repository[switch][-1]
            new_table = copy.deepcopy(last_table)
            new_table.timestamp = datetime.datetime.now().timestamp()
            new_table.add(flow)
        else:
            for i in range(len(self.repository[switch])):
                if self.repository[switch][i].timestamp > timestamp:
                    new_table = copy.deepcopy(self.repository[switch][i])
                    new_table.timestamp = timestamp
                    new_table.add(flow)
                    self.repository[switch].insert(i+1, new_table)

    def remove_flow(self, switch, flow, timestamp=None):
        if timestamp is None:
            last_table: FlowTables = self.repository[switch][-1]
            new_table = copy.deepcopy(last_table)
            new_table.timestamp = datetime.datetime.now().timestamp()
            new_table.delete(flow)
        else:
            for i in range(len(self.repository[switch])):
                if self.repository[switch][i].timestamp > timestamp:
                    new_table = copy.deepcopy(self.repository[switch][i])
                    new_table.timestamp = timestamp
                    new_table.delete(flow)
                    self.repository[switch].insert(i+1, flow)

    def pop(self, switch, until=None, count=None):
        """

        Args:
            switch:
            until:
            count:

        Returns:
            list or None : まだフローテーブルが取得できていない状況だとNone
        """
        try:
            if until is not None:
                return self._pop_until(switch, until)
            elif count is not None:
                return self._pop_count(switch, count)
            else:
                return self._pop(switch)
        except KeyError:
            logger.error("Failed to pop from table repository (repo={})".format(self.repository))
            return None

    def _pop(self, switch):
        return self.repository.pop(switch)

    def _pop_until(self, switch, until):
        tmp_i = []
        tables = self.repository[switch]
        for i in range(len(tables)):
            if tables[i].timestamp < until:
                tmp_i.append(i)
        tmp = []
        for i in tmp_i[::-1]:
            tmp.insert(0, tables.pop(i))
        return tmp

    def _pop_count(self, switch, count):
        tmp_i = []
        tables = self.repository[switch]
        for i in range(min(len(tables), count)):
            tmp_i.append(i)
        tmp = []
        for i in tmp_i[::-1]:
            tmp.insert(0, tables.pop(i))
        return tmp

    def get(self, switch, at_time=None):
        try:
            if at_time:
                for t in self.repository[switch][::-1]:
                    if t.timestamp > at_time:
                        pass
                    else:
                        return t
            else:
                if len(self.repository[switch]) > 0:
                    return self.repository[switch][-1]
                else:
                    return None
        except KeyError:
            return None

    def output(self):
        """repository output to file"""
        file_name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + "-" + "flowtable" + ".yaml"
        file_path = conf.FLOWTABLES_DIRECTORY + file_name
        with open(file_path, 'w') as f:
            repo_dict = {"switches": []}
            for switch, flow_tables in self.repository.items():
                repo_dict["switches"].append({
                    "switch": switch,
                    "flow_tables": [flow_table.to_dict() for flow_table in flow_tables]
                })
            f.write(yaml.dump(repo_dict))


table_repository = TableRepository()
