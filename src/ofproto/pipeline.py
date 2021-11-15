"""
A module for reproducing OpenFlow pipelining.

``apply_pipeline`` can perform OpenFlow pipeline processing.
"""
import copy
from logging import getLogger, setLoggerClass, Logger

from pyof.foundation.basic_types import UBInt32
from pyof.v0x04.common.header import Type
from pyof.v0x04.common.port import PortNo

from src.tracing_net.ofproto.table import FlowTables
from src.tracing_net.ofproto.msg import Msg
from src.tracing_net.ofproto.action import ActionSet
from src.ofproto.msg import MsgForOFMsg

# analyzerに依存しているので変更するのもあり
from src.analyzer.packet_trace import PacketProcessing

from src.config import conf


setLoggerClass(Logger)
logger = getLogger('tracing_of_pipeline.pipeline')


def apply_pipeline(msg, flowtables):
    """apply flow table to msg

    Args:
        msg (Msg) :
        flowtables (FlowTables) :

    Returns:
        dict : pipeline result.
            * dict["port_to_msg"] is list[tuple[port, Msg]] (outport, msg).
            * dict["packet_processing"] is packet_processing

    TODO:
        * output logger
        * todo Floodingなどは，analyzerに問い合わせるしか無い．
    """
    if not isinstance(msg, Msg):
        raise TypeError("{} not supported, should be Msg".format(type(msg)))
    if not isinstance(flowtables, FlowTables):
        raise TypeError("{} not supported, should be FlowTables".format(type(flowtables)))

    action_set = ActionSet()
    out_ports = []
    # first table is 0
    next_table = 0

    packet_processing = PacketProcessing(switch=flowtables.switch_name, flow_table=flowtables)

    if conf.OUTPUT_APPLY_PIPELINE_PROCESSING_TO_LOGFILE:
        logger.debug("msg{} apply pipeline {}".format(msg, flowtables))

    # PIPELINE processing
    while next_table is not None:
        msg = copy.deepcopy(msg)
        # analyzed table
        current_table = next_table

        # matched flow
        flow = flowtables.match(msg, current_table)

        if flow:  # Is matching flow?
            # applied action set
            result = flow.action(msg, action_set)

            if conf.OUTPUT_APPLY_PIPELINE_PROCESSING_TO_LOGFILE:
                logger.debug("result{} of action that msg{} is applied ".format(result, msg))

            packet_processing.add_msg(result.msg, table_id=current_table)
            packet_processing.add_flowentry(flow.flow_id)

            # update out_ports and next table
            for p in result.out_ports:
                out_ports.append((p, msg))
            if result.table_id is not None and result.table_id > current_table:
                next_table = result.table_id
            else:
                next_table = None
        else:  # no match
            # default action drop
            if conf.OUTPUT_APPLY_PIPELINE_PROCESSING_TO_LOGFILE:
                logger.debug("No match")
            next_table = None

    # exec ActionSet
    msg = copy.deepcopy(msg)
    result = action_set.action(msg)
    for p in result.out_ports:
        out_ports.append((p, msg))
    packet_processing.action_set = action_set
    packet_processing.packet_after_action_set = msg
    packet_processing.outport2msg = out_ports

    return {"port_to_msg": out_ports, "packet_processing": packet_processing}


def apply_pipeline_for_packetout(packet_msg: MsgForOFMsg, **params):
    """apply flow table to msg

    Args:
        packet_msg (MsgForOFMsg) :

    Returns:
        dict : pipeline result.
            * dict["port_to_msg"] is list[tuple[port, Msg]] (port, msg).

    todo:
        * msgをdeep_copyする
        * output以外に対応させる
    """
    outports = []

    # port convert
    if isinstance(packet_msg.of_msg.actions[0].port, UBInt32):
        # port is specific port? (e.g. OFPP_FLOOD)
        tmp_port = int(packet_msg.of_msg.actions[0].port)

        if tmp_port in list(PortNo):
            outports.append((PortNo(tmp_port), packet_msg))
        else:
            outports.append((tmp_port, packet_msg))

    return {"port_to_msg": outports}


