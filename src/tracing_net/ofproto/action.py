from enum import IntEnum
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from pyof.foundation.basic_types import UBInt16


setLoggerClass(Logger)
logger = getLogger('tracing_net.action')

class ActionResult:

    def __init__(self, msg, out_ports=None, table_id=None):
        self.msg = msg
        self.out_ports = out_ports if out_ports else []


class ActionType(IntEnum):
    """Actions associated with flows and packets."""

    #: Output to switch port.
    OFPAT_OUTPUT = 0
    #: Copy TTL "outwards" -- from next-to-outermost to outermost
    OFPAT_COPY_TTL_OUT = 11
    #: Copy TTL "inwards" -- from outermost to next-to-outermost
    OFPAT_COPY_TTL_IN = 12
    #: MPLS TTL
    OFPAT_SET_MPLS_TTL = 15
    #: Decrement MPLS TTL
    OFPAT_DEC_MPLS_TTL = 16
    #: Push a new VLAN tag
    OFPAT_PUSH_VLAN = 17
    #: Pop the outer VLAN tag
    OFPAT_POP_VLAN = 18
    #: Push a new MPLS tag
    OFPAT_PUSH_MPLS = 19
    #: Pop the outer MPLS tag
    OFPAT_POP_MPLS = 20
    #: Set queue id when outputting to a port
    OFPAT_SET_QUEUE = 21
    #: Apply group.
    OFPAT_GROUP = 22
    #: IP TTL.
    OFPAT_SET_NW_TTL = 23
    #: Decrement IP TTL.
    OFPAT_DEC_NW_TTL = 24
    #: Set a header field using OXM TLV format.
    OFPAT_SET_FIELD = 25
    #: Push a new PBB service tag (I-TAG)
    OFPAT_PUSH_PBB = 26
    #: Pop the outer PBB service tag (I-TAG)
    OFPAT_POP_PBB = 27
    #: Experimenter type
    OFPAT_EXPERIMENTER = 0xffff

    DROP =99


# Classes


class ActionBase:

    action_type = UBInt16(enum_ref=ActionType)

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


class ActionPopVLAN(ActionBase):
    """OFPAT_POP_VLAN

    Notes:
          * This class put on the back burner.
    """

    def __init__(self):
        """Create an ActionPopVLAN."""
        super().__init__(action_type=ActionType.OFPAT_POP_VLAN)

    def action(self, msg):
        raise NotImplementedError


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


class ActionDrop(ActionBase):
    """DropAction"""

    def __init__(self):
        super(ActionDrop, self).__init__(action_type=ActionType.DROP)

    def action(self, msg):
        return ActionResult(msg=msg)

    @classmethod
    def parser(cls):
        return cls()


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

    @classmethod
    def parser_vlan(cls, ethertype=None):
        return cls(action_type=ActionType.OFPAT_PUSH_VLAN, ethertype=ethertype)

    @classmethod
    def parser_mpls(cls, ethertype=None):
        return cls(action_type=ActionType.OFPAT_PUSH_MPLS, ethertype=ethertype)


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
        raise NotImplementedError

    # def __repr__(self):
    #     return (f"{type(self).__name__}({self.field.oxm_field!s}, "
    #             f"{self.field.oxm_value})")

    @classmethod
    def parser(cls, value=None, mask=None, dst=None):
        return cls(value=value, mask=mask, dst=dst)


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


class ActionsList:
    """Action list"""

    def __init__(self, actions=None):
        self.actions = actions if actions else []


class ActionSet:
    """ActionSet"""

    def __init__(self, actions=None):
        self.actions = actions if actions else []

    def write(self, action):
        pass

    def clear(self):
        pass




# def action(action_name, msg, *args):
#     """
#
#     Args:
#         action_name:
#         msg:
#         **params:
#
#     Returns:
#         ActionResult: msg, out_ports
#     """
#     try:
#         args = 'msg,' + ','.join(args)
#         msg, out_ports = eval(action_name + '(' + args + ')')
#         return msg, out_ports
#     except NotImplementedError:
#         raise Exception('This action do not supported: name={}, args={}'.format(action_name, args))
#     except Exception as e:
#         raise Exception('Failed to call action method: name={}, args={}'.format(action_name, args))
#
#
# def drop(msg):
#     out_ports = []
#     return ActionResult(msg, out_ports)
#
#
# def output(msg, port):
#     out_ports = [port]
#     return ActionResult(msg, out_ports)
#
#
# def controller(msg, controller):
#     out_ports = [controller]
#     return ActionResult(msg, out_ports)
#
#
# def enqueue(msg):
#     raise NotImplementedError
#
#
# def bundle(msg):
#     raise NotImplementedError
#
#
# def group(msg):
#     raise NotImplementedError
#
#
# def strip_vlan(msg):
#     raise NotImplementedError
#
#
# def pop_vlan(msg):
#     raise NotImplementedError
#
#
# def push_vlan(msg, eth_type):
#     out_ports = []
#     if msg.vlan_vid:
#         msg.vlan_vid = eth_type
#     return ActionResult(msg, out_ports)
#
#
# def push_mpls(msg, eth_type):
#     out_ports = []
#     msg.mpls_label = eth_type
#     return ActionResult(msg, out_ports)
#
#
# def pop_mpls(msg, eth_type):
#     raise NotImplementedError
#
#
# def encap(msg):
#     raise NotImplementedError
#
#
# def decap(msg):
#     raise NotImplementedError
#
#
# def set_field(msg, value, mask, dst):
#     out_ports = []
#     dst = value & mask
#     raise NotImplementedError
#
#
# def move(msg, src, dst):
#     raise NotImplementedError
#
#
# def mod_dl_src(msg, mac):
#     raise NotImplementedError
#
#
# def mod_dl_dst(msg, mac):
#     raise NotImplementedError
#
#
# def learn(msg):
#     raise NotImplementedError
#
#
# def resubmit(msg, port, table, ct):
#     raise NotImplementedError
#
#
# def clone(msg):
#     raise NotImplementedError
