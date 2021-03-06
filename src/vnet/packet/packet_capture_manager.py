import datetime
import multiprocessing
import threading
import asyncio
from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger

from src.vnet.packet.packet_capture import PacketCapture
from .packet_repository import packet_repository


setLoggerClass(Logger)
logger = getLogger('vnet.packet_capture_manager')


class AbstractPacketCaptureManager(metaclass=ABCMeta):
    """An Abstract Class Managing the PacketCapture class"""

    def __init__(self, repository):
        """

        Args:
            repository (PacketRepository) : repository for packet
        """
        self.repository = repository
        self.pcap_file: str or None = None

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

    def __init__(self, links, event_loop=None, packet_to_pcap_file=True, pacp_file_directory='log/pcap/'):
        super(PacketCaptureManager, self).__init__(packet_repository)
        self.links = links
        self.event_loop = event_loop
        self.captures = {}
        self.packet_to_pcap_file = packet_to_pcap_file
        self.pcap_file_directory = pacp_file_directory

    def start_capture(self, edge):
        interface = self.links.get_primary_interface(edge)
        process = self._create_packet_capture_process(interface, edge)
        process.start()
        logger.debug("capture process (intf={} edge={} processid={}) started".format(interface, edge, process.pid))

    def start_captures(self, edges):
        for edge in edges:
            self.start_capture(edge)

    def _create_packet_capture_process(self, interface_name, edge):
        """return packet capture process

        Args:
            interface_name (str) : target interface
            edge (str) : edge

        Returns:
            Process : packet capture process
        """
        if self.packet_to_pcap_file:
            date = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            self.pcap_file = self.pcap_file_directory + interface_name + '-' + date + '.pcap'
        parent_conn, child_conn = multiprocessing.Pipe()
        capture = PacketCapture(interface_name, edge, parent_conn, output_file=self.pcap_file, event_loop=self.event_loop)

        # server stop??
        p = multiprocessing.Process(target=capture.start_capture, daemon=True)
        t = threading.Thread(target=self._receive_data, args=(child_conn,))
        t.daemon = True
        t.start()
        p.daemon = True
        self.captures[interface_name] = p
        return p

    def stop_capture(self, edge):
        interface = self.links.get_primary_interface(edge)
        self.captures[interface].terminate()
        logger.debug("capture process ({}:{}) terminated".format(interface, self.captures[interface].pid))

    def stop_all_captures(self):
        for edge in self.links.links.keys():
            self.stop_capture(edge)

    def is_capturing(self, edge):
        raise NotImplementedError

    def _receive_data(self, child_conn):
        while True:
            try:
                data = child_conn.recv()
                self.repository.add(*data)
            except EOFError:
                break
