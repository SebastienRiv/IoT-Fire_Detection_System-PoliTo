from abc import ABC, abstractmethod
import yaml
import requests
import threading
from time import sleep
from src.libs.REST.RequestREST import RequestREST
from src.libs.CatalogJSON.CatalogJSON import CatalogJSON
from src.libs.ConfigYAML.ConfigYAML import ConfigYAML

class Service(ABC):
    
    def __init__(self, configFilePath:str) -> None :

        self.localIP = ""
        
        self.configFilePath = configFilePath
        self.configLocal = ConfigYAML(self.configFilePath)
        self.configCatalog = CatalogJSON(self.configLocal, 'services')
        self.serviceRunTimeStatus = False
        
        self.requestREST = RequestREST(self.configLocal.getKey.CatalogURL)
        
        self.registeredSatus = self.registerServiceToCatalog()
        self.updateCatalogConfig()
            
    def setServiceRunTimeStatus(self, status:bool) -> None :
        self.serviceRunTimeStatus = status
            
    def updateCatalogConfig(self) -> bool :
        if self.configLocal.getKey.CatalogURL != "" :
            if not self.registeredSatus :
                self.registeredSatus = self.registerServiceToCatalog()
            
            update = self.requestREST.GET("getServiceByID", params={"serviceID": self.configLocal.getKey.ClientID})
            if "data" in update and update["data"] is not None :
                update = update["data"] 
            modified = self.configCatalog.updateCatalog(update)
            return modified
        return False
    
    def registerServiceToCatalog(self) -> bool :
        if self.configLocal.getKey.CatalogURL != "" :
            data = {
                "serviceID": self.getServiceID(),
                "serviceName": self.configLocal.getKey.ClientName,
                "serviceAddress": self.localIP,
                "servicePort": self.configLocal.get('Port', 5000)
            }
            #response = self.requestREST.PUT("servicesCatalog/register", data=data, params={"service_id": self.getServiceID()})
            #if response != {} :
            #    return True
        return False
                
    def updateLoopStart(self, updateInterval:int=12) -> None :
        if not hasattr(self, 'updateThread') or not self.updateThread.is_alive():
            self.updateThread = threading.Thread(target=self.updateLoopRunTime, args=(updateInterval,), daemon=True)
            self.updateThread.start()
           
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.serviceRunTimeStatus :
            modified = self.updateCatalogConfig()
                        
            sleep(self.configCatalog.get.catalogUpdateIntervalCycles)
                
    def getServiceID(self) -> str :
        serviceID = self.configLocal.getKey.ClientID
        if serviceID is not None :
            return serviceID
        else :
            print("Warning: ServiceID not found in local configuration.")
            return "UnknownID"
    
    def getConfigLocal(self) -> dict :
        return self.configLocal.getConfig()
    
    def getConfigCatalog(self) -> dict :
        return self.configCatalog.getCatalog()
    
    def setServiceRunTimeStatus(self, status:bool) -> None :
        self.serviceRunTimeStatus = status
    
    @abstractmethod
    def serviceRunTime(self) -> None :
        pass
         
    @abstractmethod     
    def killServiceRunTime(self) -> None :
        self.serviceRunTimeStatus = False