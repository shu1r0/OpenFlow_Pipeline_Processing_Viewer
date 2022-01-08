import datetime
import enum
from logging import getLogger, Logger, DEBUG, INFO, StreamHandler, Formatter, handlers, setLoggerClass


class RunMode(enum.IntEnum):

    NOMAL = enum.auto()
    DEBUG_ROUTER = enum.auto()


class Configuration:
    """Configuration of system"""

    #
    # OpenFlow Tracer's Config
    #
    LOGFILE_OFPIPELINE_TRACER = 'log/' + "tracing_of_pipeline-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"
    LOGLEVEL_OFPIPELINE_TRACER = DEBUG
    FLOW_MONITOR_INTERVAL = 1  # seconds

    MININET_LOG_LEVEL = 'output'

    # CLI config
    WS_CLI_OUTPUT_STDOUT = True

    #
    # OpenFlow Capture's Config
    #
    LOCAL_PORT = 63333
    CONTROLLER_IP = "127.0.0.1"
    CONTROLLER_PORT = 6633
    LOGFILE_OFCAPTURE = "log/" + "ofcapture-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"  # debug用
    LOGLEVEL_OFCAPTURE = INFO

    # Are captured packets output to pcap file?
    OUTPUT_PACKETS_TO_PCAP_FILE = True
    # Don't forget '/'.
    PCAP_FILE_DIRECTORY = 'log/pcap/'

    OUTPUT_FLOWTABLES_TO_FILE = True
    FLOWTABLES_DIRECTORY = 'log/flowtable/'

    OUTPUT_PACKET_PROCESSING_TO_FILE = True
    PACKET_PROCESSING_DIRECTORY = 'log/packet_processing/'

    #
    # Web Socket Server
    #
    # Is the web socket server enabled?
    ENABLE_WS_SERVER = True
    ENABLE_WS_CLI = True  # 廃止したい
    WS_SERVER_IPADDRESS = "0.0.0.0"
    WS_SERVER_PORT = 8888

    #
    # Logging variables for debugging
    #

    # If the log level is not DEBUG, packets is not output.
    OUTPUT_PACKETS_TO_LOGFILE = False
    # If the log level is not DEBUG, flow monitor result is not output
    OUTPUT_FLOWMONITOR_TO_LOGFILE = False
    # If the log level is not DEBUG, dump flows result is not output
    OUTPUT_DUMPFLOWS_TO_LOGFILE = False
    # If the log level is not DEBUG, flow table update information is not output
    OUTPUT_FLOW_TABLE_UPDATE_TO_LOGFILE = False
    # ``src.ofproto.pipeline``のapply_action
    OUTPUT_APPLY_PIPELINE_PROCESSING_TO_LOGFILE = False
    # CLI
    OUTPUT_CLI_TO_LOGFILE = False
    # WS Message Hub
    OUTPUT_MESSAGE_HUB_TO_LOGFILE = True

    # analyzing to logfile

    OUTPUT_PACKET_MATCHING_TO_LOGFILE = True
    # ``src.analyzer``
    OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE = True
    OUTPUT_ANALYZING_POLLING_TO_LOGFILE = False
    # If the log level is not DEBUG, flow matching result is not output
    # If this is True, process of matching is output to logfile
    OUTPUT_FLOW_MATCHING_RESULT_TO_LOGFILE = True

    OUTPUT_SETFIELD_TO_LOGFILE = True

    #
    # Control Variables for debugging
    #

    # print traces
    OUTPUT_TRACES_WHEN_SYSTEM_IS_FINISHED = True

    # Is IPv6 disabled in mininet network?
    DISABLE_IPV6 = True

    # Judge pakcets only by timestamp
    JUDGE_PACKETS_ONLY_BY_TIME = False


class DEBUGCONFIG:
    pass


conf = Configuration()

