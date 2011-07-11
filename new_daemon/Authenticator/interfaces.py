from zope import interface

class IAuthenticator(interface.Interface):
    '''Interface for Authenticator object'''
    def __init__(self,user):
        '''Initialization'''
    def getRepositoryAccess(self,argv):
        '''Returns a deferred fired with auth results if successful or error if not'''
    