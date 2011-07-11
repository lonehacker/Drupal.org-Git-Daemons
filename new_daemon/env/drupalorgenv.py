import json
from zope import interface
from env.interfaces import IEnv
class DrupalorgEnv():
    interface.implements(IEnv)
    def setEnv(self,auth_results,user,router):
        user , auth_service = auth_results
        repo_id = auth_service["repo_id"]
        env = {}
        if user:
            # The UID is known, populate the environment
            env['VERSION_CONTROL_GIT_UID'] = user["uid"]
            env['VERSION_CONTROL_GIT_REPO_ID'] = repo_id
            env['VERSION_CONTROL_VCS_AUTH_DATA'] = json.dumps(auth_service)
        return env    