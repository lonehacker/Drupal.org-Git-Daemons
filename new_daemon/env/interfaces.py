from zope.interface import Interface
class IEnv(Interface):
    '''Interface for Setting Environment'''
    def setEnv(self,auth_results,user,router):
        '''return an env dictionary'''