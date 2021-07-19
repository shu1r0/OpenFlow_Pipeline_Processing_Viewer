from mininet.node import Switch
from net.net import OnDemandNet


class Router(Switch):

    def __init__(self, name, inNamespace=True, **params):
        Switch.__init__(name, inNamespace=inNamespace, **params)


class QuaggaNet(OnDemandNet):

    def __init__(self, log_level='info'):
        OnDemandNet.__init__(log_level='info')

    def add_router(self, name):
        added_router = self.mininet.addSwitch(name, cls=Router)
        added_router.start()
        return added_router

