import datetime
from logging import getLogger, Logger, DEBUG, INFO, StreamHandler, Formatter, handlers, setLoggerClass


class Configuration:

    LOGFILE_OFPIPELINE_TRACER = 'log/' + "tracing_of_pipeline-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"
    LOGLEVEL_OFPIPELINE_TRACER = DEBUG
    MININET_LOG_LEVEL = 'output'

    LOCAL_PORT = 63333
    CONTROLLER_IP = "127.0.0.1"
    CONTROLLER_PORT = 6633
    LOGFILE_OFCAPTURE = "log/" + "ofcapture-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"  # debug用

    # If the log level is greater than DEBUG, packets is not output.
    OUTPUT_PACKETS_TO_LOGFILE = False
    DISABLE_IPV6 = True

    # Is the web socket server enabled?
    ENABLE_WS_SERVER = True
    WS_SERVER_IPADDRESS = "0.0.0.0"
    WS_SERVER_PORT = 8888


conf = Configuration()

