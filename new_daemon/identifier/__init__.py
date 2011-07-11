from twisted.internet import defer
from app import identifiers
class Identifier(object):
    
    def __init__(self,credentials, service):
        
        
        self.credentials = credentials
        self.deferred = defer.Deferred()
        if service == "Key" :
           iden_service = getattr(identifiers,"SSHKeyIdentifier")
        elif service == "Password" :
           iden_service = getattr(identifiers,"SSHPassIdentifier")
        self.iden_service = iden_service()
    def identify(self):
        self.deferred = self.iden_service.identify(self.credentials)
        return self.deferred