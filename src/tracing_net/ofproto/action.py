"""
Open Flow Actions

This module is a model of OpenFlow Action.
The actual appliction of the action is in ``src.ofproto.pipeline``

TODO:
    * implement all the actions
    * パケットの書き換え履歴の保存の実装ができていない(保存はInstructionでいい，もっというならパイプラインの前でいい)
    * todo POPをどうするか？
"""

from enum import IntEnum
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from pyof.foundation.basic_types import UBInt16

from src.api.proto import net_pb2
from src.tracing_net.ofproto.match import OxmOfbMatchField2stringfield, mac_address2str, ipv4address2str, \
    ipv6address2str

setLoggerClass(Logger)
logger = getLogger('tracing_net.action')


class ActionResult:
    """
    アクション実行後の結果.

    Attributes:
        msg (Msg) : message applied action
        out_ports (list) : out port
    """

    def __init__(self, msg, out_ports=None):
        self.msg = msg
        self.out_ports = out_ports if out_ports else []


ACTIONS = {}


class ActionType(IntEnum):
    """Actions associated with flows and packets."""

    # Output to switch port.
    OFPAT_OUTPUT = 0
    # Copy TTL "outwards" -- from next-to-outermost to outermost
    OFPAT_COPY_TTL_OUT = 11
    # Copy TTL "inwards" -- from outermost to next-to-outermost
    OFPAT_COPY_TTL_IN = 12
    # MPLS TTL
    OFPAT_SET_MPLS_TTL = 15
    # Decrement MPLS TTL
    OFPAT_DEC_MPLS_TTL = 16
    # Push a new VLAN tag
    OFPAT_PUSH_VLAN = 17
    # Pop the outer VLAN tag
    OFPAT_POP_VLAN = 18
    # Push a new MPLS tag
    OFPAT_PUSH_MPLS = 19
    # Pop the outer MPLS tag
    OFPAT_POP_MPLS = 20
    # Set queue id when outputting to a port
    OFPAT_SET_QUEUE = 21
    # Apply group.
    OFPAT_GROUP = 22
    # IP TTL.
    OFPAT_SET_NW_TTL = 23
    # Decrement IP TTL.
    OFPAT_DEC_NW_TTL = 24
    # Set a header field using OXM TLV format.
    OFPAT_SET_FIELD = 25
    # Push a new PBB service tag (I-TAG)
    OFPAT_PUSH_PBB = 26
    # Pop the outer PBB service tag (I-TAG)
    OFPAT_POP_PBB = 27
    # Experimenter type
    OFPAT_EXPERIMENTER = 0xffff

    # Notes: This is not OpenFlow action
    DROP =99

    @classmethod
    def ActionSetOrder(cls):
        order = [cls.OFPAT_COPY_TTL_IN,
                 cls.OFPAT_POP_MPLS, cls.OFPAT_POP_PBB, cls.OFPAT_POP_VLAN,
                 cls.OFPAT_PUSH_MPLS, cls.OFPAT_PUSH_PBB, cls.OFPAT_PUSH_VLAN,
                 cls.OFPAT_COPY_TTL_OUT,
                 cls.OFPAT_DEC_NW_TTL, cls.OFPAT_DEC_MPLS_TTL,
                 cls.OFPAT_SET_FIELD,
                 cls.OFPAT_SET_QUEUE,
                 cls.OFPAT_GROUP,
                 cls.OFPAT_OUTPUT]
        return order


# Classes


class ActionBase:

    def __init__(self, action_type=None):
        self.action_type = action_type

    @abstractmethod
    def action(self, msg):
        """This action apply to msg.

        Args:
            msg (Msg) : packet

        Returns:
            ActionResult
        """
        raise NotImplementedError

    def get_protobuf_message(self):
        action_msg = net_pb2.Action()
        action_msg.str = str(self)
        return action_msg

    def __eq__(self, other):
        if other is None or not isinstance(other, ActionBase):
            raise TypeError("Action can not compare other type (type={})".format(type(other)))
        return str(self) == str(other)

    def __str__(self):
        """This str is used by the visualization feature.

        Examples:
            ActionOutput(port=1)  # action_name(key=value)
        """
        return "{}()".format(self.__class__.__name__)

    def __repr__(self):
        return "<{} type={}>".format(self.__class__.__name__, self.action_type.value)


# class ActionExperimenter(ActionBase):
#     """Action structure for OFPAT_EXPERIMENTER."""
#
#     experimenter = UBInt32()
#     body = BinaryData()
#
#     _allowed_types = (ActionType.OFPAT_EXPERIMENTER,)
#
#     def __init__(self, length=None, experimenter=None, body=None):
#         """Create ActionExperimenterHeader with the optional parameters below.
#         Args:
#             experimenter (int): The experimenter field is the Experimenter ID,
#                 which takes the same form as in struct ofp_experimenter.
#             body(bytes): The body of the experimenter. It is vendor-defined,
#                 so it is left as it is.
#         """
#         super().__init__(action_type=ActionType.OFPAT_EXPERIMENTER)
#         self.length = length
#         self.experimenter = experimenter
#         self.body = body


class ActionGroup(ActionBase):
    """OFPAT_GROUP.

    Notes:
          * This class put on the back burner.
    """

    def __init__(self, group_id=None):
        """Create an ActionGroup with the optional parameters below.
        Args:
            group_id (int): The group_id indicates the group used to process
                this packet. The set of buckets to apply depends on the group
                type.
        """
        super().__init__(action_type=ActionType.OFPAT_GROUP)
        self.group_id = group_id

    def action(self, msg):
        raise NotImplementedError

    def __str__(self):
        return "{}(group_id={})".format(self.__class__.__name__, self.group_id)

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls(group_id=same_obj.group_id)


ACTIONS[ActionType.OFPAT_GROUP] = ActionGroup


class ActionDecMPLSTTL(ActionBase):
    """OFPAT_DEC_MPLS_TTL

    Notes:
          * This class put on the back burner.
    """

    def __init__(self):
        """Create an ActionDecMPLSTTL."""
        super().__init__(action_type=ActionType.OFPAT_DEC_MPLS_TTL)

    def action(self, msg):
        raise NotImplementedError

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls()


ACTIONS[ActionType.OFPAT_DEC_MPLS_TTL] = ActionDecMPLSTTL


class ActionSetMPLSTTL(ActionBase):
    """OFPAT_SET_MPLS_TTL

    Notes:
          * This class put on the back burner.
    """

    def __init__(self, mpls_ttl=None):
        """Create an ActionSetMPLSTTL with the optional parameters below.

        Args:
            mpls_ttl (int): The mpls_ttl field is the MPLS TTL to set.
        """
        super().__init__(action_type=ActionType.OFPAT_SET_MPLS_TTL)
        self.mpls_ttl = mpls_ttl

    def action(self, msg):
        raise NotImplementedError

    def __str__(self):
        return "{}(mpls_ttl={})".format(self.__class__.__name__, self.mpls_ttl)

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls(same_obj.mpls_ttl)


ACTIONS[ActionType.OFPAT_SET_MPLS_TTL] = ActionSetMPLSTTL


class ActionCopyTTLIn(ActionBase):
    """OFPAT_COPY_TTL_IN

    Notes:
          * This class put on the back burner.
    """

    def __init__(self):
        """Create an ActionCopyTTLIn."""
        super().__init__(action_type=ActionType.OFPAT_COPY_TTL_IN)

    def action(self, msg):
        raise NotImplementedError

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls()


ACTIONS[ActionType.OFPAT_COPY_TTL_IN] = ActionCopyTTLIn


class ActionCopyTTLOut(ActionBase):
    """OFPAT_COPY_TTL_OUT

    Notes:
          * This class put on the back burner.
    """

    def __init__(self):
        """Create an ActionCopyTTLOut."""
        super().__init__(action_type=ActionType.OFPAT_COPY_TTL_OUT)

    def action(self, msg):
        raise NotImplementedError

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls()


ACTIONS[ActionType.OFPAT_COPY_TTL_OUT] = ActionCopyTTLOut


class ActionPopVLAN(ActionBase):
    """OFPAT_POP_VLAN

    Notes:
          * This class put on the back burner.
    """

    def __init__(self):
        """Create an ActionPopVLAN."""
        super().__init__(action_type=ActionType.OFPAT_POP_VLAN)

    def action(self, msg):
        # msg.set_properties("vlan_vid", None)
        # result = ActionResult(msg=msg)
        raise NotImplementedError

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls()


ACTIONS[ActionType.OFPAT_POP_VLAN] = ActionPopVLAN


class ActionPopPBB(ActionBase):
    """OFPAT_POP_PBB

    Notes:
          * This class put on the back burner.
    """

    def __init__(self):
        """Create an ActionPopPBB."""
        super().__init__(action_type=ActionType.OFPAT_POP_PBB)

    def action(self, msg):
        raise NotImplementedError

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls()


ACTIONS[ActionType.OFPAT_POP_PBB] = ActionPopPBB


class ActionDecNWTTL(ActionBase):
    """OFPAT_DEC_NW_TTL

    Notes:
          * This class put on the back burner.
    """

    def __init__(self):
        """Create a ActionDecNWTTL."""
        super().__init__(action_type=ActionType.OFPAT_DEC_NW_TTL)

    def action(self, msg):
        raise NotImplementedError

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls()


ACTIONS[ActionType.OFPAT_DEC_NW_TTL] = ActionDecNWTTL


class ActionSetNWTTL(ActionBase):
    """OFPAT_SET_NW_TTL

    Notes:
          * This class put on the back burner.
    """

    def __init__(self, nw_ttl=None):
        """Create an ActionSetNWTTL with the optional parameters below.
        Args:
            nw_ttl (int): the TTL address to set in the IP header.
        """
        super().__init__(action_type=ActionType.OFPAT_SET_NW_TTL)
        self.nw_ttl = nw_ttl

    def action(self, msg):
        raise NotImplementedError

    def __str__(self):
        return "{}(nw_ttl={})".format(self.__class__.__name__, self.nw_ttl)

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls(same_obj.nw_ttl)


ACTIONS[ActionType.OFPAT_SET_NW_TTL] = ActionSetNWTTL


class ActionOutput(ActionBase):
    """Defines the actions output.
    Action structure for :attr:`ActionType.OFPAT_OUTPUT`, which sends packets
    out :attr:`port`. When the :attr:`port` is the
    :attr:`.Port.OFPP_CONTROLLER`, :attr:`max_length` indicates the max number
    of bytes to send. A :attr:`max_length` of zero means no bytes of the packet
    should be sent.
    """

    def __init__(self, port=None):
        """Create a ActionOutput with the optional parameters below.

        Args:
            port (:class:`Port` or :class:`int`): Output port.
        """
        super().__init__(action_type=ActionType.OFPAT_OUTPUT)
        self.port = port

    def action(self, msg):
        result = ActionResult(msg=msg)
        result.out_ports.append(self.port)
        return result

    def __str__(self):
        return "{}(port={})".format(self.__class__.__name__, self.port)

    def __repr__(self):
        return f"{type(self).__name__}(port={self.port})"

    @classmethod
    def parser(cls, port1=None, port2=None, controller=None):
        """

        Args:
            port1:
            port2:
            controller: ovs controller action

        Returns:
            ActionOutput : instance of ActionOutput
        """
        if port1:
            return cls(port=port1)
        elif port2:
            return cls(port=port2)
        elif controller:
            return cls(port=controller)

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls(port=same_obj.port)


ACTIONS[ActionType.OFPAT_OUTPUT] = ActionOutput


class ActionDrop(ActionBase):
    """DropAction"""

    def __init__(self):
        super(ActionDrop, self).__init__(action_type=ActionType.DROP)

    def action(self, msg):
        return ActionResult(msg=msg)

    @classmethod
    def parser(cls):
        return cls()

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls()


ACTIONS[ActionType.DROP] = ActionDrop


class ActionPopMPLS(ActionBase):
    """OFPAT_POP_MPLS

    Notes:
          * This class put on the back burner.
    """

    def __init__(self, ethertype=None):
        """Create an ActionPopMPLS with the optional parameters below.
        Args:
            ethertype (int): indicates the Ethertype of the payload.
        """
        super().__init__(action_type=ActionType.OFPAT_POP_MPLS)
        self.ethertype = ethertype

    def action(self, msg):
        raise NotImplementedError

    def __str__(self):
        return "{}(ethertype={})".format(self.__class__.__name__, self.ethertype)

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls(ethertype=same_obj.ethertype)


ACTIONS[ActionType.OFPAT_POP_MPLS] = ActionPopMPLS


class ActionPush(ActionBase):
    """OFPAT_PUSH_[VLAN/MPLS/PBB]

    Notes:
          * This class put on the back burner.
    """

    def __init__(self, action_type=None, ethertype=None):
        """Create a ActionPush with the optional parameters below.
        Args:
            action_type (:class:`ActionType`): indicates which tag will be
                pushed (VLAN, MPLS, PBB).
            ethertype (int): indicates the Ethertype of the new tag.
        """
        super().__init__(action_type)
        self.ethertype = ethertype

    def action(self, msg):
        raise NotImplementedError

    def __str__(self):
        return "{}(ethertype={})".format(self.__class__.__name__, self.ethertype)

    @classmethod
    def parser_vlan(cls, ethertype=None):
        return cls(action_type=ActionType.OFPAT_PUSH_VLAN, ethertype=ethertype)

    @classmethod
    def parser_mpls(cls, ethertype=None):
        return cls(action_type=ActionType.OFPAT_PUSH_MPLS, ethertype=ethertype)

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls(same_obj.ethertype)


class ActionPushMPLS(ActionPush):

    def __init__(self, ethertype=None):
        super(ActionPushMPLS, self).__init__(ActionType.OFPAT_PUSH_MPLS, ethertype)

    @classmethod
    def parser(cls, ethertype=None):
        return cls.parser_mpls(ethertype)


ACTIONS[ActionType.OFPAT_PUSH_MPLS] = ActionPushMPLS


class ActionPushVLAN(ActionPush):

    def __init__(self, ethertype=None):
        super(ActionPushVLAN, self).__init__(ActionType.OFPAT_PUSH_VLAN, ethertype)

    @classmethod
    def parser(cls, ethertype=None):
        return cls.parser_vlan(ethertype)


ACTIONS[ActionType.OFPAT_PUSH_VLAN] = ActionPushVLAN


class ActionSetField(ActionBase):
    """OFPAT_SET_FIELD

    Notes:
          * This class put on the back burner.
    """

    def __init__(self, value=None, mask=None, dst=None):
        """Create a ActionSetField with the optional parameters below.
        """
        super().__init__(action_type=ActionType.OFPAT_SET_FIELD)
        self.value = value
        self.mask = mask
        self.dst = dst

    def action(self, msg):
        current_value = getattr(msg, self.dst)
        value = self.value
        if self.mask is not None:  # todo test
            current_value = current_value & ~self.mask
            value = self.value & self.mask
            msg.set_properties(self.dst, current_value + value)
        else:
            msg.set_properties(self.dst, self.value)
        return ActionResult(msg=msg)

    def __str__(self):
        return "{}({}/{}, {})".format(self.__class__.__name__, self.value, self.mask, self.dst)

    # def __repr__(self):
    #     return (f"{type(self).__name__}({self.field.oxm_field!s}, "
    #             f"{self.field.oxm_value})")

    @classmethod
    def parser(cls, value=None, mask=None, dst=None):
        return cls(value=value, mask=mask, dst=dst)

    @classmethod
    def parse_from_obj(cls, same_obj):
        field_name = OxmOfbMatchField2stringfield(same_obj.field.oxm_field)
        value = same_obj.field.oxm_value
        if field_name in ["eth_dst", "eth_src"]:
            value = mac_address2str(value)
        elif field_name in ["ipv4_src", "ipv4_dst"]:
            value = ipv4address2str(value)
        elif field_name in ["ipv6_src", "ipv6_dst"]:
            value = ipv6address2str(value)
        else:
            value = int.from_bytes(value, byteorder="big")
        return cls(value=value, mask=0xfffffffffffff, dst=field_name)


ACTIONS[ActionType.OFPAT_SET_FIELD] = ActionSetField


class ActionSetQueue(ActionBase):
    """OFPAT_SET_QUEUE

    Notes:
          * This class put on the back burner.
    """

    def __init__(self, queue_id=None):
        """Create an ActionSetQueue with the optional parameters below.
        Args:
            queue_id (int): The queue_id send packets to given queue on port.
        """
        super().__init__(action_type=ActionType.OFPAT_SET_QUEUE)
        self.queue_id = queue_id

    def action(self, msg):
        raise NotImplementedError

    def __str__(self):
        return "{}(queue_id={})".format(self.__class__.__name__, self.queue_id)

    @classmethod
    def parse_from_obj(cls, same_obj):
        return cls(same_obj.queue_id)


ACTIONS[ActionType.OFPAT_SET_QUEUE] = ActionSetQueue


class ActionSet:
    """ActionSet"""

    def __init__(self, actions=None):
        self.actions = actions if actions else []

    def write(self, action):
        if isinstance(action, ActionBase):
            self.actions.append(action)
        else:
            logger.error("Type {} can't add to ActionSet. Only ActionBase".format(type(action)))

    def clear(self):
        self.actions = []

    def action(self, msg):
        """

        Args:
            msg:

        Returns:
            InstructionResult
        """
        from src.tracing_net.ofproto.instruction import InstructionResult

        result = InstructionResult(msg=msg, action_set=self)
        self._sort()
        for action in self.actions:
            action_result = action.action(msg=msg)
            result.out_ports.extend(action_result.out_ports)
        return result

    def _sort(self):
        tmp_actions = []
        for t in ActionType.ActionSetOrder():
            actions = self._get_type(t)
            for a in actions:
                tmp_actions.append(a)
        self.actions = tmp_actions

    def _get_type(self, action_type: ActionType):
        actions = []
        for action in self.actions:
            if action.action_type == action_type:
                actions.append(action)
        return actions

    def get_protobuf_message(self):
        """

        Returns:
            net_pb2.ActionSet
        """
        self._sort()
        action_set = net_pb2.ActionSet()
        for action in self.actions:
            action_set.actions.append(action.get_protobuf_message())
        return action_set

