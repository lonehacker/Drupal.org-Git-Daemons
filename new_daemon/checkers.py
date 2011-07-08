from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernamePassword, ISSHPrivateKey
from twisted.conch.ssh.keys import Key
from twisted.python.failure import Failure
from twisted.conch.error import ConchError, UnauthorizedLogin, ValidPublicKey
from zope import interface

import hashlib
from service import Service
from service.protocols import AuthProtocol
class GitPubKeyChecker(object):
    """Skip most of the auth process until the SSH session starts.
    Save the public key fingerprint for later use and verify the signature."""
    credentialInterfaces = ISSHPrivateKey,
    interface.implements(ICredentialsChecker)

    def __init__(self, meta):
        self.meta = meta

    def verify(self, username, credentials, key):
        # Verify the public key signature
        # From twisted.conch.checkers.SSHPublicKeyDatabase._cbRequestAvatarId
        if not credentials.signature:
            # No signature ready
            return Failure(ValidPublicKey())
        else:
            # Ready, verify it
            try:
                if key.verify(credentials.signature, credentials.sigData):
                    return credentials.username
            except:
                log.err()
                return Failure(UnauthorizedLogin("key could not verified"))

    def requestAvatarId(self, credentials):
        key = Key.fromString(credentials.blob)
        fingerprint = key.fingerprint().replace(':', '')
        self.meta.fingerprint = fingerprint
        if (credentials.username == 'git'):
            # Todo, maybe verify the key with a process protocol call
            # (drush or http)
            def success():
                return credentials.username
            d = defer.maybeDeferred(success)
            d.addCallback(self.verify, credentials, key)
            return d
        else:
            """ If a user specified a non-git username, check that the user's key matches their username

            so that we can request a password if it does not."""
            service = Service(AuthProtocol('drupalorg-ssh-user-key'))
            service.request_bool({"username":credentials.username},
                                 {"fingerprint":fingerprint})
            def auth_callback(result):
                if result:
                    return credentials.username
                else:
                    return Failure(UnauthorizedLogin(credentials.username))
            service.addCallback(auth_callback)
            service.addCallback(self.verify, credentials, key)
            return service.deferred

class GitPasswordChecker(object):
    """Skip most of the auth process until the SSH session starts.

    Save the password hash for later use."""
    credentialInterfaces = IUsernamePassword,
    interface.implements(ICredentialsChecker)

    def __init__(self, meta):
        self.meta = meta

    def requestAvatarId(self, credentials):
        self.meta.password = hashlib.md5(credentials.password).hexdigest()
        service = Service(AuthProtocol('drupalorg-vcs-auth-check-user-pass'))
        service.request_bool({"username":credentials.username},
                            {"password":self.meta.password})
        def auth_callback(result):
            if result:
                return credentials.username
            else:
                return Failure(UnauthorizedLogin(credentials.username))
        service.addCallback(auth_callback)
        return service.deferred
