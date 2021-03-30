#!/usr/bin/env python

"""
multiping.py: monitor multiple sets of hosts using ping
This demonstrates how one may send a simple shell script to
multiple hosts and monitor their output interactively for a period=
of time.
"""

from select import poll, POLLIN
from time import time

from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import SingleSwitchTopo
from mininet.log import info, setLogLevel


def chunks(l, n):
    """Divide list l into chunks of size n - thanks Stackoverflow

    Args:
        l:
        n:

    Returns:

    """
    return [l[i: i+n] for i in range(0, len(l), n)]


def start_pings(host, target_ips):
    """Tell host to repeatedly ping targets

    Args:
        host:
        targetips:

    Returns:

    """
    target_ips = ' '.join(target_ips)
    # Simple ping loop
    cmd = ('while true; do '
           ' for ip in %s; do ' % target_ips +
           '  echo -n %s "->" $ip ' % host.IP() +
           '   `ping -c1 -w 1 $ip | grep packets` ;'
           '  sleep 1;'
           ' done; '
           'done &')
    info('*** Host %s (%s) will be pinging ips: %s\n' %
         (host.name, host.IP(), target_ips))
    host.cmd(cmd)


def multi_ping(netsize, chunksize, seconds):
    """Ping subsets of size chunksize in net of size netsize

    Args:
        netsize (int) : ネットワーク
        chunksize (int) :
        seconds (int) :

    Returns:

    """
    # Create network and identify subnets
    topo = SingleSwitchTopo(netsize)
    net = Mininet(topo=topo, waitConnected=True)
    net.start()
    hosts = net.hosts
    subnets = chunks(hosts, chunksize)

    # Create polling object
    fds = [host.stdout.fileno() for host in hosts]
    # generate polling obj
    poller = poll()
    for fd in fds:
        # 呼び出し可能なデータが存在するとイベントが発生
        poller.register(fd, POLLIN)

    # Start pings
    for subnet in subnets:
        ips = [host.IP() for host in subnet]
        # adding bogus to generate packet loss
        ips.append('10.0.0.200')
        for host in subnet:
            start_pings(host, ips)

    # Monitor output
    end_time = time() + seconds
    while time() < end_time:
        # イベントを待機する
        readable = poller.poll(1000)
        # Taple(fd(ファイル記述子), event)
        for fd, _mask in readable:
            node = Node.outToNode[fd]
            # strip() => 両端の*空白文字*を消す
            info('%s:' % node.name, node.monitor().strip(), '\n')

    # Stop pings
    for host in hosts:
        host.cmd('kill %while')

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    multi_ping(netsize=20, chunksize=4, seconds=10)
