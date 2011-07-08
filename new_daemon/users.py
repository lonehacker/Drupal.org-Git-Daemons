from twisted.conch.avatar import ConchUser
from twisted.conch.ssh.session import SSHSession
from utils import *
class GitConchUser(ConchUser):
    print "In User\n\n"
    utilobj = Util()
    shell = utilobj.find_git_shell()
    error_script = utilobj.find_error_script()

    def __init__(self, username, meta):
        ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({"session": SSHSession})
        self.meta = meta

    def logout(self): pass