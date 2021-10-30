from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger


setLoggerClass(Logger)
logger = getLogger('tracing_net.packet_repository')


class AbstractPacketRepository(metaclass=ABCMeta):
    """An abstract repository for packets"""

    def __init__(self):
        self.repository = {}

    @abstractmethod
    def add(self, interface, msg):
        """add message to this repository

        Args:
            interface (str) : interface name
            msg (Msg) : packet message
        """
        raise NotImplementedError

    @abstractmethod
    def pop(self, interface, until=None, count=None):
        """

        Args:
            interface (str) : interface name
            until (float) : unix timestamp
            count (int) :
        """
        raise NotImplementedError


class PacketRepository(AbstractPacketRepository):
    """A repository for packets"""

    def __init__(self):
        super(PacketRepository, self).__init__()

    def add(self, interface, msg):
        """

        Args:
            interface (str) :
            msg (Msg) :
        """
        self.repository.setdefault(interface, [])
        self.repository[interface].append(msg)
        # logger.debug("added msg {} to packet repo {}".format(msg, self.repository))

    def pop(self, interface, until=None, count=None):
        """

        Args:
            interface (str) :
            until (timestamp) :
            count (int) :

        Returns:
            list[Msg] :
        """
        try:
            if until is not None:
                return self._pop_until(interface, until)
            elif count is not None:
                return self._pop_count(interface, count)
            else:
                return self._pop(interface)
        except KeyError:
            logger.error("Failed to pop from packet repository (repo={})".format(self.repository))
            return None

    def _pop(self, interface):
        return self.repository.pop(interface)

    def _pop_until(self, interface, until):
        tmp_i = []
        packets = self.repository[interface]
        for i in range(len(packets)):
            if packets[i].sniff_timestamp < until:
                tmp_i.append(i)
        tmp = []
        for i in tmp_i[::-1]:
            tmp.insert(0, packets.pop(i))
        return tmp

    def _pop_count(self, interface, count):
        tmp_i = []
        packets = self.repository[interface]
        for i in range(min(len(packets), count)):
                tmp_i.append(i)
        tmp = []
        for i in tmp_i[::-1]:
            tmp.insert(0, packets.pop(i))
        return tmp


packet_repository = PacketRepository()
