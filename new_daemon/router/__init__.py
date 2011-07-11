import os
from twisted.internet import defer
from app import routers
from config import config
class Router(object):
   
   def __init__(self,repostring):
        
        self.repostring = repostring
        self.deferred = defer.Deferred()
        routerservice = getattr(routers, config.get('application','RouterModule'))
        self.routerservice = routerservice()
   def gotrepo(self,repopath):
        self.repopath = repopath
        return None
   def route(self):
        self.deferred = self.routerservice.route(self.repostring)
        self.deferred.addCallback(self.gotrepo)