from abc import ABC, abstractmethod
from src.Services.Service import Service
from src.libs.REST.ServerREST import ServerREST
from time import sleep

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
        
        if self.configCatalog.get.restServerHost != "" and self.configCatalog.get.restServerPort != "" and self.configCatalog.get.restServerConfig != "" :
            
            if self.serverREST is not None:
                self.serverREST.killServerRunTime()
            
            self.host = self.configCatalog.get.restServerHost
            self.port = self.configCatalog.get.restServerPort
            self.restServiceConfig = self.configCatalog.get.restServerConfig
            
            self.serverREST = ServerREST(self.host, self.port, self.restServiceConfig, self.GET, self.POST, self.PUT, self.DELETE)
            
            self.serverREST.setupServer()
            self.serverREST.startServer()
            
        else :
            print("Warning: REST Server configuration not found in service catalog. REST Server functionalities will be disabled.")
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
        # return NotImplementedError("POST method not implemented.")
        pass
    
    @abstractmethod 
    def GET(self, *uri, **params):
        # return NotImplementedError("GET method not implemented.")
        pass
    
    @abstractmethod 
    def PUT(self, *uri, **params):
        # return NotImplementedError("PUT method not implemented.")
        pass
    
    @abstractmethod
    def DELETE(self, *uri, **params):
        # return NotImplementedError("DELETE method not implemented.")
        pass
    
    @abstractmethod
    def serviceRunTime(self) -> None :
        pass
    
    @abstractmethod
    def killServiceRunTime(self) -> None:
        if self.serverREST is not None:
            self.serverREST.killServerRunTime()