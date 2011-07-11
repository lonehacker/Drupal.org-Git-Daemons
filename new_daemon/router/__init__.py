import os
from twisted.internet import defer

class Router(object):
   
   def __init__(self,repostring):
        self.repostring = repostring
        self.deferred = defer.Deferred()
        from Router import DrupalRouter
        self.routerservice = DrupalRouter()
   def gotrepo(self,repopath):
        self.repopath = repopath
        return None
   def route(self):
        self.deferred = self.routerservice.route(self.repopath)
        self.deferred.addCallback(self.gotrepo)