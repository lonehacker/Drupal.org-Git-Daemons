from twisted.python.failure import Failure
from twisted.conch.error import ConchError, UnauthorizedLogin, ValidPublicKey
from config import config
import os
from twisted.internet import defer

class Router(object):
   
   def __init__(self,repostring):
        
        self.repostring = repostring
        self.deferred = defer.Deferred()
            
   def gotrepo(self,repopath):
        self.repopath = repopath
        return self.isLocal
   def route(self):
        self.getrepopath()
        self.deferred.addCallback(self.gotrepo)
   def getrepopath(self):
        '''Note, this is where we do further mapping into a subdirectory
        for a user or issue's specific sandbox'''
        path = self.map_repo()
        # Check to see that the folder exists
        if not os.path.exists(path):
            self.deferred.errback(Failure(ConchError("The remote repository at '{0}' does not exist. Verify that your remote is correct.".format(self.repostring))))
        else:
            self.deferred.callback(path)
    
   def map_repo(self):
        '''Function that returns the repository path'''
        repolist = self.repostring.split('/')
        self.projectname = self.getprojectname(self.repostring)
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
        return path
   def getprojectname(self, uri):
        '''Extract the project name alone from a path like /project/views.git'''

        parts = uri.split('/')
        project = parts[-1]
        if len(project) > 4 and project[-4:] == '.git':
            return project[:-4]
        else:
            return project