from src.Services.REST.RESTService import RESTService
from libs.CatalogJSON.JSONCatalogRepository import JSONCatalogRepository
from abc import ABC, abstractmethod
import json
import cherrypy
import time

class CatalogProviderService(RESTService, ABC):
    
    def __init__(self, configFilePath:str) -> None :

        # init parent RESTService
        super().__init__(configFilePath)
        
        self.catalogPath = self.configLocal.get("CatalogPath", "catalog.json")
        self.catalog = {}
        self.updateCatalog()

        # if we want to use a DB
        # self.dbPath = self.configLocal.get("DatabasePath", "catalog.db")
        # self.repository = SQLCatalogRepository(self.dbPath)

    def getCatalogPath(self) -> str :
        return self.catalogPath
    

    # REST methods

    def GET(self, *uri, **params):
        # GET is used to retrive the catalog or just specific devices given the IDs
        # GET / --> catalog
        # GET /getDeviceByID?deviceID=xxx --> specific device
        

    
    def getCatalog(self) -> dict :
        return self.catalog
    
    def updateCatalog(self) -> None :
        try : 
            with open(self.catalogPath, 'r') as file:
                try :
                    self.catalog = json.load(file)
                except json.JSONDecodeError:
                    print(f"Error: Failed to decode JSON from catalog file {self.catalogPath}.")
        except FileNotFoundError:
            print(f"Error: Catalog file {self.catalogPath} not found.")
            
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
        