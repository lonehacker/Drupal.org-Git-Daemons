from base64 import b64encode
from config import config
from service import IServiceProtocol
from twisted.conch.error import ConchError
from twisted.internet import reactor, defer
from twisted.internet.protocol import ProcessProtocol
from twisted.python import log
from twisted.web.client import getPage
from twisted.web.error import Error
import urllib, urlparse
from zope.interface import implements
auth_protocol = config.get('drupalSSHGitServer', 'authServiceProtocol')
if auth_protocol == "drush":
    # Load drush settings from drupaldaemons.cnf
    drush_webroot = config.get('drush-settings', 'webroot')
    drush_path = config.get('drush-settings', 'drushPath')
elif auth_protocol == "http":
    # Load http settings
    http_service_url = config.get('http-settings', 'serviceUrl')
    http_headers = {}
    if config.has_option('http-settings', 'hostHeader'):
        http_host_header = config.get('http-settings', 'hostHeader')
        http_headers["Host"] = http_host_header
    if config.has_option('http-settings', 'httpAuth'):
        http_auth = b64encode(config.get('http-settings', 'httpAuth'))
        http_headers["Authorization"] = "Basic " + http_auth
elif auth_protocol == "stub_service":
	print "Using Stubs for testing"
else:
    raise Exception("No valid authServiceProtocol specified.")

class DrushError(ConchError):
    pass

class HTTPError(ConchError):
    pass

class DrushProcessProtocol(ProcessProtocol):
    implements(IServiceProtocol)
    """Read string values from Drush"""
    def __init__(self, command):
        self.raw = ""
        self.raw_error = ""
        self.deferred = defer.Deferred()
        self.command = command

    def outReceived(self, data):
        self.raw += data

    def errReceived(self, data):
        self.raw_error += data

    def outConnectionLost(self):
        self.result = self.raw.strip()

    def processEnded(self, status):
        if self.raw_error:
            log.err("Errors reported from drush:")
            for each in self.raw_error.split("\n"):
                log.err("  " + each)
        rc = status.value.exitCode
        if self.result and rc == 0:
            self.deferred.callback(self.result)
        else:
            if rc == 0:
                err = DrushError("Failed to read from drush.")
            else:
                err = DrushError("Drush failed ({0})".format(rc))
            self.deferred.errback(err)

    def request(self, *args):
        exec_args = [drush_path, 
                     "--root={0}".format(drush_webroot), 
                     self.command]
        for a in args:
            exec_args += a.values()
        reactor.spawnProcess(self, drush_path, exec_args, env={"TERM":"dumb"})
        return self.deferred

class HTTPServiceProtocol(object):
    implements(IServiceProtocol)
    def __init__(self, url):
        self.deferred = None
        self.command = url

    def http_request_error(self, fail):
        fail.trap(Error)
        raise HTTPError("Could not open URL for {0}.".format(self.command))

    def request(self, *args):
        arguments = dict()
        for a in args:
            arguments.update(a)
        url_arguments = self.command + "?" + urllib.urlencode(arguments)
        constructed_url = urlparse.urljoin(http_service_url, url_arguments)
        self.deferred = getPage(constructed_url, headers=http_headers)
        self.deferred.addErrback(self.http_request_error)

class StubServiceProtocol(object):
    implements(IServiceProtocol)
    def __init__(self, command):
        self.deferred = defer.Deferred()
        self.command = command
    def request(self,*args):
        exec_args = []
        for a in args:
            exec_args += a.values()
        if self.command == 'drupalorg-ssh-user-key':
		    uname = exec_args[0]
		    key = exec_args[1]
		    realkey = "df77b58486045d5f31c45126c44c5ff7"
		    if key == realkey :
			    self.deferred.callback("true")
		    else :
			    self.deferred.callback("false")
        elif self.command == 'pushctl-state':
	        self.deferred.callback("0")
        elif self.command == 'vcs-auth-data':
		    data = "{\"project\":\"Drupal core\",\"project_nid\":\"3060\",\"repository_name\":\"drupal\",\"repo_id\":\"4\",\"status\":\"1\",\"users\":{\"drumm\":{\"uid\":\"3064\",\"repo_id\":\"4\",\"access\":\"2\",\"branch_create\":\"0\",\"branch_update\":\"0\",\"branch_delete\":\"0\",\"tag_create\":\"0\",\"tag_update\":\"0\",\"tag_delete\":\"0\",\"per-label\":[],\"name\":\"drumm\",\"pass\":\"\",\"ssh_keys\":{\" \":\" \"},\"global\":0},\"webchick\":{\"uid\":\"24967\",\"repo_id\":\"4\",\"access\":\"2\",\"branch_create\":\"0\",\"branch_update\":\"0\",\"branch_delete\":\"0\",\"tag_create\":\"0\",\"tag_update\":\"0\",\"tag_delete\":\"0\",\"per-label\":[],\"name\":\"webchick\",\"pass\":\"d41d8cd98f00b204e9800998ecf8427e\",\"ssh_keys\":{\" \":\" \"},\"global\":0},\"rfay\":{\"uid\":\"30906\",\"repo_id\":\"4\",\"access\":\"2\",\"branch_create\":\"0\",\"branch_update\":\"0\",\"branch_delete\":\"0\",\"tag_create\":\"0\",\"tag_update\":\"0\",\"tag_delete\":\"0\",\"per-label\":[],\"name\":\"rfay\",\"pass\":\"\",\"ssh_keys\":{\" \":\" \"},\"global\":0},\"dries\":{\"uid\":\"1\",\"repo_id\":\"4\",\"access\":\"2\",\"branch_create\":\"0\",\"branch_update\":\"0\",\"branch_delete\":\"0\",\"tag_create\":\"0\",\"tag_update\":\"0\",\"tag_delete\":\"0\",\"per-label\":[],\"name\":\"Dries\",\"pass\":\"\",\"ssh_keys\":{\" \":\" \"},\"global\":0},\"\":{\"uid\":\"3\",\"repo_id\":\"4\",\"access\":\"2\",\"branch_create\":\"0\",\"branch_update\":\"0\",\"branch_delete\":\"0\",\"tag_create\":\"0\",\"tag_update\":\"0\",\"tag_delete\":\"0\",\"per-label\":[],\"name\":\"Drupal\",\"pass\":\"\",\"ssh_keys\":{\" \":\" \"},\"global\":1},\"goba\":{\"uid\":\"4166\",\"repo_id\":\"4\",\"access\":\"2\",\"branch_create\":\"0\",\"branch_update\":\"0\",\"branch_delete\":\"0\",\"tag_create\":\"0\",\"tag_update\":\"0\",\"tag_delete\":\"0\",\"per-label\":[],\"name\":\"G\u00e1bor Hojtsy\",\"pass\":\"\",\"ssh_keys\":{\" \":\" \"},\"global\":1},\"killes\":{\"uid\":\"227\",\"repo_id\":\"4\",\"access\":\"2\",\"branch_create\":\"0\",\"branch_update\":\"0\",\"branch_delete\":\"0\",\"tag_create\":\"0\",\"tag_update\":\"0\",\"tag_delete\":\"0\",\"per-label\":[],\"name\":\"killes@www.drop.org\",\"pass\":\"\",\"ssh_keys\":{\" \":\" \"},\"global\":1}},\"protected_labels\":{\"tags\":[\"DRUPAL-4-3-0-RC\",\"DRUPAL-4-1-1\",\"DRUPAL-4-5-0-RC\",\"4.4.0\",\"DRUPAL-4-6-0-RC\",\"4.0.0\",\"4.4.2\",\"4.5.0\",\"4.1.0\",\"4.3.1\",\"4.5.2\",\"4.2.0\",\"4.4.1\",\"4.3.0\",\"4.5.1\",\"x_y_z\",\"4.3.2\",\"4.6.0\",\"4.5.3\",\"4.6.1\",\"4.4.3\",\"4.5.4\",\"4.6.2\",\"4.5.5\",\"4.6.3\",\"4.5.6\",\"4.6.4\",\"DRUPAL-4-7-0-BETA-1\",\"4.5.7\",\"4.6.5\",\"DRUPAL-4-7-0-BETA-2\",\"4.7.0-beta-3\",\"4.7.0-beta-4\",\"4.7.0\",\"4.7.0-rc-4\",\"4.7.0-rc-3\",\"4.7.0-beta-5\",\"4.5.8\",\"4.6.6\",\"4.7.0-beta-6\",\"4.7.0-rc-1\",\"4.7.0-rc-2\",\"4.7.1\",\"4.6.7\",\"4.7.2\",\"4.6.8\",\"4.7.3\",\"4.6.9\",\"4.7.4\",\"4.6.10\",\"5.0-beta-1\",\"5.0-beta-2\",\"5.0-rc-1\",\"4.6.11\",\"4.7.5\",\"5.0-rc-2\",\"5.0\",\"4.7.6\",\"5.1\",\"5.2\",\"4.7.7\",\"6.0-beta-1\",\"5.3\",\"4.7.8\",\"6.0-beta-2\",\"6.0-beta-3\",\"4.7.9\",\"5.4\",\"6.0-beta-4\",\"5.5\",\"4.7.10\",\"6.0-rc-1\",\"5.6\",\"4.7.11\",\"6.0-rc-2\",\"5.7\",\"6.0-rc-3\",\"6.0-rc-4\",\"6.0\",\"6.1\",\"6.2\",\"6.3\",\"5.8\",\"5.9\",\"5.10\",\"6.4\",\"5.11\",\"6.5\",\"6.6\",\"5.12\",\"6.7\",\"5.13\",\"5.14\",\"6.8\",\"5.15\",\"6.9\",\"6.10\",\"5.16\",\"5.17\",\"6.11\",\"6.12\",\"5.18\",\"6.13\",\"5.19\",\"6.14\",\"5.20\",\"5.21\",\"6.15\",\"7.0-alpha1\",\"7.0-alpha2\",\"6.16\",\"5.22\",\"7.0-alpha3\",\"7.0-alpha4\",\"7.0-alpha5\",\"6.17\",\"7.0-alpha6\",\"6.18\",\"6.19\",\"5.23\",\"7.0-alpha7\",\"7.0-beta1\",\"7.0-beta2\",\"7.0-beta3\",\"7.0-rc-1\",\"7.0-rc-2\",\"6.20\",\"7.0-rc-3\",\"7.0-rc-4\",\"7.0\"],\"branches\":[\"5.x\",\"6.x\",\"4.6.x\",\"master\",\"HEAD\"]},\"repo_group\":1}"
		    self.deferred.callback(data)
        elif self.command == 'drupalorg-vcs-auth-check-user-pass':
		    passwd = exec_args[1]
		    goodpasswd = "3d6e6e70c75f60ccf3b0f57dff19aac6"
		    if passwd == goodpasswd:
		        self.deferred.callback("true")
		    else :
			    self.deferred.callback("false")

if auth_protocol == "drush":
    AuthProtocol = DrushProcessProtocol
elif auth_protocol == "http":
    AuthProtocol = HTTPServiceProtocol
elif auth_protocol == "stub_service":
	AuthProtocol = StubServiceProtocol