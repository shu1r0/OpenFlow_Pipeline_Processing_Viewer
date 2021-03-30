from select import poll
from select import POLLIN
import time

from mininet.net import Mininet
from mininet.node import Node, Host
from mininet.topo import SingleSwitchTopo
from mininet.log import info, setLogLevel


def do_dump_flows(host):
    """`dump_flows`のコマンドを実行

    Args:
        host (:obj:mininet.node.Host) : コマンドを実行するホスト

    Returns:
        None
    """
    cmd = ('while true; do '
           '  echo %s ;' % host.name +
           '  sudo ovs-ofctl dump-flows %s;' % host.name +
           '  sleep 1;' 
           'done &')
    info(host.cmd(cmd))


def monitor_dump_flows(hosts):
    """引数に対して，dump_flowsを実行

    Args:
        hosts (list) : ホストのリスト

    Returns:
        None
    """
    # ファイル記述子(番号)を取得
    fds = [host.stdout.fileno() for host in hosts]
    poller = poll()
    info(poller)
    for fd in fds:
        poller.register(fd, POLLIN)
    # dump_flows
    for host in hosts:
        do_dump_flows(host)
    # Monitor
    end_time = time.time() + 10
    while time.time() < end_time:
        readable = poller.poll(1000)
        info(readable)
        for fd, _event_mask in readable:
            node = Node.outToNode[fd]
            print(('$s: ' % node.name) + node.monitor().strip())
    for host in hosts:
        # whileのジョブを終了
        host.cmd('kill %while')


def create_network():
    topo = SingleSwitchTopo(20)
    net = Mininet(topo=topo, waitConnected=True)
    net.start()
    hosts = net.hosts
    monitor_dump_flows(hosts)
    net.stop()

if __name__ == "__main__":
    setLogLevel('info')
    create_network()



"""
shu@shu-VirtualBox:~$ cd Network/
shu@shu-VirtualBox:~/Network$ ls
 batfish                          'SDN and NFV Simplified.xmind'
 faucet                            switchToSDN
 OpenFlowTutorial_ONS_Heller.pdf   tcpdump
 ryu                               trace_ovs_pipeline
 Ryu.xmind                         TrafficViewerByAnalyzingPacketIn
shu@shu-VirtualBox:~/Network$ cd trace_ovs_pipeline/
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ ls
main.py  mininet  venv
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo python3 mininet/example
example1.py           example_flowdumps.py  
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo python3 mininet/example_flowdumps.py 
[sudo] password for shu: 
*** Creating network
*** Adding controller
Traceback (most recent call last):
  File "mininet/example_flowdumps.py", line 70, in <module>
    create_network()
  File "mininet/example_flowdumps.py", line 62, in create_network
    net = Mininet(topo=topo, waitConnected=True)
  File "/usr/local/lib/python3.8/dist-packages/mininet/net.py", line 178, in __init__
    self.build()
  File "/usr/local/lib/python3.8/dist-packages/mininet/net.py", line 508, in build
    self.buildFromTopo( self.topo )
  File "/usr/local/lib/python3.8/dist-packages/mininet/net.py", line 475, in buildFromTopo
    self.addController( 'c%d' % i, cls )
  File "/usr/local/lib/python3.8/dist-packages/mininet/net.py", line 291, in addController
    controller_new = controller( name, **params )
  File "/usr/local/lib/python3.8/dist-packages/mininet/node.py", line 1593, in DefaultController
    return controller( name, **kwargs )
  File "/usr/local/lib/python3.8/dist-packages/mininet/node.py", line 1417, in __init__
    self.checkListening()
  File "/usr/local/lib/python3.8/dist-packages/mininet/node.py", line 1433, in checkListening
    raise Exception( "Please shut down the controller which is"
Exception: Please shut down the controller which is running on port 6653:
Active Internet connections (servers and established)
tcp        0      0 0.0.0.0:6653            0.0.0.0:*               LISTEN      1129/python3        
tcp        0      0 127.0.0.1:56154         127.0.0.1:6653          TIME_WAIT   -                   
tcp        0      0 127.0.0.1:6653          127.0.0.1:56142         ESTABLISHED 1129/python3        
tcp        0      0 127.0.0.1:56142         127.0.0.1:6653          ESTABLISHED 676/ovs-vswitchd    
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo systemctl stop faucet
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo python3 mininet/example_flowdumps.py 
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) (h4, s1) (h5, s1) (h6, s1) (h7, s1) (h8, s1) (h9, s1) (h10, s1) (h11, s1) (h12, s1) (h13, s1) (h14, s1) (h15, s1) (h16, s1) (h17, s1) (h18, s1) (h19, s1) (h20, s1) 
*** Configuring hosts
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1 
Traceback (most recent call last):
  File "mininet/example_flowdumps.py", line 70, in <module>
    create_network()
  File "mininet/example_flowdumps.py", line 65, in create_network
    monitor_dump_flows(hosts)
  File "mininet/example_flowdumps.py", line 41, in monitor_dump_flows
    info("The poller is " + eval(poller))
TypeError: eval() arg 1 must be a string, bytes or code object
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo python3 mininet/example_flowdumps.py 
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) (h4, s1) (h5, s1) (h6, s1) (h7, s1) (h8, s1) (h9, s1) (h10, s1) (h11, s1) (h12, s1) (h13, s1) (h14, s1) (h15, s1) (h16, s1) (h17, s1) (h18, s1) (h19, s1) (h20, s1) 
*** Configuring hosts
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1 
Traceback (most recent call last):
  File "mininet/example_flowdumps.py", line 70, in <module>
    create_network()
  File "mininet/example_flowdumps.py", line 65, in create_network
    monitor_dump_flows(hosts)
  File "mininet/example_flowdumps.py", line 41, in monitor_dump_flows
    info("The poller is " + poller)
TypeError: can only concatenate str (not "select.poll") to str
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo python3 mininet/example_flowdumps.py 
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) (h4, s1) (h5, s1) (h6, s1) (h7, s1) (h8, s1) (h9, s1) (h10, s1) (h11, s1) (h12, s1) (h13, s1) (h14, s1) (h15, s1) (h16, s1) (h17, s1) (h18, s1) (h19, s1) (h20, s1) 
*** Configuring hosts
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1 
<select.poll object at 0x7f26c8a9fb70>bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
Traceback (most recent call last):
  File "mininet/example_flowdumps.py", line 70, in <module>
    create_network()
  File "mininet/example_flowdumps.py", line 65, in create_network
    monitor_dump_flows(hosts)
  File "mininet/example_flowdumps.py", line 48, in monitor_dump_flows
    end_time = time() + 10
TypeError: 'module' object is not callable
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ kill %while
bash: kill: %while: no such job
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo python3 mininet/example_flowdumps.py 
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) (h4, s1) (h5, s1) (h6, s1) (h7, s1) (h8, s1) (h9, s1) (h10, s1) (h11, s1) (h12, s1) (h13, s1) (h14, s1) (h15, s1) (h16, s1) (h17, s1) (h18, s1) (h19, s1) (h20, s1) 
*** Configuring hosts
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1 
<select.poll object at 0x7fb1059c2b70>bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
Traceback (most recent call last):
  File "mininet/example_flowdumps.py", line 70, in <module>
    create_network()
  File "mininet/example_flowdumps.py", line 65, in create_network
    monitor_dump_flows(hosts)
  File "mininet/example_flowdumps.py", line 51, in monitor_dump_flows
    info("The readable is " + readable)
TypeError: can only concatenate str (not "list") to str
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo python3 mininet/example_flowdumps.py 
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) (h4, s1) (h5, s1) (h6, s1) (h7, s1) (h8, s1) (h9, s1) (h10, s1) (h11, s1) (h12, s1) (h13, s1) (h14, s1) (h15, s1) (h16, s1) (h17, s1) (h18, s1) (h19, s1) (h20, s1) 
*** Configuring hosts
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1 
<select.poll object at 0x7f1811ba4b70>bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
bash: syntax error near unexpected token `done'
[][][][][][]^CTraceback (most recent call last):
  File "mininet/example_flowdumps.py", line 70, in <module>
    create_network()
  File "mininet/example_flowdumps.py", line 65, in create_network
    monitor_dump_flows(hosts)
  File "mininet/example_flowdumps.py", line 50, in monitor_dump_flows
    readable = poller.poll(1000)
KeyboardInterrupt

shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ while true; do
>   echo s1;
>   sudo ovs-ofctl dump-flows s1;
>   done
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
^Cs1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
s1
^C
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ ^C
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo python3 mininet/example_flowdumps.py 
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) (h4, s1) (h5, s1) (h6, s1) (h7, s1) (h8, s1) (h9, s1) (h10, s1) (h11, s1) (h12, s1) (h13, s1) (h14, s1) (h15, s1) (h16, s1) (h17, s1) (h18, s1) (h19, s1) (h20, s1) 
*** Configuring hosts
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1 
<select.poll object at 0x7f7bec10bb70>h1
h2
h3
h4
h5
h6
h7
h8
h9
h10
h11
h12
h13
h14
h15
h16
h17
h18
h19
h20
[(7, 1), (11, 1), (13, 1), (15, 1), (17, 1), (21, 1), (23, 1)]Traceback (most recent call last):
  File "mininet/example_flowdumps.py", line 69, in <module>
    create_network()
  File "mininet/example_flowdumps.py", line 64, in create_network
    monitor_dump_flows(hosts)
  File "mininet/example_flowdumps.py", line 53, in monitor_dump_flows
    info('$s: ' % node.name, node.monitor(), '\n')
TypeError: not all arguments converted during string formatting
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo python3 mininet/example_flowdumps.py 
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) (h4, s1) (h5, s1) (h6, s1) (h7, s1) (h8, s1) (h9, s1) (h10, s1) (h11, s1) (h12, s1) (h13, s1) (h14, s1) (h15, s1) (h16, s1) (h17, s1) (h18, s1) (h19, s1) (h20, s1) 
*** Configuring hosts
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1 
<select.poll object at 0x7f6b7f73eb70>h1
h2
h3
h4
h5
h6
h7
h8
h9
h10
h11
h12
h13
h14
h15
h16
h17
h18
h19
h20
[(7, 1), (13, 1)]Traceback (most recent call last):
  File "mininet/example_flowdumps.py", line 69, in <module>
    create_network()
  File "mininet/example_flowdumps.py", line 64, in create_network
    monitor_dump_flows(hosts)
  File "mininet/example_flowdumps.py", line 53, in monitor_dump_flows
    info('$s: ' % node.name, node.monitor().strip(), '\n')
TypeError: not all arguments converted during string formatting
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ sudo python3 mininet/example_flowdumps.py 
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) (h4, s1) (h5, s1) (h6, s1) (h7, s1) (h8, s1) (h9, s1) (h10, s1) (h11, s1) (h12, s1) (h13, s1) (h14, s1) (h15, s1) (h16, s1) (h17, s1) (h18, s1) (h19, s1) (h20, s1) 
*** Configuring hosts
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 h17 h18 h19 h20 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Waiting for switches to connect
s1 
<select.poll object at 0x7f210fb65b70>h1
h2
h3
h4
h5
[1] 6290
h6
h7
h8
h9
h10
h11
h12
h13
h14
h15
h16
h17
h18
h19
h20
[(5, 1)]Traceback (most recent call last):
  File "mininet/example_flowdumps.py", line 69, in <module>
    create_network()
  File "mininet/example_flowdumps.py", line 64, in create_network
    monitor_dump_flows(hosts)
  File "mininet/example_flowdumps.py", line 53, in monitor_dump_flows
    print(('$s: ' % node.name) + node.monitor().strip())
TypeError: not all arguments converted during string formatting
shu@shu-VirtualBox:~/Network/trace_ovs_pipeline$ 


"""