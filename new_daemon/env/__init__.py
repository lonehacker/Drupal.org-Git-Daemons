from app import envs
from config import config
class Env():
    def __init__(self,user,router):
        self.user = user
        self.router = router
        envservice = getattr(envs,config.get('application','EnvModule'))
        self.envservice = envservice()
    def setEnv(self,auth_results):
        return self.envservice.setEnv(auth_results,self.user,self.router)    