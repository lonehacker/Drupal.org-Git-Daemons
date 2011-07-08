#!/usr/bin/env python
#from twisted.internet import epollreactor
#epollreactor.install()

import os
import shlex
import sys
from twisted.conch.error import ConchError, UnauthorizedLogin, ValidPublicKey
from twisted.conch.ssh.channel import SSHChannel
from twisted.conch.ssh.session import ISession, SSHSession, SSHSessionProcessProtocol
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.cred.portal import Portal
from twisted.internet import reactor, defer
from twisted.internet.defer import DeferredList
from twisted.python import components, log
from twisted.python.failure import Failure
from zope import interface
from checkers import *
from drupalorgAuth import *
from users import *
from realms import *
# Workaround for early EOF in git-receive-pack
# Seems related to Twisted bug #4350
# See: http://twistedmatrix.com/trac/ticket/4350
SSHSessionProcessProtocol.outConnectionLost = lambda self: None

import urllib
import base64
import hashlib
import json

from config import config
from service import Service
from service.protocols import AuthProtocol

class GitSession(object):
    interface.implements(ISession)
    
    def __init__(self, user):
        self.user = user
        print "Started Session\n\n"
    def errorHandler(self, fail, proto):
        """Catch any unhandled errors and send the exception string to the remote client."""
        fail.trap(ConchError)
        message = fail.value.value
        log.err(message)
        if proto.connectionMade():
            proto.loseConnection()
        error_script = self.user.error_script
        reactor.spawnProcess(proto, error_script, (error_script, message))

    def execCommand(self, proto, cmd):
        """Execute a git-shell command."""
        argv = shlex.split(cmd)
        # This starts an auth request and returns.
        print "In execCommand Command is "+cmd+"\n\n\n"
        repostring = argv[-1]
        self.router = Router(repostring)
        self.router.route()
        if self.router.isLocal :
           try:
            auth_service_deferred = self.user.meta.request(argv[-1])
           except ConchError, e:
            # The request could not be started
            self.errorHandler(Failure(e), proto)
           else:
            # Check if pushes are disabled for this path
            authobj = Authenticator(self.user)
            auth_service_deferred.addCallback(authobj.pushcontrol, argv)
            # Once it completes, auth is run
            auth_service_deferred.addCallback(authobj.auth, argv)
            # Then the result of auth is passed to execGitCommand to run git-shell
            auth_service_deferred.addCallback(self.execGitCommand, argv, proto)
            auth_service_deferred.addErrback(self.errorHandler, proto)

    def execGitCommand(self, auth_values, argv, proto):
        """After all authentication is done, setup an environment and execute the git-shell commands."""
        user, auth_service = auth_values
        repopath = self.router.repopath
        sh = self.user.shell
        repo_id = auth_service["repo_id"]
        
        env = {}
        if user:
            # The UID is known, populate the environment
            env['VERSION_CONTROL_GIT_UID'] = user["uid"]
            env['VERSION_CONTROL_GIT_REPO_ID'] = repo_id
            env['VERSION_CONTROL_VCS_AUTH_DATA'] = json.dumps(auth_service)
            
        command = ' '.join(argv[:-1] + ["'{0}'".format(repopath)])
        reactor.spawnProcess(proto, sh, (sh, '-c', command), env=env)

    def eofReceived(self): pass

    def closed(self): pass

class GitServer(SSHFactory):
    authmeta = DrupalMeta()
    portal = Portal(GitRealm(authmeta))
    portal.registerChecker(GitPubKeyChecker(authmeta))
    portal.registerChecker(GitPasswordChecker(authmeta))

    def __init__(self, privkey):
        pubkey = '.'.join((privkey, 'pub'))
        self.privateKeys = {'ssh-rsa': Key.fromFile(privkey)}
        self.publicKeys = {'ssh-rsa': Key.fromFile(pubkey)}

class Server(object):
    def __init__(self):
        self.port = config.getint('drupalSSHGitServer', 'port')
        self.interface = config.get('drupalSSHGitServer', 'host')
        self.key = config.get('drupalSSHGitServer', 'privateKeyLocation')
        components.registerAdapter(GitSession, GitConchUser, ISession)

    def application(self):
        return GitServer(self.key)

if __name__ == '__main__':
    log.startLogging(sys.stderr)
    ssh_server = Server()
    reactor.listenTCP(ssh_server.port, 
                      ssh_server.application(), 
                      interface=ssh_server.interface)
    reactor.run()
