class Env():
    def __init__(self,user,router):
        self.user = user
        self.router = router
        from drupalorgenv import DrupalorgEnv
        self.envservice = DrupalorgEnv()
    def setEnv(self,auth_results):
        return self.envservice.setEnv(auth_results,self.user,self.router)    