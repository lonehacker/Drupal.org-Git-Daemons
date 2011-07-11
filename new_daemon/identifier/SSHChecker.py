from service import Service
from service.protocols import AuthProtocol
from twisted.python.failure import Failure
from twisted.conch.error import UnauthorizedLogin
from identifier.interfaces import ISSHIdentifier
from zope import interface
import hashlib
class SSHKeyIdentifier(object):
    interface.implements(ISSHIdentifier)
    def identify(self,credentials):
       if (credentials.username == 'git'):
            # Todo, maybe verify the key with a process protocol call
            # (drush or http)
            def success():
                return credentials.username
            d = defer.maybeDeferred(success)
            return d
       else:
            
            """ If a user specified a non-git username, check that the user's key matches their username

            so that we can request a password if it does not."""
            service = Service(AuthProtocol('drupalorg-ssh-user-key'))
            service.request_bool({"username":credentials.username},
                                 {"fingerprint":credentials.fingerprint})
            def auth_callback(result):
                if result:
                    return credentials.username
                else:
                    return Failure(UnauthorizedLogin(credentials.username))
            service.addCallback(auth_callback)
            return service.deferred
class SSHPassIdentifier(object):
    interface.implements(ISSHIdentifier)
    def identify(self,credentials):
        passwd = hashlib.md5(credentials.password).hexdigest()
        service = Service(AuthProtocol('drupalorg-vcs-auth-check-user-pass'))
        service.request_bool({"username":credentials.username},
                            {"password":passwd})
        def auth_callback(result):
            if result:
                return credentials.username
            else:
                return Failure(UnauthorizedLogin(credentials.username))
        service.addCallback(auth_callback)
        return service.deferred