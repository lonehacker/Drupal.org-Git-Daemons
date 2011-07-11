from app import envs
class Env():
    def __init__(self,user,router):
        self.user = user
        self.router = router
        envservice = getattr(envs,"DrupalorgEnv")
        self.envservice = envservice()
    def setEnv(self,auth_results):
        return self.envservice.setEnv(auth_results,self.user,self.router)    