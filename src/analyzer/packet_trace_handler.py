import datetime
import yaml
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from src.config import conf


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
        # pop trace max id
        self._max_id = -1

    def append(self, trace):
        trace.id = default_id()
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
            if t.id > self._max_id:
                traces.append(t.get_protobuf_message())
                if t.id > max:
                    max = t.id
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
