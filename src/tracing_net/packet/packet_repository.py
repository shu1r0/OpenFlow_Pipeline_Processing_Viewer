from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger


setLoggerClass(Logger)
logger = getLogger('tracing_net.packet_repository')


class AbstractPacketRepository(metaclass=ABCMeta):
    """An abstract repository for packets"""

    def __init__(self):
        self.repository = {}

    @abstractmethod
    def add(self, edge, msg):
        """add message to this repository

        Args:
            edge (str) : edge name
            msg (Msg) : packet message
        """
        raise NotImplementedError

    @abstractmethod
    def pop(self, edge, until=None, count=None):
        """

        Args:
            edge (str) : edge name
            until (float) : unix timestamp
            count (int) :
        """
        raise NotImplementedError


class PacketRepository(AbstractPacketRepository):
    """A repository for packets"""

    def __init__(self):
        super(PacketRepository, self).__init__()

    def add(self, edge, msg):
        """

        Args:
            edge (str) :
            msg (Msg) :
        """
        self.repository.setdefault(edge, [])
        self.repository[edge].append(msg)
        logger.debug("added msg {} to packet repo {}".format(msg, self.repository))

    def pop(self, edge, until=None, count=None):
        """

        Args:
            edge (str) :
            until (timestamp) :
            count (int) :

        Returns:
            list[Msg] :
        """
        logger.debug("pop msg from packet repo {}".format(self.repository))
        try:
            if until is not None:
                return self._pop_until(edge, until)
            elif count is not None:
                return self._pop_count(edge, count)
            else:
                return self._pop(edge)
        except KeyError:
            logger.error("Failed to pop from packet repository (repo={})".format(self.repository))
            return None

    def _pop(self, edge):
        return self.repository.pop(edge)

    def _pop_until(self, edge, until):
        tmp = []
        packets = self.repository[edge]
        for i in range(len(packets)):
            if packets[i].sniff_timestamp < until:
                tmp.append(packets.pop(i))
        return tmp

    def _pop_count(self, edge, count):
        tmp = []
        packets = self.repository[edge]
        for i in range(min(len(packets), count)):
            tmp.append(packets.pop(i))
        return tmp


packet_repository = PacketRepository()
