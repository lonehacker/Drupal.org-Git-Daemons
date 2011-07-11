from twisted.python.failure import Failure
from twisted.conch.error import ConchError
from config import config
import os
from twisted.internet import defer
from router.interfaces import IRouter
from zope import interface
class DrupalRouter(object):
   interface.implements(IRouter)
   def __init__(self):
        self.deferred = defer.Deferred()
   def route(self,repostring):
        self.getrepopath(repostring)
        return self.deferred
   def getrepopath(self,repostring):
        '''Note, this is where we do further mapping into a subdirectory
        for a user or issue's specific sandbox'''
        path = self.map_repo(repostring)
        # Check to see that the folder exists
        if not os.path.exists(path):
            self.deferred.errback(Failure(ConchError("The remote repository at '{0}' does not exist. Verify that your remote is correct.".format(self.repostring))))
        else:
            if self.isLocal:
               self.deferred.callback(path)
            else:
               self.deferred.errback("The repository is not local, stay tuned while you are forwarded")
   def map_repo(self,repostring):
        '''Function that returns the repository path'''
        repolist = repostring.split('/')
        self.projectname = self.getprojectname(repostring)
        if repolist[0]:
            # No leading /
            scheme = repolist[0]
            projectpath = repolist[1:]
        else:
            scheme = repolist[1]
            projectpath = repolist[2:]
        # Build the path to the repository
        self.isLocal = True
        try:
            scheme_path = config.get(scheme, 'repositoryPath')
        except:
            # Fall back to the default configured path scheme
            scheme_path = config.get('drupalSSHGitServer', 'repositoryPath')
        path = os.path.join(scheme_path, *projectpath)
        if path[-4:] != ".git":
            path += ".git"
        #return path
        return "/Users/rajeel/Drupal.org-Git-Daemons/"
   def getprojectname(self, uri):
        '''Extract the project name alone from a path like /project/views.git'''

        parts = uri.split('/')
        project = parts[-1]
        if len(project) > 4 and project[-4:] == '.git':
            return project[:-4]
        else:
            return project