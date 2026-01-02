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

        self.configFilePath = configFilePath
        self.configLocal = ConfigYAML(self.configFilePath)
        self.configCatalog = CatalogJSON(self.configLocal)
        self.serviceRunTimeStatus = False
        
        self.requestREST = RequestREST(self.configLocal.getKey.CatalogURL)
        
        self.updateCatalogConfig()
            
    def updateCatalogConfig(self) -> bool :
        if self.configLocal.getKey.CatalogURL != "" :
            update = self.requestREST.GET("", params={"service_id": self.configLocal.getKey.ClientID})
            modified = self.configCatalog.updateCatalog(update)
            return modified
        return False
                
    def updateLoopStart(self, updateInterval:int=12) -> None :
        if not hasattr(self, 'updateThread') or not self.updateThread.is_alive():
            self.updateThread = threading.Thread(target=self.updateLoopRunTime, args=(updateInterval,), daemon=True)
            self.updateThread.start()
           
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.serviceRunTimeStatus :
            modified = self.updateCatalogConfig()

            if modified:
                self.onConfigUpdate()
                        
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
    
    def killServiceRunTime(self) -> None :
        self.serviceRunTimeStatus = False

        self.onKill()
    
    @abstractmethod
    def onConfigUpdate(self) -> None :
        """
        Method called automatically when the configuration changes.
        """
        pass
    
    @abstractmethod
    def serviceRunTime(self) -> None :
        """
        Keeping the service alive by periodically checking
        the execution status
        """
        pass

    @abstractmethod
    def onKill(self) -> None :
        """
        Services can do some specific cleaning tasks 
        at the end of the run time
        """
        pass
            