import shlex
import json
from twisted.conch.error import ConchError
from twisted.python import components, log
from twisted.internet import reactor, defer
from Authenticator import Authenticator
from Router import Router
from env import Env
class Executor(object):
    def __init__(self,cmd,user,proto):
        self.argv = shlex.split(cmd)
        self.user = user
        self.proto = proto
        self.router = Router(self.argv[-1])
        self.authobj = Authenticator(user,self.argv)
        self.envobj = Env(self.user,self.router)
    def execute(self):
        repostring = self.argv[-1]
        self.router.route()
        auth_service_deferred = self.router.deferred
        auth_service_deferred.addCallback(self.authobj.getRepositoryAccess)
        auth_service_deferred.addCallback(self.envobj.setEnv)
        # Then the result of auth is passed to execGitCommand to run git-shell
        auth_service_deferred.addCallback(self.execGitCommand, self.argv, self.proto)
        auth_service_deferred.addErrback(self.errorHandler, self.proto)

    def execGitCommand(self, env , argv, proto):
        """After all authentication is done, setup an environment and execute the git-shell commands."""
        repopath = self.router.repopath
        sh = self.user.shell  
        command = ' '.join(argv[:-1] + ["'{0}'".format(repopath)])
        reactor.spawnProcess(proto, sh, (sh, '-c', command), env=env)
        
    def errorHandler(self, fail, proto):
        """Catch any unhandled errors and send the exception string to the remote client."""
        fail.trap(ConchError)
        message = fail.value.value
        log.err(message)
        if proto.connectionMade():
            proto.loseConnection()
        error_script = self.user.error_script
        reactor.spawnProcess(proto, error_script, (error_script, message))