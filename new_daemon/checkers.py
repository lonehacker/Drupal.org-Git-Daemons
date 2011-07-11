from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernamePassword, ISSHPrivateKey
from twisted.conch.ssh.keys import Key
from twisted.python.failure import Failure
from twisted.conch.error import ConchError, UnauthorizedLogin, ValidPublicKey
from identifier import Identifier
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
        credentials.fingerprint = fingerprint
        iden = Identifier(credentials,"Key")
        d = iden.identify()
        d.addCallback(self.verify,credentials,key)
class GitPasswordChecker(object):
    """Skip most of the auth process until the SSH session starts.

    Save the password hash for later use."""
    credentialInterfaces = IUsernamePassword,
    interface.implements(ICredentialsChecker)

    def __init__(self, meta):
        self.meta = meta

    def requestAvatarId(self, credentials):
        self.meta.password = hashlib.md5(credentials.password).hexdigest()
        iden = Identifier(credentials,"Password")
        d = iden.identify()
        return d