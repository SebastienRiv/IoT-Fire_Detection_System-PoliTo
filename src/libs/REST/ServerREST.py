import cherrypy
import threading

class ServerREST:
    exposed = True
    
    def __init__(self, host, port, config, GET, POST, PUT, DELETE) :
        self.host = host
        self.port = port
        self.config = config
        
        self.GET = GET
        self.POST = POST
        self.PUT = PUT
        self.DELETE = DELETE   
         
        self.serverRunTimeStatue = False
    
    def setupServer(self):
        cherrypy.tree.mount(self,'/',self.config) 
        cherrypy.config.update({'server.socket_port':self.port, 
                                'server.socket_host':self.host})
        
    def startServer(self):
        self.serverRunTimeStatue = True
        if not hasattr(self, 'serverThread') or not self.serverThread.is_alive():
            self.serverThread = threading.Thread(target=self.serverRunTime)
            self.serverThread.start()
        
    def serverRunTime(self):
        if self.serverRunTimeStatue :
            cherrypy.engine.start() 
            cherrypy.engine.block()
            
    def GET(self, *uri, **params):
        return self.GET(*uri, **params)
    
    def POST(self, *uri, **params):
        return self.POST(*uri, **params)
    
    def PUT(self, *uri, **params):
        return self.PUT(*uri, **params)
    
    def DELETE(self, *uri, **params):
        return self.DELETE(*uri, **params)