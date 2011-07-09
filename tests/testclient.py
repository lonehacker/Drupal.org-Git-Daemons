from twisted.conch.ssh import transport, userauth, connection, common, keys, channel
from twisted.internet import defer, protocol, reactor

class SimpleFactory(protocol.ClientFactory):
    def __init__(self):
        self.deferred = defer.Deferred()
    def data_rec(self,data):
        if self.deferred is not None:
             d , self.deferred = self.deferred , None
             d.callback(data)
    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)
class SimpleTransport(transport.SSHClientTransport):
    def verifyHostKey(self, hostKey, fingerprint):
        print 'host key fingerprint: %s' % fingerprint
        return defer.succeed(1) 

    def connectionSecure(self):
        self.connection = SimpleConnection()
        self.connection.protocol = self
        self.requestService(
            SimpleUserAuth(self.factory.user,
                self.connection))
class SimpleUserAuth(userauth.SSHUserAuthClient):
    def getPassword(self):
        return defer.succeed("Thai1mil3ahb")        
    def getPublicKey(self):
        print "trying public key"
        path = os.path.expanduser('~/.ssh/id_rsa') 
        # this works with rsa too 
        # just change the name here and in getPrivateKey
        if not os.path.exists(path) or self.lastPublicKey:
            # the file doesn't exist, or we've tried a public key
            return
        return keys.Key.fromFile(filename=path+'.pub',passphrase='pikachu').blob()
    def getPrivateKey(self):
        path = os.path.expanduser('~/.ssh/id_rsa')
        return defer.succeed(keys.Key.fromFile(path,passphrase='pikachu').keyObject)
class SimpleConnection(connection.SSHConnection):
    def serviceStarted(self):
        self.openChannel(CatChannel(conn = self))
    def serviceStopped(self):
        print "a"
class CatChannel(channel.SSHChannel):
    name = 'session'
    def openFailed(self, reason):
        print 'echo failed', reason

    def channelOpen(self, ignoredData):
        self.data = ''
        print "sending.."
        self.d = self.conn.sendRequest(self, 'exec', common.NS(self.conn.protocol.factory.command), wantReply = 1)
    def dataReceived(self, data):
        print "data received"
        self.data += data
    def closed(self):
        self.conn.protocol.factory.deferred.callback(self.data)