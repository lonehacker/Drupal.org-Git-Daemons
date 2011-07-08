from twisted.cred.portal import IRealm
from users import GitConchUser
from zope import interface

class GitRealm(object):
    interface.implements(IRealm)

    def __init__(self, meta):
        self.meta = meta

    def requestAvatar(self, username, mind, *interfaces):
        print "Avatar Requested \n\n"
        user = GitConchUser(username, self.meta)
        return interfaces[0], user, user.logout