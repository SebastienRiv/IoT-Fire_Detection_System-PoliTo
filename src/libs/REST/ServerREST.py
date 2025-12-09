import cherrypy
import threading

class ServerREST:
    exposed = True
    
    def __init__(self, host, port, config, myGET, myPOST, myPUT, myDELETE) :
        self.host = host
        self.port = port
        self.config = config
        
        self.myGET = myGET
        self.myPOST = myPOST
        self.myPUT = myPUT
        self.myDELETE = myDELETE   
         
        self.serverRunTimeStatue = False
    
    def getServerRunTimeStatue(self) -> bool :
        return self.serverRunTimeStatue
    
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
        cherrypy.engine.start() 
        cherrypy.engine.block()
        
    def killServerRunTime(self):
        self.serverRunTimeStatue = False
        cherrypy.engine.exit()
        
    def GET(self, *uri, **params):
        return self.myGET(*uri, **params)
    
    def POST(self, *uri, **params):
        return self.myPOST(*uri, **params)
    
    def PUT(self, *uri, **params):
        return self.myPUT(*uri, **params)
    
    def DELETE(self, *uri, **params):
        return self.myDELETE(*uri, **params)