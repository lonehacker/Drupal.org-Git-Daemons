from twisted.internet import defer
from app import identifiers
from config import config
class Identifier(object):
    
    def __init__(self,credentials, service):
        self.credentials = credentials
        self.deferred = defer.Deferred()
        if service == "Key" :
           iden_service = getattr(identifiers,config.get('application','KeyIdentifier'))
        elif service == "Password" :
           iden_service = getattr(identifiers,config.get('application','PassIdentifier'))
        self.iden_service = iden_service()
    def identify(self):
        self.deferred = self.iden_service.identify(self.credentials)
        return self.deferred