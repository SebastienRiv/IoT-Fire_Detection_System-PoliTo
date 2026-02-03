from abc import ABC, abstractmethod
from src.Services.Service import Service
from src.libs.REST.ServerREST import ServerREST
from time import sleep
import cherrypy

class RESTService(Service, ABC):
    
    def __init__(self, configFilePath:str) -> None :
        super().__init__(configFilePath)
        
        self.host = None
        self.port = None
        self.restServiceConfig = None
        
        self.serverREST = None
        
        self.restSetupServer()
        
    def gethost(self) :
        return self.host
    
    def getport(self) :
        return self.port
    
    def getRESTServiceConfig(self):
        return self.restServiceConfig
        
    def restSetupServer(self) -> None :
        
        # Try catalog config first, then fallback to local config
        host = ""
        port = ""
        config = ""
        
        if self.configCatalog.get.restServerHost != "" :
            host = self.configCatalog.get.restServerHost
            port = self.configCatalog.get.restServerPort
            config = self.configCatalog.get.restServerConfig
        elif self.configLocal.get("RESTServerHost", "") != "" :
            host = self.configLocal.get("RESTServerHost", "")
            port = self.configLocal.get("RESTServerPort", "")
            config = self.configLocal.get("RESTServerConfig", "/")
        
        if host != "" and port != "" :
            if self.serverREST is not None:
                self.serverREST.killServerRunTime()
            
            self.host = host
            self.port = int(port)
            
            # Config doit être un dict pour CherryPy
            if isinstance(config, dict):
                self.restServiceConfig = config
            else:
                self.restServiceConfig = {
                    '/': {
                        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                        'tools.sessions.on': True
                    }
                }
            
            self.serverREST = ServerREST(self.host, self.port, self.restServiceConfig, self.GET, self.POST, self.PUT, self.DELETE)
            
            self.serverREST.setupServer()
            self.serverREST.startServer()
            print(f"Info: REST Server started on {self.host}:{self.port}")
            
        else :
            print("Warning: REST Server configuration not found. REST Server functionalities will be disabled.")
            self.serverREST = None
        
    def updateLoopRunTime(self, updateInterval:int = 12) -> None:
        while self.serviceRunTimeStatus :
            modified = self.updateCatalogConfig()
            
            if modified :
                print("Info: Service catalog updated. Restarting REST server with new configuration.")
                self.restSetupServer()
                        
            sleep(self.configCatalog.get.catalogUpdateIntervalCycles)
       
    @abstractmethod 
    def POST(self, *uri, **params):
        return NotImplementedError("POST method not implemented.")
    
    @abstractmethod 
    def GET(self, *uri, **params):
        return NotImplementedError("GET method not implemented.")
    
    @abstractmethod 
    def PUT(self, *uri, **params):
        return NotImplementedError("PUT method not implemented.")
    
    @abstractmethod
    def DELETE(self, *uri, **params):
        return NotImplementedError("DELETE method not implemented.")
    
    @abstractmethod
    def serviceRunTime(self) -> None :
        pass
    
    @abstractmethod
    def killServiceRunTime(self) -> None:
        if self.serverREST is not None:
            self.serverREST.killServerRunTime()