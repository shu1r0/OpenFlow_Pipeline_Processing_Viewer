import datetime
from logging import getLogger, Logger, DEBUG, INFO, StreamHandler, Formatter, handlers, setLoggerClass


class Configuration:
    """Configuration of system"""

    #
    # OpenFlow Tracer's Config
    #
    LOGFILE_OFPIPELINE_TRACER = 'log/' + "tracing_of_pipeline-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"
    LOGLEVEL_OFPIPELINE_TRACER = INFO

    MININET_LOG_LEVEL = 'output'

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

    #
    # Web Socket Server
    #
    # Is the web socket server enabled?
    ENABLE_WS_SERVER = False
    ENABLE_WS_CLI = False
    WS_SERVER_IPADDRESS = "0.0.0.0"
    WS_SERVER_PORT = 8888

    #
    # Logging variables for debugging
    #

    # If the log level is not DEBUG, packets is not output.
    OUTPUT_PACKETS_TO_LOGFILE = False
    # If the log level is not DEBUG, flow monitor result is not output
    OUTPUT_FLOWMONITOR_TO_LOGFILE = True
    # If the log level is not DEBUG, dump flows result is not output
    OUTPUT_DUMPFLOWS_TO_LOGFILE = True
    # If the log level is not DEBUG, flow matching result is not output
    # If this is True, process of matching is output to logfile
    OUTPUT_FLOW_MATCHING_RESULT_TO_LOGFILE = False
    # If the log level is not DEBUG, flow table update information is not output
    OUTPUT_FLOW_TABLE_UPDATE_TO_LOGFILE = False
    # ``src.ofproto.pipeline``のapply_action
    OUTPUT_APPLY_PIPELINE_PROCESSING_TO_LOGFILE = True
    # CLI
    OUTPUT_CLI_TO_LOGFILE = True
    # WS Message Hub
    OUTPUT_MESSAGE_HUB_TO_LOGFILE = True

    OUTPUT_PACKET_MATTING_TO_LOGFILE = True

    OUTPUT_ANALYZING_PACKET_PROCESS_TO_LOGFILE = True

    #
    # Control Variables for debugging
    #

    # print traces
    OUTPUT_TRACES_WHEN_SYSTEM_IS_FINISHED = True

    # Is IPv6 disabled in mininet network?
    DISABLE_IPV6 = True

    JUDGE_PACKETS_ONLY_BY_TIME = False


conf = Configuration()

