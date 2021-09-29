import sys
import subprocess
from logging import getLogger, setLoggerClass, Logger
from cmd import Cmd
from abc import ABCMeta, abstractmethod

from mininet.log import info, output, error
from mininet.cli import CLI

from src.tracing_net.flowtable.table_repository import table_repository


setLoggerClass(Logger)
logger = getLogger('tracing_net.cli')


class Writable(metaclass=ABCMeta):

    @abstractmethod
    def output(self, msg):
        raise NotImplementedError

    @abstractmethod
    def error(self, msg):
        raise NotImplementedError


class Printer(Writable):

    def output(self, msg):
        pass

    def error(self, msg):
        pass


writer = Printer()


class TracingCLI(Cmd):
    """

    TODO:
        * このままだと，プロンプトがそのまま表示されるので，それを回避して結果だけを返すようにする
        * エラー用のインターフェースほしいな．
    """

    prompt = 'mininet> '

    def __init__(self, mininet):
        super(TracingCLI, self).__init__()
        self.output = writer.output
        self.error = writer.error

        self.mn = mininet
        # Local variable bindings for py command
        self.locals = { 'net': mininet }
        # Attempt to handle input
        self.inPoller = poll()
        self.inPoller.register( stdin )

        write('*** Starting CLI:\n')

    def emptyline(self):
        """Don't repeat last command when you hit return."""
        pass

    # def getLocals(self):
    #     """Local variable bindings for py command"""
    #     self.locals.update(self.mn)
    #     return self.locals

    help_str = (
        'You may also send a command to a node using:\n'
        '  <node> command {args}\n'
        'For example:\n'
        '  mininet> h1 ifconfig\n'
        '\n'
        'The interpreter automatically substitutes IP addresses\n'
        'for node names when a node is the first arg, so commands\n'
        'like\n'
        '  mininet> h2 ping h3\n'
        'should work.\n'
        '\n'
        'Some character-oriented interactive commands require\n'
        'noecho:\n'
        '  mininet> noecho h2 vi foo.py\n'
        'However, starting up an xterm/gterm is generally better:\n'
        '  mininet> xterm h2\n\n'
    )

    def do_help(self, line):
        """Describe available CLI commands."""
        # Cmd.do_help(self, line)  # TODO 要検討
        if line == '':
            self.output(self.help_str)

    def do_nodes(self, _line):
        """List all nodes."""
        nodes = ' '.join(sorted(self.mn))
        self.output('available nodes are: \n%s\n' % nodes)

    def do_ports(self, _line):
        """display ports and interfaces for each switch"""
        dumpPorts(self.mn.switches)

    def do_net(self, _line):
        """List network connections."""
        dumpNodeConnections(self.mn.values())

    def do_sh(self, line):
        """Run an external shell command
           Usage: sh [cmd args]"""
        result = subprocess.run(line, shell=True, check=False, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout
        result = result.decode().strip()
        self.output(result)

    def do_py(self, line):
        """Evaluate a Python expression.
           Node names may be used, e.g.: py h1.cmd('ls')"""
        try:
            result = eval(line, globals(), self.getLocals())
            if not result:
                return

            if isinstance(result, str):
                self.output(result + '\n')
            else:
                self.output(repr(result) + '\n')
        except Exception as e:
            self.output(str(e) + '\n')

    # def do_px( self, line ):
    #     """Execute a Python statement.
    #         Node names may be used, e.g.: px print h1.cmd('ls')"""
    #     try:
    #         exec( line, globals(), self.getLocals() )
    #     except Exception as e:
    #         output( str( e ) + '\n' )

    def do_pingall(self, line):
        """Ping between all hosts."""
        self.mn.pingAll(line)

    def do_pingpair(self, _line):
        """Ping between first two hosts, useful for testing."""
        self.mn.pingPair()

    def do_pingallfull(self, _line):
        """Ping between all hosts, returns all ping results."""
        self.mn.pingAllFull()

    def do_pingpairfull(self, _line):
        """Ping between first two hosts, returns all ping results."""
        self.mn.pingPairFull()

    def do_iperf(self, line):
        """Simple iperf TCP test between two (optionally specified) hosts.
           Usage: iperf node1 node2"""
        args = line.split()
        if not args:
            self.mn.iperf()
        elif len(args) == 2:
            hosts = []
            err = False
            for arg in args:
                if arg not in self.mn:
                    err = True
                    self.output("node '%s' not in network\n" % arg)
                else:
                    hosts.append(self.mn[arg])
            if not err:
                self.mn.iperf(hosts)
        else:
            self.output('invalid number of args: iperf src dst\n')

    def do_iperfudp( self, line ):
        """Simple iperf UDP test between two (optionally specified) hosts.
           Usage: iperfudp bw node1 node2"""
        args = line.split()
        if not args:
            self.mn.iperf( l4Type='UDP' )
        elif len(args) == 3:
            udpBw = args[ 0 ]
            hosts = []
            err = False
            for arg in args[ 1:3 ]:
                if arg not in self.mn:
                    err = True
                    self.error( "node '%s' not in network\n" % arg )
                else:
                    hosts.append( self.mn[ arg ] )
            if not err:
                self.mn.iperf( hosts, l4Type='UDP', udpBw=udpBw )
        else:
            self.error('invalid number of args: iperfudp bw src dst\n bw examples: 10M\n')

    def do_intfs(self, _line):
        """List interfaces."""
        for node in self.mn.values():
            self.output('%s: %s\n' % (node.name, ','.join(node.intfNames())))

    def do_dump(self, _line):
        """Dump node info."""
        for node in self.mn.values():
            self.output('%s\n' % repr( node ))

    def do_link(self, line):
        """Bring link(s) between two nodes up or down.
           Usage: link node1 node2 [up/down]"""
        args = line.split()
        if len(args) != 3:
            self.error('invalid number of args: link end1 end2 [up down]\n')
        elif args[ 2 ] not in [ 'up', 'down' ]:
            self.error('invalid type: link end1 end2 [up down]\n')
        else:
            self.mn.configLinkStatus( *args )

    def do_xterm( self, line, term='xterm' ):
        """Spawn xterm(s) for the given node(s).
           Usage: xterm node1 node2 ..."""
        self.error("This command is not supported")

    def do_x(self, line):
        """Create an X11 tunnel to the given node,
           optionally starting a client.
           Usage: x node [cmd args]"""
        self.error("This command is not supported")

    def do_gterm( self, line ):
        """Spawn gnome-terminal(s) for the given node(s).
           Usage: gterm node1 node2 ..."""
        self.error("This command is not supported")

    def do_exit( self, _line ):
        """Exit"""
        self.output('exited by user command')
        return True

    def do_quit( self, line ):
        "Exit"
        return self.do_exit( line )

    def do_EOF( self, line ):
        "Exit"
        output( '\n' )
        return self.do_exit( line )

    def isatty( self ):
        "Is our standard input a tty?"
        return isatty( self.stdin.fileno() )

    def do_noecho( self, line ):
        """Run an interactive command with echoing turned off.
           Usage: noecho [cmd args]"""
        if self.isatty():
            quietRun( 'stty -echo' )
        self.default( line )
        if self.isatty():
            quietRun( 'stty echo' )

    def do_source( self, line ):
        """Read commands from an input file.
           Usage: source <file>"""
        self.error("This command is not supported")

    def do_dpctl( self, line ):
        """Run dpctl (or ovs-ofctl) command on all switches.
           Usage: dpctl command [arg1] [arg2] ..."""
        args = line.split()
        if len(args) < 1:
            self.error('usage: dpctl command [arg1] [arg2] ...\n')
            return
        for sw in self.mn.switches:
            self.output('*** ' + sw.name + ' ' + ('-' * 72) + '\n')
            self.output(sw.dpctl(*args))

    def do_time( self, line ):
        "Measure time taken for any command in Mininet."
        start = time.time()
        self.onecmd(line)
        elapsed = time.time() - start
        self.stdout.write("*** Elapsed time: %0.6f secs\n" % elapsed)

    def do_links(self, _line):
        """Report on links"""
        for link in self.mn.links:
            self.output(link, link.status(), '\n')

    def do_switch(self, line):
        "Starts or stops a switch"
        args = line.split()
        if len(args) != 2:
            self.error('invalid number of args: switch <switch name>{start, stop}\n')
            return
        sw = args[0]
        command = args[1]
        if sw not in self.mn or self.mn.get(sw) not in self.mn.switches:
            self.error('invalid switch: %s\n' % args[1])
        else:
            sw = args[0]
            command = args[1]
            if command == 'start':
                self.mn.get(sw).start(self.mn.controllers)
            elif command == 'stop':
                self.mn.get(sw).stop(deleteIntfs=False)
            else:
                self.error('invalid command: switch <switch name> {start, stop}\n')

    def do_wait(self, _line):
        """Wait until all switches have connected to a controller"""
        self.mn.waitConnected()

    def default(self, line):
        """Called on an input line when the command prefix is not recognized.
           Overridden to run shell commands when a node is the first
           CLI argument.  Past the first CLI argument, node names are
           automatically replaced with corresponding IP addrs."""

        first, args, line = self.parseline(line)

        if first in self.mn:
            if not args:
                self.error('*** Please enter a command for node: %s <cmd>\n' % first)
                return
            node = self.mn[first]
            rest = args.split(' ')
            # Substitute IP addresses for node names in command
            # If updateIP() returns None, then use node name
            rest = [self.mn[arg].defaultIntf().updateIP() or arg
                    if arg in self.mn else arg
                    for arg in rest]
            rest = ' '.join(rest)
            # Run cmd on node:
            node.sendCmd(rest)
            self.waitForNode(node)
        else:
            self.error('*** Unknown command: %s\n' % line)

    def waitForNode( self, node ):
        """Wait for a node to finish, and print its output."""
        # Pollers
        nodePoller = poll()
        nodePoller.register( node.stdout )
        bothPoller = poll()
        bothPoller.register( self.stdin, POLLIN )
        bothPoller.register( node.stdout, POLLIN )
        if self.isatty():
            # Buffer by character, so that interactive
            # commands sort of work
            quietRun( 'stty -icanon min 1' )
        while True:
            try:
                bothPoller.poll()
                # XXX BL: this doesn't quite do what we want.
                if False and self.inputFile:
                    key = self.inputFile.read( 1 )
                    if key != '':
                        node.output(key)
                    else:
                        self.inputFile = None
                if isReadable( self.inPoller ):
                    key = self.stdin.read( 1 )
                    node.output(key)
                if isReadable( nodePoller ):
                    data = node.monitor()
                    output( data )
                if not node.waiting:
                    break
            except KeyboardInterrupt:
                # There is an at least one race condition here, since
                # it's possible to interrupt ourselves after we've
                # read data but before it has been printed.
                node.sendInt()
            except select.error as e:
                # pylint: disable=unpacking-non-sequence
                # pylint: disable=unbalanced-tuple-unpacking
                errno_, errmsg = e.args
                if errno_ != errno.EINTR:
                    error( "select.error: %s, %s" % (errno_, errmsg) )
                    node.sendInt()

    def precmd(self, line):
        """allow for comments in the cli"""
        if '#' in line:
            line = line.split('#')[0]
        return line


# Helper functions

def isReadable( poller ):
    "Check whether a Poll object has a readable fd."
    for fdmask in poller.poll( 0 ):
        mask = fdmask[ 1 ]
        if mask & POLLIN:
            return True
        return False

