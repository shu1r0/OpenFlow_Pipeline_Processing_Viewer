"""
インストラクションの再現
"""
from enum import IntEnum
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger


setLoggerClass(Logger)
logger = getLogger('tracing_net.instruction')


class InstructionResult:

    def __init__(self, msg, action_set=None, out_ports=None, table_id=None):
        """

        Args:
            msg (Msg) :
            action_set (ActionSet) :
            out_ports (list) :
            table_id (int) :
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

    def __repr__(self):
        return "<{} type={}>".format(self.__class__.__name__, self.instruction_type.value)


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
        """
        instruction_result = InstructionResult(msg=msg, action_set=action_set)
        for action in self.actions:
            action_result = action.action(msg=instruction_result.msg)
            instruction_result.msg = action_result.msg
            instruction_result.out_ports.extend(action_result.out_ports)
        return instruction_result

    @classmethod
    def parser(cls, actions):
        return cls(actions=actions)


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

    @classmethod
    def parser(cls):
        return cls()


class InstructionGotoTable(Instruction):
    """OFPIT_GOTO_TABLE"""

    def __init__(self, table_id=None):
        """Create a InstructionGotoTable with the optional parameters below.
        Args:
            length (int): Length of this struct in bytes.
            table_id (int): set next table in the lookup pipeline.
        """
        super().__init__(InstructionType.OFPIT_GOTO_TABLE)
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

    @classmethod
    def parser(cls, table=None):
        return cls(table_id=table)


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
        pass

    @classmethod
    def parser(cls, meter_id=None):
        return cls(meter_id=meter_id)


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
        pass

    @classmethod
    def parser(cls, actions):
        """

        Args:
            actions (list) :

        Returns:
            InstructionWriteAction :
        """
        return cls(actions=actions)


class InstructionWriteMetadata(Instruction):
    """OFPIT_WRITE_METADATA.

    Notes:
          * This class put on the back burner.
    """

    def __init__(self, metadata=0, metadata_mask=0):
        """Create InstructionWriteMetadata with the optional parameters below.

        Args:
            metadata (int): Metadata value to write.
            metadata_mask (int): Metadata write bitmask.
        """
        super().__init__(InstructionType.OFPIT_WRITE_METADATA)
        self.metadata = metadata
        self.metadata_mask = metadata_mask

    def apply(self, msg, action_set=None):
        """This instruction apply to msg and action set.

        Args:
            msg (Msg) :
            action_set (action.ActionSet) :

        Returns:
            InstructionResult : result
        """
        pass

    @classmethod
    def parser(cls, metadata=0, mask=0):
        return cls(metadata=metadata, metadata_mask=mask)



# def apply_instruction(msg, instruction_name, actions, action_set, *args):
#     """
#
#     Todo:
#         * アクション順にしたい
#
#     Args:
#         msg:
#         instruction_name:
#         actions:
#         action_set:
#         *args:
#
#     Returns:
#
#     """
#     raise NotImplementedError
#
#
# def merter(msg):
#     raise NotImplementedError
#
#
# def apply_actions(msg, actions):
#     raise NotImplementedError
#
#
# def write_actions(msg, actions, action_set):
#     raise NotImplementedError
#
#
# def clear_actions(msg, action_set):
#     raise NotImplementedError
#
#
# def write_metadata(msg, data, mask):
#     raise NotImplementedError
#
#
# def stat_trigger(msg, *args):
#     raise NotImplementedError
#
#
# def goto_table(msg, table_id):
#     raise NotImplementedError

