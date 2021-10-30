"""Flow Table Module"""
import datetime
from logging import getLogger, setLoggerClass, Logger

from src.tracing_net.ofproto.instruction import InstructionResult, Instruction
from src.tracing_net.ofproto.match import Match
from src.tracing_net.ofproto.msg import Msg
from src.config import conf

from src.api.proto import net_pb2


setLoggerClass(Logger)
logger = getLogger('tracing_net.table')


class Flow:
    """Flow table entry

    Attributes:
        cookie (str) : cookie
        duration (int) : duration
        table (int) : table id
        n_packets (int) : counter of packets
        n_bytes (int) : counter of packet bytes
        priority (int) : flow priority
        match (list[Match]) : match field
        actions (list) : action(instruction) list
        flow_id (int) : this flow identifier. The flow_id is decided when the flow is added to flow table.

    Warnings:
        This flow_id is not flow table index. It is used only to identify the flow on system.
    """

    def __init__(self, cookie="", duration=0, table=0, n_packets=0, n_bytes=0,
                 priority=0, match=None, actions=None):
        self.cookie = cookie
        self.duration = duration if isinstance(duration, int) else int(duration)
        self.table = table if isinstance(table, int) else int(table)
        self.n_packets = n_packets if isinstance(n_packets, int) else int(n_packets)
        self.n_bytes = n_bytes if isinstance(n_bytes, int) else int(n_bytes)
        # self.idle_age =
        self.priority = priority if isinstance(priority, int) else int(priority)
        self.match: list[Match] = match if match is not None else []
        self.actions: list[Instruction] = actions if actions is not None else []
        self.flow_id = -1

    def is_match(self, msg):
        """Is msg matched?

        * If there is any item that does not match, The msg is not matched this flow.

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
        matched = True
        # match key is openflow packet field (e.g. eth_type, ip_proto and more)
        # match values is dict that is value and mask. If the values is able to convert digit, the value type is int.
        for match in self.match:
            msg_value = getattr(msg, match.field_name, None)
            if not match.is_match(msg_value):
                matched = False

        if conf.OUTPUT_FLOW_MATCHING_RESULT_TO_LOGFILE:
            logger.debug("flow matching is {}: msg={}, match={}".format(str(matched), msg, self.match))
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
        # Notes:
        #     * applied action(instruction) is only apply_actions
        for action in self.actions:
            temp_result = action.apply(msg=msg, action_set=action_set)
            # update out ports
            instruction_result.out_ports.extend(temp_result.out_ports)
            # update table id
            instruction_result.table_id = temp_result.table_id
        return instruction_result

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        * 構造は``src/api/proto/net.proto``のFlow参照

        Returns:
            net_pb2.Flow
        """
        flow_msg = net_pb2.Flow()
        flow_msg.cookie = self.cookie
        flow_msg.duration = self.duration
        flow_msg.table = self.table
        flow_msg.n_packets = self.n_packets
        flow_msg.n_bytes = self.n_bytes
        flow_msg.priority = self.priority
        for m in self.match:
            flow_msg.match.append(m.get_protobuf_message())
        for i in self.actions:
            flow_msg.actions.append(i.get_protobuf_message())
        flow_msg.flow_id = self.flow_id
        return flow_msg

    def __lt__(self, other):
        if other is None or not isinstance(other, Flow):
            return False
        return self.priority < other.priority

    def __le__(self, other):
        if other is None or not isinstance(other, Flow):
            return False
        return self.priority <= other.priority

    def __eq__(self, other):
        """
        todo: これでいいの？？？？
        """
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

        # a counter to decide flow_id
        self._flow_counter = 0

    def add(self, flow: Flow):
        """add flow

        * The flow is inserted in ascending order of priority.
        * This set the flow id.

        Args:
            flow (Flow) : flow entry
        """
        if not isinstance(flow, Flow):
            raise TypeError
        flow.flow_id = self._flow_counter
        self._flow_counter += 1

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

    def get(self, table_id: int or str):
        """get flow table

        Args:
            table_id (int or str) : table id

        Returns:
            list[Flow] : flow table
        """
        table = []
        for flow in self.flows:
            if int(flow.table) == int(table_id):
                table.append(flow)
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
        if conf.OUTPUT_FLOW_MATCHING_RESULT_TO_LOGFILE:
            logger.debug("Matching calculation in table_id {} table {}".format(table_id, table))
        for flow in table:
            if flow.is_match(msg):
                return flow

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.FlowTable
        """
        flowtable_msg = net_pb2.FlowTable()
        for f in self.flows:
            flowtable_msg.flows.append(f.get_protobuf_message())
        return flowtable_msg

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

