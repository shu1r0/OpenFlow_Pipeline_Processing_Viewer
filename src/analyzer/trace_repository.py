# from abc import ABCMeta, abstractmethod
# from logging import getLogger, setLoggerClass, Logger
#
#
# setLoggerClass(Logger)
# logger = getLogger('tracing_of_pipeline.trace_repository')
#
#
# class AbstractPacketTraceRepository(metaclass=ABCMeta):
#
#     def __init__(self):
#         self.repository = []
#
#     @abstractmethod
#     def add(self, trace):
#         raise NotImplementedError
#
#
# class PacketTraceRepository(AbstractPacketTraceRepository):
#
#     def __init__(self):
#         super(PacketTraceRepository, self).__init__()
#
#     def add(self, trace):
#         self.repository.append(trace)
#         logger.debug("{} : {}".format(trace.arcs[0].timestamp, trace))
#
#     def save_to_file(self):
#         raise NotImplementedError
#
#     def print(self):
#         print(self.repository)
#
#
# packet_trace_repository = PacketTraceRepository()
