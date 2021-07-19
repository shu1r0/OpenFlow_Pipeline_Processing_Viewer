import sys
from logging import getLogger, setLoggerClass, Logger

from mininet.log import info, output, error
from mininet.cli import CLI

from src.tracing_net.flowtable.table_repository import table_repository


setLoggerClass(Logger)
logger = getLogger('tracing_net.cli')

class TracingCLI(CLI):

    def __init__(self, mininet, stdin=sys.stdin, script=None, **kwargs):
        super(TracingCLI, self).__init__(mininet, stdin=stdin, script=script, **kwargs)

    def do_tables(self, line):
        switch, at_time = line.split()
        if switch and at_time:
            tables = table_repository.get(switch, at_time)
            output(tables)
        else:
            output("Usage: tables [switch] [timestamp]")
