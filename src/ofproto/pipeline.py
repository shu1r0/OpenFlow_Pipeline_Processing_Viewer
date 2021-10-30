"""
A module for reproducing OpenFlow pipelining.

``apply_pipeline`` can perform OpenFlow pipeline processing.
"""
import copy
from logging import getLogger, setLoggerClass, Logger

from src.tracing_net.ofproto.table import FlowTables
from src.tracing_net.ofproto.msg import Msg
from src.tracing_net.ofproto.action import ActionSet

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
            * dict["port_to_msg"] is list[tuple[port, Msg]] (msg, outports).
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

    while next_table is not None:
        msg = copy.deepcopy(msg)
        # analyzed table
        current_table = next_table

        # matched flow
        flow = flowtables.match(msg, current_table)

        if flow:  # Is matching flow?
            # applied action set
            # TODO: (msgの更新は？？？)
            result = flow.action(msg, action_set)

            if conf.OUTPUT_APPLY_PIPELINE_PROCESSING_TO_LOGFILE:
                logger.debug("result{} of action that msg{} is applied ".format(result, msg))

            packet_processing.add_msg(result.msg)
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

    # TODO: exec ActionSet

    return {"port_to_msg": out_ports, "packet_processing": packet_processing}


def apply_pipeline_for_packetout():
    """apply flow table to msg

    Args:
        msg (Msg) :
        flowtables (FlowTables) :

    Returns:
        list[tuple[port, Msg]]: msg, outports
    """
    pass



