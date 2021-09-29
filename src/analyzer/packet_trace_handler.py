from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger


setLoggerClass(Logger)
logger = getLogger('tracing_of_pipeline.packet_trace_handler')


class AbstractPacketTraceList(metaclass=ABCMeta):
    """A Abstract Class to store packet trace

    This class recives the computed packet routes.
    """

    def __init__(self):
        self.traces = []

    @abstractmethod
    def append(self, trace):
        raise NotImplementedError


class PacketTraceList(AbstractPacketTraceList):

    def __init__(self):
        super(PacketTraceList, self).__init__()

    def append(self, trace):
        self.traces.append(trace)
        logger.debug("{} : {}".format(trace.arcs[0].timestamp, trace))

    def save_to_file(self):
        raise NotImplementedError

    def print(self):
        print(self.traces)


packet_trace_list = PacketTraceList()
