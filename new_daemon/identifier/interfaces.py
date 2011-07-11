from zope.interface import Interface

class ISSHIdentifier(Interface):
    '''Interface for Identifier objects to get Identification Info'''
    def identify(credentials):
        '''Identify user using provided credentials. Returns a deferred fired with
            credentials.username if successful and Failure object if unsuccesful'''