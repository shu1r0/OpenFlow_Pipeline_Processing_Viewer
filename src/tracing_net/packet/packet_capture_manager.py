import datetime
import multiprocessing
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from src.tracing_net.packet.packet_capture import PacketCapture
from .packet_repository import packet_repository


setLoggerClass(Logger)
logger = getLogger('tracing_net.packet_capture_manager')


class AbstractPacketCaptureManager(metaclass=ABCMeta):
    """An Abstract Class Managing the PacketCapture class"""

    def __init__(self, repository):
        """

        Args:
            repository (PacketRepository) : repository for packet
        """
        self.repository = repository

    @abstractmethod
    def start_capture(self, edge):
        """start packet capture on edge

        Args:
            edge (str) : edge name
        """
        raise NotImplementedError

    @abstractmethod
    def start_captures(self, edges):
        """start packet capture on edges

        Args:
            edges (list[str]) : edges
        """
        raise NotImplementedError

    @abstractmethod
    def stop_capture(self, edge):
        """stop packet capture on edge

        Args:
            edge (str) : edge name
        """
        raise NotImplementedError

    @abstractmethod
    def stop_all_captures(self):
        """stop packet capture on all edges"""
        raise NotImplementedError

    @abstractmethod
    def is_capturing(self, edge):
        """Is this capturing on the edge

        Args:
            edge (str) :
        """
        raise NotImplementedError


class PacketCaptureManager(AbstractPacketCaptureManager):
    """A Class Managing the PacketCapture class

    Todo:
        * 辺と頂点の関連付けを行う
    """

    def __init__(self, links, event_loop=None):
        super(PacketCaptureManager, self).__init__(packet_repository)
        self.links = links
        self.event_loop = event_loop
        self.captures = {}

    def start_capture(self, edge):
        interface = self._get_int(edge)
        process = self._create_packet_capture_process(interface)
        logger.debug("capture process ({}:{}) started".format(interface, process.pid))
        process.start()

    def start_captures(self, edges):
        for edge in edges:
            self.start_capture(edge)

    def _create_packet_capture_process(self, interface_name):
        """return packet capture process

        Args:
            interface_name (str) : target interface

        Returns:
            Process : packet capture process
        """
        date = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_name = 'log/pcap/' + interface_name + '-' + date + '.pcap'
        capture = PacketCapture(interface_name, self.repository, file_name, event_loop=self.event_loop)
        p = multiprocessing.Process(target=capture.start_capture)
        p.daemon = True
        self.captures[interface_name] = p
        return p

    def stop_capture(self, edge):
        interface = self._get_int(edge)
        self.captures[interface].terminate()
        logger.debug("capture process ({}:{}) terminated".format(interface, self.captures[interface].pid))

    def stop_all_captures(self):
        for edge in self.links.links.keys():
            self.stop_capture(edge)

    def is_capturing(self, edge):
        interface = self._get_int(edge)
        raise NotImplementedError

    def _get_int(self, edge):
        return self.links.get_int_name_pairs(edge)[0]
