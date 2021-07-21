"""Flow Table Module"""
import datetime
from logging import getLogger, setLoggerClass, Logger

from src.tracing_net.ofproto.instruction import InstructionResult
from src.tracing_net.ofproto.msg import Msg


setLoggerClass(Logger)
logger = getLogger('tracing_net.table')


class Flow:

    def __init__(self, cookie="", duration=0, table=0, n_packets=0, n_bytes=0,
                 priority=0, match=None, actions=None):
        self.cookie = cookie
        self.duration = duration if isinstance(duration, int) else int(duration)
        self.table = table if isinstance(table, int) else int(table)
        self.n_packets = n_packets if isinstance(n_packets, int) else int(n_packets)
        self.n_bytes = n_bytes if isinstance(n_bytes, int) else int(n_bytes)
        # self.idle_age =
        self.priority = priority if isinstance(priority, int) else int(priority)
        self.match = match if match is not None else {}
        self.actions = actions if actions is not None else []
        self.other_options = []

    def is_match(self, msg):
        """Is msg matched?

        Args:
            msg (Msg) : message

        Returns:
            bool : Is the msg matched?

        Notes:
            * This is not an accurate way to determine matching.
            * It does not take into account the different types.
            * Bitmasking is not implemented.
            * In the future, match may be Match Class instead of dict
        """
        # logger.debug("called is matching")
        matched = True
        for match_key, match_values in self.match.items():
            # logger.debug("is match={} to msg={}?".format((match_key, match_values), msg))
            msg_value = getattr(msg, match_key, None)
            if msg_value != match_values['value']:
                logger.debug("no match key={} msg_value={} match_values={}".format(match_key, msg_value, match_values))
                matched = False
        return matched

    def action(self, msg, action_set):
        """apply action

        Args:
            msg (Msg) :
            action_set (ActionSet) :

        Returns:
            InstructionResult

        Notes:
            * Currently, it is just calculated.
            * In the future, we would like to obtain information on the computation in progress.
        """
        instruction_result = InstructionResult(msg=msg, action_set=action_set)
        for action in self.actions:
            temp_result = action.apply(msg=msg, action_set=action_set)
            instruction_result.out_ports.extend(temp_result.out_ports)
            instruction_result.table_id = temp_result.table_id
        return instruction_result

    def __lt__(self, other):
        if other is None or not isinstance(other, Flow):
            return False
        return self.priority < other.priority

    def __le__(self, other):
        if other is None or not isinstance(other, Flow):
            return False
        return self.priority <= other.priority

    def __eq__(self, other):
        if other is None or not isinstance(other, Flow):
            return False
        return self.match == other.match and self.priority == other.priority

    def __gt__(self, other):
        if other is None or not isinstance(other, Flow):
            return False
        return self.priority > other.priority

    def __ge__(self, other):
        if other is None or not isinstance(other, Flow):
            return False
        return self.priority >= other.priority

    def __repr__(self):
        return "<Flow(table={}, priority={}, match={}, actions={})>".format(self.table, self.priority, self.match, self.actions)


class FlowTables:
    """Flow table.
    This also computes the match.

    Attributes:
        datapath_id (int) : datapath id
        switch_name (str) : switch name
        timestamp (float) : unix time stamp
        flows (list) : list of flows
    """

    def __init__(self, datapath_id=0, switch_name=None, timestamp=None, flows=None):
        self.datapath_id = datapath_id
        self.switch_name = switch_name
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now().timestamp()
        self.flows: list[Flow] = flows if flows is not None else []
        self.flows.sort(reverse=True)

    def add(self, flow: Flow):
        """add flow

        Args:
            flow (Flow) : flow entry
        """
        if not isinstance(flow, Flow):
            raise TypeError
        is_inserted = False
        for i in range(len(self.flows)):
            if flow > self.flows[i]:
                self.flows.insert(i, flow)
                is_inserted = True
                break
        if not is_inserted:
            self.flows.append(flow)

    def delete(self, flow: Flow):
        """delete flow

        Args:
            flow (Flow) : flow entry
        """
        if not isinstance(flow, Flow):
            raise TypeError
        self.flows.remove(flow)

    def get(self, table_id: int):
        """get flow table

        Args:
            table_id (int) : table id

        Returns:
            list[Flow] : flow table
        """
        table = []
        for flow in self.flows:
            if int(flow.table) == int(table_id):
                table.append(flow)
            # else:
            #     logger.debug("flow entry not match {} {}".format(type(flow.table), table_id))
        return table

    def match(self, msg: Msg, table_id: int):
        """Returns the matched flow.
        Whether or not the message is matched depends on ``Flow.is_match`` function.

        Args:
            msg (Msg) :
            table_id (int) :

        Returns:
            Flow : matched flow
        """
        table = self.get(table_id)
        logger.debug("matching table_id {} table {} from {}".format(table_id, table, self.flows))
        for flow in table:
            if flow.is_match(msg):
                return flow

    def __lt__(self, other):
        if other is None or not isinstance(other, FlowTables):
            return False
        return self.timestamp < other.timestamp

    def __le__(self, other):
        if other is None or not isinstance(other, FlowTables):
            return False
        return self.timestamp <= other.timestamp

    def __eq__(self, other):
        if other is None or not isinstance(other, FlowTables):
            return False
        return self.flows == other.flows

    def __gt__(self, other):
        if other is None or not isinstance(other, FlowTables):
            return False
        return self.timestamp > other.timestamp

    def __ge__(self, other):
        if other is None or not isinstance(other, FlowTables):
            return False
        return self.timestamp >= other.timestamp

    def __repr__(self):
        return "<FlowTables(datapath={}, timestamp={}, flows={})>".format(self.datapath_id, self.timestamp, self.flows)

    @classmethod
    def parse(cls, flows):
        raise NotImplementedError
