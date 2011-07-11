from twisted.internet import defer
class Authenticator(object):
    def __init__(self,user,argv):
        self.argv = argv
        self.deferred = defer.Deferred()
        from drupalorgAuth import DrupalorgAuthenticator
        self.auth_thread = DrupalorgAuthenticator(user)
    def getRepositoryAccess(self,deferred_results):
        self.deferred = self.auth_thread.getRepositoryAccess(self.argv)
        return self.deferred
