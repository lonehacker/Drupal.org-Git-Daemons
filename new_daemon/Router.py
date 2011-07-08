from twisted.python.failure import Failure
from twisted.conch.error import ConchError, UnauthorizedLogin, ValidPublicKey
from config import config
from utils import Util
import os
from twisted.internet import defer

class Router(object):
   
   def __init__(self,repostring):
        repolist = repostring.split('/')
        self.utilobj = Util()
        self.repostring = repostring
        self.deferred = defer.Deferred()
        if repolist[0]:
            # No leading /
            self.scheme = repolist[0]
            self.projectpath = repolist[1:]
        else:
            self.scheme = repolist[1]
            self.projectpath = repolist[2:]    
   def gotrepo(self,repopath):
        self.repopath = repopath
        return self.isLocal
   def route(self):
        self.getrepopath(self.scheme, self.projectpath)
        self.deferred.addCallback(self.gotrepo)
        self.projectname = self.utilobj.getprojectname(self.repostring)
   def getrepopath(self, scheme, subpath):
        '''Note, this is where we do further mapping into a subdirectory
        for a user or issue's specific sandbox'''

        # Build the path to the repository
        self.isLocal = True
        try:
            scheme_path = config.get(scheme, 'repositoryPath')
        except:
            # Fall back to the default configured path scheme
            scheme_path = config.get('drupalSSHGitServer', 'repositoryPath')
        path = os.path.join(scheme_path, *subpath)
        if path[-4:] != ".git":
            path += ".git"
        # Check to see that the folder exists
        """if not os.path.exists(path):
            self.deferred.errback(Failure(ConchError("The remote repository at '{0}' does not exist. Verify that your remote is correct.".format(self.repostring))))
        else:
            self.deferred.callback(path)"""
        self.deferred.callback("/Users/rajeel/Drupal.org-Git-Daemons.git")