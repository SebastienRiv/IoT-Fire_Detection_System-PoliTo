from typing import Any
from src.Services.REST.RESTService import RESTService
from abc import ABC, abstractmethod
import json
import cherrypy
import time

class CatalogProviderService(RESTService, ABC):
    
    def __init__(self, configFilePath:str) -> None :

        # init parent RESTService
        super().__init__(configFilePath)
        self.configCatalog.updateCatalog(self.genCatalogueFormat())
        super().restSetupServer()
        
        self.catalogPath = self.configLocal.getKey.Extra.get("CatalogPath", "catalog.json")
        self.catalog = {}

        # if we want to use a DB
        # self.dbPath = self.configLocal.getKey.Extra.get("DatabasePath", "catalog.db")
        # self.repository = SQLCatalogRepository(self.dbPath)
        
    def genCatalogueFormat(self) -> dict : # self registration for running purpose only
        catalog_data = {
            "serviceID": str(self.configLocal.getKey.ClientID),
            "serviceName": self.configLocal.getKey.ClientName,
            "lifeTimeInterval": self.configLocal.getKey.LifeTimeInterval,
            "catalogUpdateIntervalCycles": self.configLocal.getKey.CatalogUpdateIntervalCycles,
            "availableServices": self.configLocal.getKey.AvailableServices,
            "MQTT": self.configLocal.getKey.MQTT,
            "REST": self.configLocal.getKey.REST,
            "extra": self.configLocal.getKey.Extra,
            "lastUpdate": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        }
        return catalog_data

    def registerServiceToCatalog(self) -> bool:
        return True # we don't need to register, this service provides static catalog

    @abstractmethod
    def GET(self, *uri, **params) -> Any :
        # return NotImplementedError("GET method not implemented.")
        pass

    @abstractmethod
    def POST(self, *uri, **params) -> Any :
        # return NotImplementedError("POST method not implemented.")
        pass
    
    @abstractmethod
    def PUT(self, *uri, **params) -> Any :
        # return NotImplementedError("PUT method not implemented.")
        pass
    
    @abstractmethod
    def DELETE(self, *uri, **params) -> Any :
        # return NotImplementedError("DELETE method not implemented.")
        pass
    
    def updateLoopStart(self, updateInterval:int=12) -> None : # we don't need to update, this service provides static catalog
        pass
    
    def updateLoopRunTime(self, updateInterval:int=12) -> None : # we don't need to update, this service provides static catalog
        pass
    
    @abstractmethod
    def serviceRunTime(self) -> None :
        pass
    
    @abstractmethod
    def killServiceRunTime(self) -> None:
        return super().killServiceRunTime()
        