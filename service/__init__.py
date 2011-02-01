from twisted.internet import defer
from zope.interface import Interface
import json

class IServiceProtocol(Interface):
    """Interface for Service objects to make requests."""
    def request(*args):
        """Setup a request for data. 

        Must use self.deferred for any asynchronous operations."""

class Service(object):
    """Wrapper class for requests out to external services.

    Protocol doesn't have to be a real protocol, but must conform to the interface specified by IServiceProtocol."""
    bool_map = {"true":True, "false":False} # PHP booleans - add more if needed
    def __init__(self, protocol):
        self.protocol = protocol
        self.deferred = protocol.deferred

    def convert_bool(self, protocol):
        self.result = self.bool_map[protocol.raw.strip()]
        return self.result

    def request_bool(self, *args):
        self.protocol.request(*args)
        self.deferred.addCallback(self.convert_bool)

    def convert_json(self, protocol):
        try:
            self.result = json.loads(protocol.raw)
            return self.result
        except ValueError:
            log.err("Protocol {0}:{1} returned bad JSON.".format(self.protocol.__class__, self.protocol.command))

    def request_json(self, *args):
        self.protocol.request(*args)
        self.deferred.addCallback(self.convert_json)

    def addCallback(self, *args):
        self.deferred.addCallback(*args)

    def addErrback(self, *args):
        self.deferred.addErrback(*args)