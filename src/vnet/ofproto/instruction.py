"""
OpenFlow Instructions

This module is a model of OpenFlow Instruction.
The actual appliction of the instruction is in ``src.ofproto.pipeline``
"""
from enum import IntEnum
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from src.api.proto import net_pb2
from src.vnet.ofproto.action import ACTIONS


setLoggerClass(Logger)
logger = getLogger('vnet.instruction')


INSTRUCTIONS = {}


class InstructionResult:
    """
    インストラクション実行後の結果．
    """

    def __init__(self, msg, action_set=None, out_ports=None, table_id=None):
        """

        Args:
            msg (Msg) :
            action_set (ActionSet) :
            out_ports (list) :
            table_id (int) : next table id
        """
        self.msg = msg
        self.action_set = action_set
        self.out_ports = out_ports if out_ports else []
        self.table_id = table_id

    def __repr__(self):
        return "<InstructionResult msg={} action_set={} out_ports={} table_id={}>"\
            .format(self.msg, self.action_set, self.out_ports, self.table_id)


class InstructionType(IntEnum):
    """List of instructions that are currently defined."""

    # Setup the next table in the lookup pipeline
    OFPIT_GOTO_TABLE = 1
    # Setup the metadata field for use later in pipeline
    OFPIT_WRITE_METADATA = 2
    # Write the action(s) onto the datapath action set
    OFPIT_WRITE_ACTIONS = 3
    # Applies the action(s) immediately
    OFPIT_APPLY_ACTIONS = 4
    # Clears all actions from the datapath action set
    OFPIT_CLEAR_ACTIONS = 5
    # Apply meter (rate limiter)
    OFPIT_METER = 6
    # Experimenter instruction
    OFPIT_EXPERIMENTER = 0xFFFF

    def find_class(self):
        """Return a class related with this type."""
        classes = {1: InstructionGotoTable, 2: InstructionWriteMetadata,
                   3: InstructionWriteAction, 4: InstructionApplyAction,
                   5: InstructionClearAction, 6: InstructionMeter}
        return classes.get(self.value, None)


class Instruction(metaclass=ABCMeta):
    """Generic Instruction class"""

    def __init__(self, instruction_type=None):
        """Create a Instruction with the optional parameters below.

        Args:
            instruction_type(InstructionType): Type of instruction.
        """
        super().__init__()
        self.instruction_type = instruction_type

    @abstractmethod
    def apply(self, msg, action_set=None):
        """apply actions to msg

        Args:
            msg (Msg) :
            action_set (action.ActionSet) :

        Returns:
            InstructionResult : result
        """
        raise NotImplementedError

    @abstractmethod
    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.Instruction
        """
        raise NotImplementedError

    def __repr__(self):
        return "<{} type={}>".format(self.__class__.__name__, self.instruction_type.value)

    @classmethod
    def parse_from_ofcapture(cls, instructions):
        for inst in instructions:
            pass
        return None


class InstructionApplyAction(Instruction):
    """OFPIT_APPLY_ACTIONS"""

    def __init__(self, actions=None):
        """Create a InstructionApplyAction with the optional parameters below.
        Args:
            actions (:class:`~.actions.ListOfActions`):
                Actions associated with OFPIT_APPLY_ACTIONS.
        """
        super().__init__(InstructionType.OFPIT_APPLY_ACTIONS)
        self.actions = actions if actions else []

    def apply(self, msg, action_set=None):
        """This instruction apply to msg and action set.

        Args:
            msg (Msg) :
            action_set (action.ActionSet) :

        Returns:
            InstructionResult : result

        TODO:
            * 適用順序を保証する
        """
        instruction_result = InstructionResult(msg=msg, action_set=action_set)
        for action in self.actions:
            action_result = action.action(msg=instruction_result.msg)
            instruction_result.msg = action_result.msg
            instruction_result.out_ports.extend(action_result.out_ports)
        return instruction_result

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.Instruction
        """
        instruction_msg = net_pb2.Instruction()
        instruction_msg.type = net_pb2.InstructionType.OFPIT_APPLY_ACTIONS
        actions = net_pb2.InstructionActions()
        for a in self.actions:
            actions.actions.append(a.get_protobuf_message())
        instruction_msg.actions.CopyFrom(actions)
        return instruction_msg

    @classmethod
    def parser(cls, actions):
        return cls(actions=actions)

    @classmethod
    def parse_from_obj(cls, same_obj):
        actions = same_obj.actions
        tmp_actions = []
        for action in actions:
            action_cls = ACTIONS[int(action.action_type)]
            action = action_cls.parse_from_obj(action)
            tmp_actions.append(action)
        return cls(tmp_actions)


INSTRUCTIONS[InstructionType.OFPIT_APPLY_ACTIONS] = InstructionApplyAction


class InstructionClearAction(Instruction):
    """OFPIT_CLEAR_ACTIONS"""

    def __init__(self, actions=None):
        """Create a InstructionClearAction with the optional parameters below.

        Args:
            actions (list): Actions associated with OFPIT_CLEAR_ACTIONS.
        """
        super().__init__(InstructionType.OFPIT_CLEAR_ACTIONS)
        self.actions = actions if actions else []

    def apply(self, msg, action_set=None):
        """This instruction apply to msg and action set.

        Args:
            msg (Msg) :
            action_set (action.ActionSet) :

        Returns:
            InstructionResult : result
        """
        action_set.clear()
        return InstructionResult(msg=msg, action_set=action_set)

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.Instruction
        """
        instruction_msg = net_pb2.Instruction()
        instruction_msg.type = net_pb2.InstructionType.OFPIT_CLEAR_ACTIONS
        actions = net_pb2.InstructionActions()
        for a in self.actions:
            actions.actions.append(a.get_protobuf_message())
        instruction_msg.actions.CopyFrom(actions)
        return instruction_msg

    @classmethod
    def parser(cls):
        return cls()

    @classmethod
    def parse_from_obj(cls, same_obj):
        actions = getattr(same_obj, 'actions', None)
        tmp_actions = []
        if actions:
            for action in actions:
                action_cls = ACTIONS[int(action.action_type)]
                action = action_cls.parse_from_obj(action)
                tmp_actions.append(action)
        return cls(tmp_actions)


INSTRUCTIONS[InstructionType.OFPIT_CLEAR_ACTIONS] = InstructionClearAction


class InstructionGotoTable(Instruction):
    """OFPIT_GOTO_TABLE"""

    def __init__(self, table_id=None):
        """Create a InstructionGotoTable with the optional parameters below.
        Args:
            length (int): Length of this struct in bytes.
            table_id (int): set next table in the lookup pipeline.
        """
        super().__init__(InstructionType.OFPIT_GOTO_TABLE)
        if not isinstance(table_id, int):
            raise TypeError
        self.table_id = table_id

    def apply(self, msg, action_set=None):
        """This instruction apply to msg and action set.

        Args:
            msg (Msg) :
            action_set (action.ActionSet) :

        Returns:
            InstructionResult : result
        """
        result = InstructionResult(msg=msg, action_set=action_set)
        result.table_id = self.table_id
        return result

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.Instruction
        """
        instruction_msg = net_pb2.Instruction()
        instruction_msg.type = net_pb2.InstructionType.OFPIT_GOTO_TABLE
        goto_table = net_pb2.InstructionGotoTable()
        goto_table.table_id = self.table_id
        instruction_msg.goto_table.CopyFrom(goto_table)
        return instruction_msg

    @classmethod
    def parser(cls, table=None):
        return cls(table_id=int(table))

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls(int(same_obj.table_id))


INSTRUCTIONS[InstructionType.OFPIT_GOTO_TABLE] = InstructionGotoTable


class InstructionMeter(Instruction):
    """OFPIT_METER

    Notes:
          * This class put on the back burner.
    """

    def __init__(self, meter_id=None):
        """Create a InstructionMeter with the optional parameters below.
        Args:
            meter_id (int): Meter instance.
        """
        super().__init__(InstructionType.OFPIT_METER)
        self.meter_id = meter_id

    def apply(self, msg, action_set=None):
        """This instruction apply to msg and action set.

        Args:
            msg (Msg) :
            action_set (action.ActionSet) :

        Returns:
            InstructionResult : result
        """
        raise NotImplementedError

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.Instruction
        """
        instruction_msg = net_pb2.Instruction()
        instruction_msg.type = net_pb2.InstructionType.OFPIT_METER
        meter = net_pb2.InstructionMeter()
        meter.meter_id = self.meter_id
        instruction_msg.meter.CopyFrom(meter)
        return instruction_msg

    @classmethod
    def parser(cls, meter_id=None):
        return cls(meter_id=meter_id)

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls(same_obj.meter_id)


INSTRUCTIONS[InstructionType.OFPIT_METER] = InstructionMeter


class InstructionWriteAction(Instruction):
    """OFPIT_WRITE_ACTIONS."""

    def __init__(self, actions=None):
        """Create a InstructionWriteAction with the optional parameters below.
        Args:
            actions (:class:`~.actions.ListOfActions`):
                Actions associated with OFPIT_WRITE_ACTIONS.
        """
        super().__init__(InstructionType.OFPIT_WRITE_ACTIONS)
        self.actions = actions if actions else []

    def apply(self, msg, action_set=None):
        """This instruction apply to msg and action set.

        Args:
            msg (Msg) :
            action_set (action.ActionSet) :

        Returns:
            InstructionResult : result
        """
        result = InstructionResult(msg=msg, action_set=action_set)
        for action in self.actions:
            result.action_set.write(action)
        return result

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.Instruction
        """
        instruction_msg = net_pb2.Instruction()
        instruction_msg.type = net_pb2.InstructionType.OFPIT_WRITE_ACTIONS
        actions = net_pb2.InstructionActions()
        for a in self.actions:
            actions.actions.append(a.get_protobuf_message())
        instruction_msg.actions.CopyFrom(actions)
        return instruction_msg

    @classmethod
    def parser(cls, actions):
        """

        Args:
            actions (list) :

        Returns:
            InstructionWriteAction :
        """
        return cls(actions=actions)

    @classmethod
    def parse_from_obj(cls, same_obj):
        actions = same_obj.actions
        tmp_actions = []
        for action in actions:
            action_cls = ACTIONS[int(action.action_type)]
            action = action_cls.parse_from_obj(action)
            tmp_actions.append(action)
        return cls(tmp_actions)


INSTRUCTIONS[InstructionType.OFPIT_WRITE_ACTIONS] = InstructionWriteAction


class InstructionWriteMetadata(Instruction):
    """OFPIT_WRITE_METADATA.

    Notes:
          * This class put on the back burner.
    """

    def __init__(self, metadata=0, metadata_mask=None):
        """Create InstructionWriteMetadata with the optional parameters below.

        Args:
            metadata (int): Metadata value to write.
            metadata_mask (int): Metadata write bitmask.
        """
        super().__init__(InstructionType.OFPIT_WRITE_METADATA)
        self.metadata = metadata
        self.metadata_mask = metadata_mask if metadata_mask else 0xffffffffffffffff

    def apply(self, msg, action_set=None):
        """This instruction apply to msg and action set.

        Args:
            msg (Msg) :
            action_set (action.ActionSet) :

        Returns:
            InstructionResult : result
        """
        result = InstructionResult(msg=msg, action_set=action_set)
        if msg.metadata is not None:
            msg.metadata = msg.metadata & ~self.metadata_mask
            msg.metadata = msg.metadata + (self.metadata & self.metadata_mask)
        else:
            msg.metadata = self.metadata & self.metadata_mask
        return result

    def get_protobuf_message(self):
        """This method convert this instance to a protocol buffer's obj

        Returns:
            net_pb2.Instruction
        """
        instruction_msg = net_pb2.Instruction()
        instruction_msg.type = net_pb2.InstructionType.OFPIT_WRITE_METADATA
        write_metadata = net_pb2.InstructionWriteMetadata()
        write_metadata.metadata = self.metadata
        write_metadata.metadata_mask = self.metadata_mask
        instruction_msg.write_metadata.CopyFrom(write_metadata)
        return instruction_msg

    @classmethod
    def parser(cls, metadata=0, mask=0xffffffffffffffff):
        """
        todo:
            parse前でintに
        """
        if not (isinstance(metadata, int) and isinstance(mask, int)):
            metadata = int(metadata, 16)
            mask = int(mask, 16)
        else:
            metadata = int(metadata)
            mask = int(mask)
        return cls(metadata=metadata, metadata_mask=mask)

    @classmethod
    def parse_from_obj(cls, same_obj):
        metadata = int(same_obj.metadata)
        mask = getattr(same_obj, "metadata_mask", None)
        if not isinstance(mask, int):
            mask = int(mask)
        return cls(metadata, mask)


INSTRUCTIONS[InstructionType.OFPIT_WRITE_METADATA] = InstructionWriteMetadata


def parse_from_obj(instructions):
    parsed_insts = []
    for inst in instructions:
        inst = INSTRUCTIONS[int(inst.instruction_type)].parse_from_obj(inst)
        parsed_insts.append(inst)
    return parsed_insts


if __name__ == '__main__':
    apply_action = InstructionApplyAction()
    clear_action = InstructionClearAction()
    goto_table = InstructionGotoTable(1)
    meter = InstructionMeter(1)
    write_action = InstructionWriteAction()
    write_metadata = InstructionWriteMetadata()

    for inst in [apply_action, clear_action, goto_table, meter, write_action, write_metadata]:
        print(inst.get_protobuf_message())
