from twisted.conch.error import ConchError, UnauthorizedLogin, ValidPublicKey
from twisted.python.failure import Failure
from twisted.conch.ssh.keys import Key
from twisted.internet import reactor, defer
from twisted.internet.defer import DeferredList
from zope import interface

from config import config
from service import Service
from service.protocols import AuthProtocol
from utils import Util
from Router import Router
import os
import urllib
import base64
import hashlib
import json

class Authenticator(object):
    def __init__(self,user):
        self.user = user
    def pushcontrol(self, deferred_results, argv):
        auth_result, pushctl_result = deferred_results
        auth_status, auth_service = auth_result
        pushctl_status, pushctl_service = pushctl_result
        if not auth_service:
            error = "Repository does not exist. Verify that your remote is correct."
            raise ConchError(error)
        if pushctl_status and auth_status:
            mask = auth_service["repo_group"] & pushctl_service
            if mask:
                error = "Pushes for this type of repo are currently disabled."
                # This type of repo has pushes disabled
                if mask & 0x01:
                    error = "Pushes to core are currently disabled."
                if mask & 0x02:
                    error = "Pushes to projects are currently disabled."
                if mask & 0x04:
                    error = "Pushes to sandboxes are currently disabled."
                return Failure(ConchError(error))
            else:
                # Good to continue with auth
                return auth_service
        elif not auth_status:
            # This will be a failure, not the auth data in this case
            return auth_service
        else:
            return pushctl_service
    def auth(self, auth_service, argv):
        """Verify we have permission to run the request command."""
        # Key fingerprint
        if hasattr(self.user.meta, "fingerprint"):
            fingerprint = self.user.meta.fingerprint
        else:
            fingerprint = None

        if hasattr(self.user.meta, "password"):
            password = self.user.meta.password
        else:
            password = None

        # Check permissions by mapping requested path to file system path
        # Map the user
        users = auth_service["users"]
        user = self.map_user(self.user.username, fingerprint, users)
        execGitCommand = user, auth_service
        

        # Check to see if anonymous read access is enabled and if
        # this is a read
        if (not self.user.meta.anonymousReadAccess or \
                'git-upload-pack' not in argv[:-1]):
            # First, error out if the project itself is disabled.
            
            if not auth_service["status"]:
                error = "Project {0} has been disabled.".format(projectname)
                return Failure(ConchError(error))
            # If anonymous access for this type of command is not allowed,
            # check if the user is a maintainer on this project
            # global values - d.o issue #1036686
            # "git":key
            if self.user.username == "git" and user and not user["global"]:
                return execGitCommand
            # Username in maintainers list
            elif self.user.username not in users:
                error = "User '{1}' does not have write permissions for repository '{0}'".format(projectname, self.user.username)
                return Failure(ConchError(error))
            elif not user["global"]:
                # username:key
                print "here" + user["pass"]
                print password
                if fingerprint in user["ssh_keys"].values():
                    return execGitCommand
                # username:password
                elif user["pass"] == password:
                    return execGitCommand
                else:
                    # Both kinds of username auth failed
                    error = "Permission denied when accessing '{0}' as user '{1}'".format(projectname, self.user.username)
                    return Failure(ConchError(error))
            else:
                # Account is globally disabled or disallowed
                # 0x01 = no Git user role, but unknown reason (probably a bug!)
                # 0x02 = Git account suspended
                # 0x04 = Git ToS unchecked
                # 0x08 = Drupal.org account blocked
                error = ''
                if user["global"] & 0x02:
                    error += "Your Git access has been suspended.\n"
                if user["global"] & 0x04:
                    error += "You are required to accept the Git Access Agreement in your user profile before using Git.\n"
                if user["global"] & 0x08:
                    error += "Your Drupal.org account has been blocked.\n"

                if not error and user["global"] == 0x01:
                    error = "You do not have permission to access '{0}' with the provided credentials.\n".format(projectname)
                elif not error:
                    # unknown situation, but be safe and error out
                    error = "This operation cannot be completed at this time.  It may be that we are experiencing technical difficulties or are currently undergoing maintenance."
                return Failure(ConchError(error))
        else:
            # Read only command and anonymous access is enabled
            return execGitCommand
    def map_user(self, username, fingerprint, users):
        """Map the username from name or fingerprint, to users item."""
        if username == "git":
            # Use the fingerprint
            for user in users.values():
                if fingerprint in user["ssh_keys"].values():
                    return user
            # No fingerprints match
            return None
        elif username in users:
            # Use the username
            return users[username]
        else:
            return None
class DrupalMeta(object):
    def __init__(self):
        self.anonymousReadAccess = config.getboolean('drupalSSHGitServer', 'anonymousReadAccess')
        self.utilobj = Util()
    def request(self,isLocal,uri):
        """Build the request to run against drupal

        request(project uri)

        Values and structure returned:
        {username: {uid:int, 
                    repo_id:int, 
                    access:boolean, 
                    branch_create:boolean, 
                    branch_update:boolean, 
                    branch_delete:boolean, 
                    tag_create:boolean,
                    tag_update:boolean,
                    tag_delete:boolean,
                    per_label:list,
                    name:str,
                    pass:md5,
                    ssh_keys: { key_name:fingerprint }
                   }
        }"""
        if not isLocal:
           return Failure("Repository is not local")
        auth_service = Service(AuthProtocol('vcs-auth-data'))
        auth_service.request_json({"project_uri":self.utilobj.getprojectname(uri)})
        pushctl_service= Service(AuthProtocol('pushctl-state'))
        pushctl_service.request_json()
       
        def NoDataHandler(fail):
            fail.trap(ConchError)
            message = fail.value.value
            log.err(message)
            # Return a stub auth_service object
            return {"users":{}, "repo_id":None}
        auth_service.addErrback(NoDataHandler)
        #d1.addErrback(NoDataHandler)
        return DeferredList([auth_service.deferred, pushctl_service.deferred])
        #return DeferredList([d1,d2])
