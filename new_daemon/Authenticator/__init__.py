from twisted.internet import defer
from app import auths
class Authenticator(object):
    def __init__(self,user,argv):
        self.argv = argv
        self.deferred = defer.Deferred()
        auth_thread = getattr(auths,"DrupalorgAuthenticator")
        self.auth_thread = auth_thread(user)
    def getRepositoryAccess(self,deferred_results):
        self.deferred = self.auth_thread.getRepositoryAccess(self.argv)
        return self.deferred
