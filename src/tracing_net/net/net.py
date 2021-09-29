"""
Mininet wrapper

Todo:
    * decide whether to use the old API or use the new API
"""

import asyncio
from logging import getLogger, setLoggerClass, Logger
import datetime
import threading

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController, Switch, OVSSwitch, Host
from mininet.link import Link
from mininet.log import setLogLevel


from src.tracing_net.api.grpc_server import TracerNetServer
from src.tracing_net.flowtable.flow_table_manager import FlowTableManager
from src.tracing_net.packet.packet_capture_manager import PacketCaptureManager
from src.config import conf
from .cli import TracingCLI

setLoggerClass(Logger)
logger = getLogger('tracing_net.net')


class Links:
    """Links.
    This has a dict maps edges to link obj
    """

    def __init__(self):
        self.links = {}

    def get(self, name):
        return self.links[name]

    def add(self, name, link):
        self.links[name] = link

    def pop(self, name):
        return self.links.pop(name)

    def get_int_name_pairs(self, link_name):
        """get link pair dict

        Returns:
            (str, str) :
        """
        link = self.get(link_name)
        return link.intf1.name, link.intf2.name

    def get_edges(self):
        """get edges

        Returns:
            list[str]
        """
        return list(self.links.keys())

    def get_next_and_edge(self, interface):
        """get next node, interface, edge name

        Args:
            interface (str) :

        Returns:
            (str, str, str) : interface, edge name
        """
        for n, l in self.links.items():
            if l.intf1.name == interface:
                return l.intf2.node.name, l.intf2.name, n
            elif l.intf2.name == interface:
                return l.intf1.node.name, l.intf1.name, n
        return None


class OnDemandNet(Mininet):
    """On-demand Net

    This provides APIs for access by external application
    and templates for launching mininet.
    APIs are designed to be controlled by the name of the host.

    Attributes:
        of_controller (RemoteController) : openflow controller
        name_to_link (dict[str, Link]) : links dict
    """

    def __init__(self, controller_ip=None, controller_port=None, switch_cls=OVSSwitch, mininet_log_level='info'):
        super().__init__(switch=switch_cls)
        if controller_ip is not None and controller_port is not None:
            self.of_controller = self.add_remote_controller('c0', controller_ip, controller_port)
        logger.info("set up on-demand mininet")
        setLogLevel(mininet_log_level)
        self.name_to_link = Links()
        # self.db_schema = ""

    def add_switch(self, name, cls=OVSSwitch, dpid=None, listenPort=None):
        """add switch (new mininet interface)

        Args:
            name (str) : new switch name
            cls (Switch) : switch class
            dpid (int) : 16 bit dpid

        Returns:
            Union[Switch, None] :
        """
        if not self.is_node(name):
            logger.debug("added the switch ({})".format(name))
            params = {}
            if dpid:
                params['dpid'] = dpid
            added_switch = self.addSwitch(name, cls=cls, **params)
            return added_switch
        else:
            raise NameError("The switch's name already exists")

    def addSwitch(self, name, cls=None, **params):
        """For compatibility"""
        added_switch = super().addSwitch(name, cls=cls, **params)
        added_switch.start([self.of_controller])
        return added_switch

    def remove_switch(self, name):
        """remove switch (new mininet interface)

        Args:
            name (str) : removed switch

        Returns:
            Union[Switch, None] :
        """
        if self.is_node(name):
            logger.debug("removed the switch ({})".format(name))
            removed_switch = self.getNodeByName(name)
            self.delSwitch(removed_switch)
            self.topology_changed()
            return removed_switch
        else:
            raise NameError("There is no switch with such the name.")

    def add_host(self, name, ip=None, mac=None):
        """add host (new mininet interface)

        Args:
            name (str) :

        Returns:
            Union[Host, None] :
        """
        if not self.is_node(name):
            params = {}
            if ip:
                params['ip'] = ip
            if mac:
                params['mac'] = mac
            logger.debug("added the host ({})".format(name))
            added_host = self.addHost(name, **params)
            # added_host = self.addHost(name)
            return added_host
        else:
            raise NameError("The host's name already exists")

    def remove_host(self, name):
        """remove host (new mininet interface)

        Args:
            name (str) : removed host

        Returns:
            Union[Host, None] :
        """
        if self.is_node(name):
            logger.debug("removed the host ({})".format(name))
            removed_host = self.getNodeByName(name)
            self.delHost(removed_host)
            return removed_host
        else:
            raise NameError("There is no host with such the name.")

    def add_link(self, link_name, host_name1, host_name2):
        """add new link (new mininet interface)

        Args:
            link_name (str) : new link name
            host_name1 (str or Node) : host 1
            host_name2 (str or Node) : host 2

        Returns:
            Link : added link

        Raises:
            NameError
        """
        if not self.is_link(link_name):
            logger.debug("added the link ({}) between {} and {}".format(link_name, host_name1, host_name2))
            added_link = self.addLink(host_name1, host_name2, link_name=link_name)
            return added_link
        else:
            raise NameError("The link's name already exists")

    def addLink(self, node1, node2, port1=None, port2=None, cls=None, link_name=None, **params):
        """For compatibility"""
        added_link = super().addLink(node1, node2, port1=port1, port2=port2, cls=cls, **params)
        self.topology_changed()
        link_name = link_name if link_name is not None else "e" + str(node1) + str(node2)
        self.name_to_link.add(link_name, added_link)
        return added_link

    def remove_link(self, link_name):
        """remove link (new mininet interface)

        Args:
            link_name (str) :

        Returns:
            Union[Link, None] : removed link or None
        """
        if self.is_link(link_name):
            logger.debug("removed the link ({})".format(link_name))
            removed_link = self.name_to_link.get(link_name)
            self.delLink(removed_link, link_name=link_name)
            return removed_link
        else:
            raise NameError("There is no link with such the name.")

    def delLink(self, link, link_name=None):
        """For compatibility"""
        super().delLink(link)
        if link_name is None:
            link_name = [n for (n, l) in self.name_to_link.links.items() if l == link][0]
        removed_link = self.name_to_link.pop(link_name)
        self.topology_changed()

    def remove_link_between(self, host_name1, host_name2):
        """remove first link between name1 and name2

        This calls self.remove_link()

        Args:
            host_name1 (str) :
            host_name2 (str) :

        Returns:
            Union[Link, None] : removed link or None
        """
        if self.is_node(host_name1) and self.is_node(host_name2):
            h1 = self.getNodeByName(host_name1)
            h2 = self.getNodeByName(host_name2)
            link = self.get_link_between(h1, h2)
            if link:
                removed_link = self.remove_link(self.get_link_name(link))
                return removed_link
        else:
            raise NameError("There is no link with such the name.")

    def get_host_names(self):
        """get list of host name

        Returns:
            list[str] : list of host name
        """
        return [h.name for h in self.hosts]

    def set_ofport(self, interface_obj):
        raise NotImplementedError

    @property
    def node_name_pairs_for_links(self):
        """get link pair dict

        Returns:
            dict[str, (str, str)] :
        """
        name_pairs = {}
        for (name, link) in self.name_to_link.links:
            name_pairs[name] = (link.intf1.node.name, link.intf2.node.name)
        return name_pairs

    def add_remote_controller(self, name, ip, port):
        """add remote controller

        Args:
            name (str) :
            ip (str) :
            port (str) :

        Returns:
            RemoteController : mininet RemoteController
        """
        return self.addController(name, controller=RemoteController, ip=ip, port=port)

    def exec_cmd(self, host_name, cmd):
        """exec command on host

        Args:
            host_name (str) : host name
            cmd (str) : exec command
        """
        host = self.getNodeByName(host_name)
        host.cmd(cmd)

    def start(self):
        """mininet start"""
        logger.info("mininet start")
        super().start()

    def stop(self):
        """mininet stop"""
        logger.info("mininet stop")
        super().stop()

    def is_node(self, name):
        """Is the node in mininet?

        Args:
            name (str) :

        Returns:
            bool
        """
        try:
            return self.getNodeByName(name) is not None
        except KeyError as e:
            return False

    def is_switch(self, name):
        """Is the switch in mininet?

        Args:
            name (str) :

        Returns:
            bool
        """
        try:
            return isinstance(self.getNodeByName(name), OVSSwitch)
        except KeyError as e:
            return False

    def is_link(self, name):
        """Is the link in mininet?

        Args:
            name (str) :

        Returns:
            bool
        """
        return name in self.name_to_link.links.keys()

    def is_link_between(self, host1, host2):
        """

        Args:
            host1 (str) :
            host2 (str) :

        Returns:
            bool
        """
        return self.get_link_between(host1, host2) is not None

    def get_link_between(self, host1, host2):
        """

        Args:
            host1 (str) :
            host2 (str) :

        Returns:
            Union[Link, None] :
        """
        if self.is_link_between(host1, host2):
            link = self.linksBetween(host1, host2)[0]
            return link
        else:
            return None

    def get_link_name(self, link):
        """get link name by link obj

        Args:
            link (Link) : link

        Returns:
            Union[str, None] : link name
        """
        links = [link_name for link_name, link_value in self.name_to_link.links.items() if link_value == link]
        if len(links) != 0:
            return links[0]
        else:
            return None

    def topology_changed(self):
        """This will be called when a link changes
        """
        self.configHosts()
        for switch in self.switches:
            switch.start([self.of_controller])

    def get_topo(self):
        """get topology

        Returns:
            (dict, dict) : name to node, name to link
        """
        return self.nameToNode, self.name_to_link.links

    def get_datapath_id(self, switch):
        datapath = self.getNodeByName(switch)
        if isinstance(datapath, Switch):
            return datapath.dpid

    def get_switch_names(self):
        names = []
        for name, node in self.nameToNode.items():
            if isinstance(node, OVSSwitch):
                names.append(name)
        return names

    def is_terminal_edge(self, edge):
        link = self.name_to_link.get(edge)
        node1 = link.intf1.node
        node2 = link.intf2.node
        if isinstance(node1, Host) or isinstance(node2, Host):
            return True
        else:
            return False

    def get_terminal_edge(self, edge):
        """get host and switch

        Args:
            edge (str) : edge name

        Returns:
            str, str, str : Host, Switch, switch intf
        """
        link = self.name_to_link.get(edge)
        node1 = link.intf1.node
        node2 = link.intf2.node
        if isinstance(node1, Host):
            return node1.name, node2.name, link.intf2.name
        elif isinstance(node2, Host):
            return node2.name, node1.name, link.intf1.name

    def get_ofport_from_interface(self, switch, interface_name):
        intf = self.get(switch).nameToIntf[interface_name]
        return self.get(switch).ports[intf]

    def get_interface_from_ofport(self, switch, ofport):
        return self.get(switch).intfs[ofport].name

    def get_interface_from_link(self, link):
        return self.name_to_link.get_int_name_pairs(link)[0]


class TracingNet(OnDemandNet):
    """trace OpenFlow network

    * packet capture
    * monitor flow

    Attributes:
        grpc_server (TracerNetServer) : grpc server
    """

    def __init__(self, controller_ip='127.0.0.1', controller_port=63333, mininet_log_level='info'):
        super(TracingNet, self).__init__(controller_ip=controller_ip, controller_port=controller_port, mininet_log_level=mininet_log_level)
        self.event_loop = asyncio.get_event_loop()
        self.grpc_server = TracerNetServer(self)
        self.table_manager = FlowTableManager(event_loop=self.event_loop)
        self.capture_manager = PacketCaptureManager(self.name_to_link, event_loop=self.event_loop)
        self.has_been_tracing = False

    def add_switch(self, name, cls=OVSSwitch, dpid=None, listenPort=None):
        if self.has_been_tracing:
            raise Exception("Cannot change network while tracing")
        return super(TracingNet, self).add_switch(name, cls=cls, dpid=dpid, listenPort=listenPort)

    def remove_switch(self, name):
        if self.has_been_tracing:
            raise Exception("Cannot change network while tracing")
        return super(TracingNet, self).remove_switch(name)

    def add_host(self, name, ip=None, mac=None):
        if self.has_been_tracing:
            raise Exception("Cannot change network while tracing")
        return super(TracingNet, self).add_host(name, ip=ip, mac=mac)

    def remove_host(self, name):
        if self.has_been_tracing:
            raise Exception("Cannot change network while tracing")
        return super(TracingNet, self).remove_host(name)

    def add_link(self, link_name, host_name1, host_name2):
        if self.has_been_tracing:
            raise Exception("Cannot change network while tracing")
        return super(TracingNet, self).add_link(link_name, host_name1, host_name2)

    def remove_link(self, link_name):
        if self.has_been_tracing:
            raise Exception("Cannot change network while tracing")
        return super(TracingNet, self).remove_link(link_name)

    def remove_link_between(self, host_name1, host_name2):
        if self.has_been_tracing:
            raise Exception("Cannot change network while tracing")
        return super(TracingNet, self).remove_link_between(host_name1, host_name2)

    def start_tracing(self):
        """start tracing"""
        if conf.DISABLE_IPV6:
            logger.debug("desable ipv6")
            for node in self.nameToNode.values():
                node.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
                node.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
                node.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

        self.has_been_tracing = True
        edges = self.name_to_link.get_edges()
        switches = self.switches
        self.capture_manager.start_captures(edges)
        self.table_manager.start_pollers(switches)

    def stop_tracing(self):
        """start tracing"""
        self.has_been_tracing = False
        self.capture_manager.stop_all_captures()
        self.table_manager.stop_all_poller()

    def stop(self):
        """stop mininet and close processes"""
        self.stop_tracing()
        super().stop()
        logger.debug("mininet stopped and all capture processes closed")

    def grpc_server_start(self):
        """gRPC API Server start"""
        self.grpc_server.start()

    def grpc_server_stop(self):
        """gRPC API Server stop"""
        self.grpc_server.stop()

    def cli_run(self):
        # cli_thread = threading.Thread(name="cli", target=CLI, args=(self,))
        # cli_thread.start()
        # cli_thread.join()
        TracingCLI(self)

    def packet_repo(self):
        """alias to the packet repository"""
        return self.capture_manager.repository

    def table_repo(self):
        """alias to the table repository"""
        return self.table_manager.repository
