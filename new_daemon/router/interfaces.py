from zope.interface import Interface

class IRouter(Interface):
      '''Interface to implement repository router'''
      def route(self,repostring):
          '''Return a deferred fired with the repository path if successful
             or an error otherwise'''