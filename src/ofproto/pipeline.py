"""
A module for reproducing OpenFlow pipelining.

``apply_pipeline`` can perform OpenFlow pipeline processing.
"""
import copy
from logging import getLogger, setLoggerClass, Logger

from src.tracing_net.ofproto.table import FlowTables
from src.tracing_net.ofproto.msg import Msg
from src.tracing_net.ofproto.action import ActionSet


setLoggerClass(Logger)
logger = getLogger('tracing_of_pipeline.pipeline')


def apply_pipeline(msg, flowtables):
    """apply flow table to msg

    Args:
        msg (Msg) :
        flowtables (FlowTables) :

    Returns:
        list[tuple[port, Msg]]: msg, outports
    """
    if not isinstance(msg, Msg):
        raise TypeError("{} not supported, should be Msg".format(type(msg)))
    if not isinstance(flowtables, FlowTables):
        raise TypeError("{} not supported, should be FlowTables".format(type(flowtables)))

    action_set = ActionSet()
    out_ports = []
    next_table = 0

    while next_table is not None:
        msg = copy.deepcopy(msg)
        current_table = next_table

        flow = flowtables.match(msg, current_table)

        if flow:  # Is matching flow?
            result = flow.action(msg, action_set)
            logger.debug("action result={} msg={}".format(result, msg))
            for p in result.out_ports:
                out_ports.append((p, msg))
            if result.table_id is not None and result.table_id > current_table:
                next_table = result.table_id
            else:
                next_table = None
        else:  # no match
            # default action drop
            logger.debug("No match")
            next_table = None

    # TODO: exec ActionSet

    return out_ports


def apply_pipeline_for_packetout():
    """apply flow table to msg

    Args:
        msg (Msg) :
        flowtables (FlowTables) :

    Returns:
        list[tuple[port, Msg]]: msg, outports
    """



