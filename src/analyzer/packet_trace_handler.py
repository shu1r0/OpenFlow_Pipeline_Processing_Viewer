import datetime
import yaml
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from src.config import conf
from src.analyzer.packet_trace import PacketTrace, get_packet_trace_id


setLoggerClass(Logger)
logger = getLogger('tracing_of_pipeline.packet_trace_handler')


class AbstractPacketTraceList(metaclass=ABCMeta):
    """A Abstract Class to store packet trace

    This class recives the computed packet routes.
    """

    def __init__(self):
        self.traces: list[PacketTrace] = []

    @abstractmethod
    def append(self, trace):
        raise NotImplementedError


class PacketTraceList(AbstractPacketTraceList):
    """Packet Trace Repository

    Notes:
        * This list is not order
    """

    def __init__(self):
        super(PacketTraceList, self).__init__()
        # pop trace max id
        self._max_id = -1

    def append(self, trace: PacketTrace):
        trace.packet_trace_id = get_packet_trace_id()
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

        todo:
            * packet trace idを決めた
        """
        traces = []
        max = self._max_id
        for t in self.traces:
            if t.packet_trace_id > self._max_id:
                traces.append(t.get_protobuf_message())
                if t.packet_trace_id > max:
                    max = t.packet_trace_id
        self._max_id = max
        return traces

    def output(self):
        file_name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + "-" + "flowtable" + ".yaml"
        file_path = conf.PACKET_PROCESSING_DIRECTORY + file_name
        with open(file_path, 'w') as f:
            f.write(yaml.dump([trace.to_dict() for trace in self.traces]))


id_base = -1
def default_id():
    global id_base
    id_base += 1
    return id_base


packet_trace_list = PacketTraceList()
