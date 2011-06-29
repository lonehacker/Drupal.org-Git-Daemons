#! /usr/bin/python
import sys
sys.path.append('/Library/Python/2.6/site-packages/Drupal.org-Git-Daemons')
from drupalGitSSHDaemon import *
from twisted.cred.credentials import UsernamePassword, SSHPrivateKey
import random
from twisted.trial import unittest
from twisted.python.failure import Failure

class TestPubKeyAuth(unittest.TestCase):
    user = 'test'
    fingerprint = 'e4d3b1a13c247635a4f4b9fcd1d39298'
    blob = """ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA1qvRgJ/A9TGZAeYuUSQbn7+zrg2Ogs5+ehJ1s/+YE0s1b2m9PT8XkLUceHlMFGkoizHdNbFSJIanSUD91eQXBzMU333vc1ylBjcs1FBcRLyvrXaXsrZhqvnmlMMKhLjb2dn2d1PfmHYznLZGQaxOgMRUoOIJ5rIh3XCQNNbZE3eD/FS7XLWSgfwAFBnYm+uMY0vnPXJLPiNO9iMhekJWM3vKnKNCqyYgaZEIpqSnXekZjafy3uIGhANWKiwVZkLAN47tPxvgu//6IqR5yF59Zmk9JcuhsvsBG+BbddaNXdlQc7P3pY8QDi/7FHcUN9C2A2UYmFMHvpcuvsQ4HJCvOQ== xashck@gmail.com"""

    bad_blob = """ssh-rsa AAAAB3NzaC1kc3MAAACBAOsD7WxLruieczHv46el57qKweUJU3R9ECYEDFs799b4BxKnHeJ+UPzC6+BIWqBdJ3+WGMTCMlXpZy3BlcVNdYLRI+AGBmdPW1rQxo0F9xpakFo9h9LKfpKeZz4mWp7FCOgkBmFlvJS+j9GYB/FEOE9LDqx0O7gBdAepm9WOieavAAAAFQDg+VFpV3y0rJbiPvbxj9PGW918ywAAAIAcOlBMKYPdqumG7pdiZtrTYhtwrfulxDy/MOBCcxqyhwuf1hSZZD5xDGbLyI58PLq2asfme1zLU5BSn8TnJJz8ddf3TFFVSJHdE0txuPu8LIfU3DMH2IDa4P/iU0QXlgGIurYeydKklzQg6FeLI+mjqr6LaLhSyBh3bdqW9GCBDwAAAIAa+/R5Bi7u9u7nk+IrAkrUuZciR+HUERBKWLBlCgldSZouziRLq2SkKPEsED2zni80SQxVeIG84olrQlThh35iYsJFNwS4J9vxQ5AJzARMACFYK/EzuFkk2YPV0NfurKd1KUoU8cb+5ns+gwgqWy06/s8jr63cDKWJmm+Hn2RwkQ== demo@demo"""
    path = os.path.expanduser('../keys/id_rsa')
    privkey = Key.fromFile(path,passphrase='pikachu')
    sigData ="testdata"
    def setUp(self):
        self.meta = DrupalMeta()
        self.checker = GitPubKeyChecker(self.meta)

    def test_good_key(self):
        credentials = SSHPrivateKey(self.user, "ssh-rsa", self.blob, self.sigData, self.privkey.sign(self.sigData))
        deferred = self.checker.requestAvatarId(credentials)
        deferred.addCallback(self.assertEqual,self.user)
        return deferred

    def test_bad_key(self):
        credentials = SSHPrivateKey(self.user, "ssh-rsa", self.bad_blob, self.sigData, self.privkey.sign(self.sigData))
        deferred = self.checker.requestAvatarId(credentials)
        deferred.addErrback(self.flushLoggedErrors)
        deferred.addCallback(self.assertEquals,[])
        return deferred
    def test_good_key_git(self):
        credentials = SSHPrivateKey(self.user, "ssh-rsa", self.blob, self.sigData, self.privkey.sign(self.sigData))
        deferred = self.checker.requestAvatarId(credentials)
        deferred.addCallback(self.assertTrue)
        return deferred
    def test_bad_key_git(self):
        credentials = SSHPrivateKey(self.user, "ssh-rsa", self.bad_blob, self.sigData, self.privkey.sign(self.sigData))
        deferred = self.checker.requestAvatarId(credentials)
        deferred.addErrback(self.flushLoggedErrors)
        deferred.addCallback(self.assertEquals,[])
        return deferred

class TestPasswordAuth(unittest.TestCase):
    user = 'test'
    password = 'Thai1mil3ahb'
    password_hash = '3d6e6e70c75f60ccf3b0f57dff19aac6'

    def setUp(self):
        self.meta = DrupalMeta()
        self.checker = GitPasswordChecker(self.meta)

    def test_good_password(self):
        credentials = UsernamePassword(self.user, self.password)
        deferred = self.checker.requestAvatarId(credentials)
        deferred.addCallback(self.assertEqual,self.user)
        return deferred
    def test_bad_password(self):
        credentials = UsernamePassword(self.user, "the wrong password")
        deferred = self.checker.requestAvatarId(credentials)
        deferred.addErrback(self.flushLoggedErrors)
        #deferred.addCallback(self.assertEqual,failure)
        deferred.addCallback(self.assertEquals,[])
        return deferred

if __name__ == '__main__':
    unittest.main()