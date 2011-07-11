from twisted.internet import defer
from SSHChecker import SSHKeyIdentifier, SSHPassIdentifier

class Identifier(object):
    
    def __init__(self,credentials, service):
        self.credentials = credentials
        self.deferred = defer.Deferred()
        if service == "Key" :
           self.iden_service = SSHKeyIdentifier()
        elif service == "Password" :
           self.iden_service = SSHPassIdentifier()
    def identify(self):
        self.deferred = self.iden_service.identify(self.credentials)
        return self.deferred