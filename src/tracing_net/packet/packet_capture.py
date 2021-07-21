from abc import ABCMeta, abstractmethod
import pyshark
import asyncio
import datetime
from logging import getLogger, setLoggerClass, Logger

from scapy.all import wrpcap
from pyshark.packet.packet import Packet
from src.tracing_net.ofproto.msg import Msg

setLoggerClass(Logger)
logger = getLogger('tracing_net.util.packet_capture')


class Capture(metaclass=ABCMeta):
    """This captures packet in mininet. The packets saved in packet repository.

    Attributes:
        parent_conn (Connection) : parent_conn
    """

    def __init__(self, parent_conn):
        self.parent_conn = parent_conn

    @abstractmethod
    def start_capture(self):
        """start packet capture"""
        raise NotImplementedError


class PacketCapture(Capture):
    """packet capture and print dict

    Attributes:
        interface (str)
        event_loop (asyncio.events.AbstractEventLoop)
        capture (pyshark.LiveCapture)
    """

    def __init__(self, interface, parent_conn, output_file=None, event_loop=None):
        """init

        Args:
            interface (str) : interface name
            output_file (str) : output pcap file name
        """
        super(PacketCapture, self).__init__(parent_conn)
        self.interface = interface
        self.event_loop = event_loop if event_loop is not None else asyncio.get_event_loop()
        self._output_file = output_file
        self.capture = pyshark.LiveCapture(interface=self.interface, eventloop=self.event_loop, use_json=True, include_raw=True)

    def start_capture(self):
        """packet capture run"""
        try:
            logger.info("capture start on {}".format(self.interface))
            coroutine = self._get_packet_handler_coro()
            self.event_loop.run_until_complete(coroutine)
        except KeyboardInterrupt as e:
            logger.info("finish capture on {}".format(self.interface))

    def _get_packet_handler_coro(self):
        return self.capture.packets_from_tshark(self._packet_handler)

    def _packet_handler(self, pkt):
        """store to repository
        If output file is not None, the packet is written in pcap file.

        Args:
            pkt (Packet) : packet
        """
        logger.debug("sniff {} : {}".format(pkt.sniff_timestamp, pkt.__class__))
        self.parent_conn.send([self.interface, Msg(self.interface, float(pkt.sniff_timestamp), pkt)])
        # self.parent_conn.send(1)
        if self._output_file:
            wrpcap(self._output_file, pkt.get_raw_packet(), append=True)



if __name__ == '__main__':
    output_file = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.pcap')
    capture = PacketCapture("en0", output_file)
    capture.start()