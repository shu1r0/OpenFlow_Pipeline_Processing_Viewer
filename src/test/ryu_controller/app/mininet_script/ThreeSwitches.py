# coding: utf-8

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, UserSwitch
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI

from functools import partial

class Three_switches_topo(Topo):
    def build(self, n=5):
        s1 = self.addSwitch('s1', cls=UserSwitch)
        s2 = self.addSwitch('s2', cls=UserSwitch)
        s3 = self.addSwitch('s3', cls=UserSwitch)
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        # self.addLink(s1, s3)
        for i in range(n):
            host = self.addHost('h{}'.format(i+1))
            self.addLink(host, s1)
            host = self.addHost('h{}'.format(i+1+n))
            self.addLink(host, s2)
            host = self.addHost('h{}'.format(i+1+n*2))
            self.addLink(host, s3)

def setup():
    topo = Three_switches_topo(n=5)
    net = Mininet(topo=topo, controller=partial(RemoteController, ip='127.0.0.1', port=6633), switch=UserSwitch)
    net.start()
    dumpNodeConnections(net.hosts)
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setup()