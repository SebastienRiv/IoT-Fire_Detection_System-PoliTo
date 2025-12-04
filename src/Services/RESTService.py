from src.Services.Service import Service
from src.libs.REST.ServerREST import ServerREST
from time import sleep

class RESTService(Service):
    
    def __init__(self, configFilePath:str) -> None :
        super().__init__(configFilePath)
        
        self.host = None
        self.port = None
        self.restServiceConfig = None
        
        self.serverREST = None
        
        self.restSetupServer()
        
    def gethost(self) -> str :
        return self.host
    
    def getport(self) -> int :
        return self.port
    
    def getRESTServiceConfig(self) -> dict :
        return self.restServiceConfig
        
    def restSetupServer(self) -> None :
        
        if "RESTServerHost" in self.configCatalog and "RESTServerPort" in self.configCatalog and "RESTServerConfig" in self.configCatalog :
            
            if self.serverREST is not None:
                self.serverREST.killServerRunTime()
            
            self.host = self.configCatalog.get("RESTServerHost", self.configLocal.get("RESTServerHost", None))
            self.port = self.configCatalog.get("RESTServerPort", self.configLocal.get("RESTServerPort", None))
            self.restServiceConfig = self.configCatalog.get("RESTServerConfig", self.configLocal.get("RESTServerConfig", None))
            
            self.serverREST = ServerREST(self.host, self.port, self.restServiceConfig, self.GET, self.POST, self.PUT, self.DELETE)
            
            self.serverREST.setupServer()
            self.serverREST.startServer()
            
        else :
            print("Warning: REST Server configuration not found in service catalog. REST Server functionalities will be disabled.")
            self.serverREST = None
        
    def updateLoopRunTime(self, updateInterval:int = 12) -> None:
        while self.serviceRunTimeStatus :
            oldCatalog = self.configCatalog.copy()
            self.updateCatalogConfig()
            
            if oldCatalog != self.configCatalog :
                print("Info: Service catalog updated. Restarting REST server with new configuration.")
                self.restSetupServer()
                        
            sleep(self.configCatalog.get("CatalogUpdateIntervalCycles", self.configLocal.get("CatalogUpdateIntervalCycles", updateInterval)))
        
    def POST(self, *uri, **params):
        return NotImplementedError("POST method not implemented.")
    
    def GET(self, *uri, **params):
        return NotImplementedError("GET method not implemented.")
    
    def PUT(self, *uri, **params):
        return NotImplementedError("PUT method not implemented.")
    
    def DELETE(self, *uri, **params):
        return NotImplementedError("DELETE method not implemented.")
    
    def serviceRunTime(self) -> None :
        pass
    
    def killServiceRunTime(self) -> None:
        self.serverREST.killServerRunTime()