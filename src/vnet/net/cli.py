import subprocess
import threading
import signal
import time
import queue
from logging import getLogger, setLoggerClass, Logger
from cmd import Cmd
from abc import ABCMeta, abstractmethod
import asyncio

from src.config import conf

setLoggerClass(Logger)
logger = getLogger('vnet.cli')


class CLIConnection(metaclass=ABCMeta):
    """This Class is interface for CLI

    """

    def __init__(self):
        self.output_handler = None
        self.error_handler = None
        self.end_signal_handler = None

    @abstractmethod
    def input(self, msg):
        """write to stdin

        Args:
            msg:

        Examples:
            def input(self, msg):
                self.stdin.write(msg)
                self.stdin.flush()
        """
        raise NotImplementedError

    async def readline(self):
        """read line

        Returns:
            str
        """
        pass

    @abstractmethod
    def output(self, msg):
        """This is called by CLI

        Args:
            msg (str) : output message
        """
        raise NotImplementedError

    @abstractmethod
    def error(self, msg):
        """This is called by CLI.

        Args:
            msg (str) : error message
        """
        raise NotImplementedError

    @abstractmethod
    def send_end_command_signal(self):
        """this is called by ``post_cmd()``"""
        raise NotImplementedError

    def output_deco(self, func):
        self.output_handler = func

    def error_deco(self, func):
        self.error_handler = func

    def end_signal_deco(self, func):
        self.end_signal_handler = func


class WSCLIConnection(CLIConnection):
    """This class is MininetCLI interface for WebSocket.

    * It issues WebSocket Protobuf message and sends them to the MessageHub of WebSocket.
    """

    def __init__(self, output_stdout=False, event_loop=None):
        self.queue = asyncio.Queue(loop=event_loop)

        super(WSCLIConnection, self).__init__()
        self.output_stdout = output_stdout

    def input(self, msg):
        if conf.OUTPUT_CLI_TO_LOGFILE:
            logger.debug("CLI input {}".format(msg))
        asyncio.ensure_future(self.queue.put(msg))

    async def readline(self):
        line = await self.queue.get()
        return line

    def output(self, msg):
        if conf.OUTPUT_CLI_TO_LOGFILE:
            logger.debug("CLI output {}".format(msg))
        if self.output_handler:
            self.output_handler(msg)

    def error(self, msg):
        if conf.OUTPUT_CLI_TO_LOGFILE:
            logger.debug("CLI error {}".format(msg))
        if self.error_handler:
            self.error_handler(msg)

    def send_end_command_signal(self):
        if conf.OUTPUT_CLI_TO_LOGFILE:
            logger.debug("CLI send end command signal")
        if self.end_signal_handler:
            self.end_signal_handler()


COMMAND_HELP = \
"""
You may also send a command to a node using:
    <node> command {args}

For example:
    mininet> h1 ifconfig
    
The interpreter automatically substitutes IP addresses for node names when a node is the first arg, so commands like
    mininet> h2 ping h3
should work.

You stop running shell command by sending q:
    mininet> q
"""


class TracingCLI(Cmd):
    """

    TODO:
        * このままだと，プロンプトがそのまま表示されるので，それを回避して結果だけを返すようにする
        * エラー用のインターフェースほしいな．

    Attributes:
        cli_connection (CLIConnection) : CLI input/output interface
        output : output function
        error : error function alias
        send_end_command_signal : send_end_command_signal function
        mn : mininet
        locals (dict) : local variables for py command
    """

    prompt = 'mininet> '

    def __init__(self, mininet, cli_connection: CLIConnection):
        super(TracingCLI, self).__init__()
        # cli input/output interface
        self.cli_connection = cli_connection
        # alias
        self.output = cli_connection.output
        self.error = cli_connection.error
        self.send_end_command_signal = cli_connection.send_end_command_signal

        self.running_popen = None

        self.mn = mininet
        # Local variable bindings for py command
        self.locals = {'net': mininet}

        self.use_rawinput = False

        self.history = []

        # write('*** Starting CLI:\n')

    async def wsevent_cmdloop(self, intro=None):
        """command loop for async"""
        self.preloop()

        if intro:
            self.output(intro)

        stop = None
        while not stop:
            line = await self.cli_connection.readline()

            line = self.precmd(line)
            stop = self.onecmd(line)
            stop = self.postcmd(stop, line)
        self.postloop()

    def preloop(self) -> None:
        logger.debug("preloop WebSocket CLI (connection={}, mn_type={})".format(self.cli_connection, self.mn))

    def postloop(self):
        logger.debug("post WebSocket CLI (history={})".format(self.history))
        print("cli end")

    def postcmd(self, stop: bool, line: str) -> bool:
        self.send_end_command_signal()
        self.history.append(line)
        return stop

    def run(self):
        """CLI run"""
        self.cmdloop()

    def emptyline(self):
        """Don't repeat last command when you hit return."""
        pass

    def getLocals(self):
        """Local variable bindings for py command"""
        self.locals.update(self.mn)
        return self.locals

    def do_help(self, line):
        """Describe available CLI commands."""
        # Cmd.do_help(self, line)  # TODO 要検討
        if line == '':
            self.output(COMMAND_HELP)

    def do_nodes(self, _line):
        """List all nodes."""
        nodes = ' '.join(sorted(self.mn))
        self.output('available nodes are: \n%s\n' % nodes)

    # def do_ports(self, _line):
    #     """display ports and interfaces for each switch"""
    #     dumpPorts(self.mn.switches)
    #
    def do_net(self, line):
        """
        List network connections.

        todo:
            * showなどで表示できるようにする
        """
        args = line.split(' ')
        if len(args) == 2 and args[0] == "show":
            if len(args[1]) >= 4 and args[1][:4] == "addr":
                hosts = self.mn.hosts
                result = "host |     IP     |     MAC     \n"
                for host in hosts:
                    result += "{} | {} | {} \n".format(host.name, host.IP(), host.MAC())
                self.output(result)
        else:
            nodes = self.mn.values()

            for node in nodes:
                result = ""
                result += node.name
                for intf in node.intfList():
                    result += " {}:".format(intf)
                    if intf.link:
                        intfs = [intf.link.intf1, intf.link.intf2]
                        intfs.remove(intf)
                        result += str(intfs[0])
                    else:
                        result += ' '
                result += "\n"
                self.output(result)

    def do_sh(self, line):
        """Run an external shell command
           Usage: sh [cmd args]
        todo:
            use running_popen
        """
        result = subprocess.run(line, shell=True, check=False, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout
        result = result.decode().strip()
        self.output(result)

    def do_py(self, line):
        """Evaluate a Python expression.
           Node names may be used, e.g.: py h1.cmd('ls')"""
        try:
            result = eval(line, globals(), self.getLocals())
            if not result:
                self.output("\n")
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
    #
    def do_pingall(self, _line):
        """Ping between all hosts."""
        self.mn.ws_ping_all()
    #
    # def do_pingpair(self, _line):
    #     """Ping between first two hosts, useful for testing."""
    #     self.mn.pingPair()
    #
    # def do_pingallfull(self, _line):
    #     """Ping between all hosts, returns all ping results."""
    #     self.mn.pingAllFull()
    #
    # def do_pingpairfull(self, _line):
    #     """Ping between first two hosts, returns all ping results."""
    #     self.mn.pingPairFull()

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

    def do_iperfudp(self, line):
        """Simple iperf UDP test between two (optionally specified) hosts.

        Usage: iperfudp bw node1 node2

        """
        args = line.split()
        if not args:
            self.mn.iperf(l4Type='UDP')
        elif len(args) == 3:
            udpBw = args[0]
            hosts = []
            err = False
            for arg in args[1:3]:
                if arg not in self.mn:
                    err = True
                    self.error("node '%s' not in network\n" % arg)
                else:
                    hosts.append(self.mn[arg])
            if not err:
                self.mn.iperf(hosts, l4Type='UDP', udpBw=udpBw)
        else:
            self.error('invalid number of args: iperfudp bw src dst\n bw examples: 10M\n')

    def do_intfs(self, _line):
        """List interfaces."""
        for node in self.mn.values():
            self.output('%s: %s\n' % (node.name, ','.join(node.intfNames())))

    def do_dump(self, _line):
        """Dump node info."""
        for node in self.mn.values():
            self.output('%s\n' % repr(node))

    def do_link(self, line):
        """Bring link(s) between two nodes up or down.
           Usage: link node1 node2 [up/down]"""
        args = line.split()
        if len(args) != 3:
            self.error('invalid number of args: link end1 end2 [up down]\n')
        elif args[2] not in ['up', 'down']:
            self.error('invalid type: link end1 end2 [up down]\n')
        else:
            self.mn.configLinkStatus(*args)

    def do_xterm(self, line, term='xterm'):
        """Spawn xterm(s) for the given node(s).
           Usage: xterm node1 node2 ..."""
        self.error("This command is not supported")

    def do_x(self, line):
        """Create an X11 tunnel to the given node,
           optionally starting a client.
           Usage: x node [cmd args]"""
        self.error("This command is not supported")

    def do_gterm(self, line):
        """Spawn gnome-terminal(s) for the given node(s).
           Usage: gterm node1 node2 ..."""
        self.error("This command is not supported")

    def do_exit(self, _line):
        """Exit"""
        self.output('exited by user command \n')
        return True

    def do_quit(self, _line):
        """Exit"""
        return self.do_exit(_line)

    def do_EOF(self, _line):
        """Exit"""
        self.output('\n')
        # return self.do_exit(_line)

    # def isatty( self ):
    #     "Is our standard input a tty?"
    #     return isatty( self.stdin.fileno() )

    # def do_noecho( self, line ):
    #     """Run an interactive command with echoing turned off.
    #        Usage: noecho [cmd args]"""
    #     if self.isatty():
    #         quietRun( 'stty -echo' )
    #     self.default( line )
    #     if self.isatty():
    #         quietRun( 'stty echo' )

    def do_source(self, line):
        """Read commands from an input file.
           Usage: source <file>"""
        self.error("This command is not supported")

    def do_dpctl(self, line):
        """Run dpctl (or ovs-ofctl) command on all switches.
           Usage: dpctl command [arg1] [arg2] ..."""
        args = line.split()
        if len(args) < 1:
            self.error('usage: dpctl command [arg1] [arg2] ...\n')
            return
        for sw in self.mn.switches:
            self.output('*** ' + sw.name + ' ' + ('-' * 72) + '\n')
            self.output(sw.dpctl(*args))

    def do_time(self, line):
        "Measure time taken for any command in Mininet."
        start = time.time()
        self.onecmd(line)
        elapsed = time.time() - start
        self.stdout.write("*** Elapsed time: %0.6f secs\n" % elapsed)

    def do_links(self, _line):
        """Report on links"""
        for link in self.mn.links:
            self.output(link + link.status() + '\n')

    def do_switch(self, line):
        """Starts or stops a switch"""
        args = line.split()
        if len(args) != 2:
            self.error('invalid number of args: switch <switch name> {start, stop}\n')
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

    def do_starttracing(self, _line):
        """経路分析を開始する

        todo: 廃止したい
        Args:
            _line:

        Returns:

        """
        self.mn.start_gathering()

    def do_stoptracing(self, _line):
        """経路分析を開始する

        todo: 廃止したい
        Args:
            _line:

        Returns:

        """
        self.mn.stop_gathering()

    def do_q(self):
        """
        quite running popen
        """
        self.send_sigint()

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

            # Run cmd on node until sigint is sent:
            self.running_popen = node.popen(rest, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while self.running_popen.poll() is None:
                self.output(self.running_popen.stdout.readline().decode().strip())
            self.output(self.running_popen.stdout.read().decode().strip())
            self.running_popen = None
        else:
            self.error('Unknown command: %s\n' % line)

    def send_sigint(self):
        """send keyboard interrupt to running popen"""
        if self.running_popen:
            # send keyboard interrupt
            self.running_popen.send_signal(signal.SIGINT)

