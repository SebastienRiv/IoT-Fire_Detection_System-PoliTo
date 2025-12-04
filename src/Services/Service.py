import yaml
import requests
import threading
from time import sleep
from src.libs.REST.RequestREST import RequestREST

class Service:
    
    def __init__(self, configFilePath:str) -> None :
        self.configFilePath = configFilePath
        self.configLocal = {}
        self.configCatalog = {}
        self.serviceRunTimeStatus = False
        
        self.updateLocalConfig()
        
        self.requestREST = RequestREST(self.configLocal.get("ServiceCatalogURL", ""))
        
        self.updateCatalogConfig()
        
    def updateLocalConfig(self) -> None :
        try : 
            with open(self.configFilePath, 'r') as file:
                self.configLocal = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Configuration file {self.configFilePath} not found.")
            
    def updateCatalogConfig(self) -> None :
        if "ServiceCatalogURL" in self.configLocal:
            self.configCatalog = self.requestREST.GET("", params={"service_id": self.configLocal.get("ServiceID", "")})
                
    def updateLoopStart(self, updateInterval:int=12) -> None :
        if not hasattr(self, 'updateThread') or not self.updateThread.is_alive():
            self.updateThread = threading.Thread(target=self.updateLoopRunTime, args=(updateInterval,), daemon=True)
            self.updateThread.start()
           
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.serviceRunTimeStatus :
            oldCatalog = self.configCatalog.copy()
            self.updateCatalogConfig()
                        
            sleep(self.configCatalog.get("CatalogUpdateIntervalCycles", self.configLocal.get("CatalogUpdateIntervalCycles", updateInterval)))
                
    def getServiceID(self) -> str :
        serviceID = self.configLocal.get("ServiceID", "UnknownServiceID")
        if serviceID is not None :
            return serviceID
        else :
            print("Warning: ServiceID not found in local configuration.")
            return "UnknownID"
    
    
    def getConfigLocal(self) -> dict :
        return self.configLocal
    
    def getConfigCatalog(self) -> dict :
        return self.configCatalog
    
    def serviceRunTime(self) -> None :
        pass
              
    def killServiceRunTime(self) -> None :
        self.serviceRunTimeStatus = False