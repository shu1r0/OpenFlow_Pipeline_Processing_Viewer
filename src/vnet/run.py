"""
entry file
"""
from logging import getLogger, Logger, DEBUG, StreamHandler, Formatter, handlers, setLoggerClass
import datetime
import time

from net.net import NetworkGatheringInfo


def setup_logger():
    setLoggerClass(Logger)
    logger = getLogger('vnet')
    logger.setLevel(DEBUG)
    formatter = Formatter(
        "%(asctime)s | %(process)d | %(name)s, %(funcName)s, %(lineno)d | %(levelname)s | %(message)s")
    # stream_handler = StreamHandler()
    # stream_handler.setLevel(DEBUG)
    # stream_handler.setFormatter(formatter)
    # logger.addHandler(stream_handler)
    filename = "traced_net-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"  # debug用
    file_handler = handlers.RotatingFileHandler(filename="log/" + filename,
                                                maxBytes=16777216,
                                                backupCount=2)
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def test1():
    net = NetworkGatheringInfo(controller_port=6653)
    net.start()
    # time.sleep(2)
    net.add_switch('s1')
    net.add_switch('s2')
    h1 = net.add_host('h1')
    h2 = net.add_host('h2')
    h3 = net.add_host('h3')
    net.add_link('l1', 's1', 's2')
    net.add_link('l2', 's1', 'h1')
    net.add_link('l3', 's2', 'h2')
    net.add_link('l4', 's2', 'h3')
    h1.setIP('192.168.1.1', 24)
    h2.setIP('192.168.1.2', 24)
    h3.setIP('192.168.1.3', 24)
    net.remove_link('l4')
    net.remove_host('h3')
    net.start_gathering()
    net.cli_run()
    net.stop()

def test2():
    """
    c0 cd ../ryu_based_simple_router/;ryu-manager router.py &
    Returns:

    """
    net = NetworkGatheringInfo(controller_port=6653)
    net.start()
    # time.sleep(2)
    s1 = net.add_switch('s1')

    # add_hostとリンクはセットにしないとエラー(インタフェースの設定がおかしくなる)
    h1 = net.add_host('h1')
    net.add_link('l2', 's1', 'h1')

    s2 = net.add_switch('s2')
    net.add_link('l1', 's1', 's2')

    h2 = net.add_host('h2')
    net.add_link('l3', 's2', 'h2')
    # h1.setIP('192.168.1.3', 24)
    # h1.cmd("route add default gw 192.168.1.1")
    # h2.setIP('192.168.3.2', 24)
    # h2.cmd("route add default gw 192.168.3.1")
    # h3.setIP('192.168.1.3', 24)
    # net.remove_link('l4')
    # net.remove_host('h3')
    net.start_gathering()
    net.cli_run()
    net.stop()

def test_for_faucet_vlan():
    net = NetworkGatheringInfo(controller_port=6653)
    net.start()
    net.add_switch('s1')

    net.add_host('h1', ip='192.168.0.1/24')
    net.addLink('s1', 'h1')

    net.add_host('h2', ip='192.168.0.2/24')
    net.addLink('s1', 'h2')

    net.add_host('h3', ip='192.168.0.3/24')
    net.addLink('s1', 'h3')

    h4 = net.add_host('h4', ip='192.168.0.4/24')
    net.addLink('s1', 'h4')

    h5 = net.add_host('h5', ip='192.168.2.5/24')
    net.addLink('s1', 'h5')

    h6 = net.add_host('h6', ip='192.168.2.6/24')
    net.addLink('s1', 'h6')

    h7 = net.add_host('h7', ip='192.168.3.7/24')
    net.addLink('s1', 'h7')

    net.add_host('h8', ip='192.168.3.8/24')
    net.addLink('s1', 'h8')

    net.start_gathering()
    net.cli_run()
    net.stop()


if __name__ == '__main__':
    setup_logger()
    test2()
