#!/usr/bin/env python
#from twisted.internet import epollreactor
#epollreactor.install()

import os
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
from checkers import GitPubKeyChecker, GitPasswordChecker
from drupalorgAuth import DrupalMeta
from users import GitConchUser
from realms import GitRealm
from executor import Executor
# Workaround for early EOF in git-receive-pack
# Seems related to Twisted bug #4350
# See: http://twistedmatrix.com/trac/ticket/4350
SSHSessionProcessProtocol.outConnectionLost = lambda self: None
from config import config
from service.protocols import AuthProtocol

class GitSession(object):
    interface.implements(ISession)
    
    def __init__(self, user):
        self.user = user
    def execCommand(self, proto, cmd):
        """Execute a git-shell command."""
        # This starts an auth request and returns.
        executor = Executor(cmd,self.user,proto)
        executor.execute()
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
