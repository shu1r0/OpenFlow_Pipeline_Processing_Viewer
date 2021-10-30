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
        self.index = 0

    def append(self, trace):
        self.traces.append(trace)
        logger.debug("{} : {}".format(trace.arcs[0].timestamp, trace))

    def save_to_file(self):
        raise NotImplementedError

    def print(self):
        self.traces.sort()
        for trace in self.traces:
            print(str(trace))

    def pop_protobuf_message(self):
        """

        Returns:
            list[net_pb2.PacketTrace]
        """
        traces = []
        if len(self.traces) > self.index + 1:
            for t in self.traces[self.index:]:
                traces.append(t.get_protobuf_message())
            self.index = len(self.traces) + 1
        return traces


packet_trace_list = PacketTraceList()
