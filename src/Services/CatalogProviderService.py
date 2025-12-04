from src.Services.RESTService import RESTService
import json

class CatalogProviderService(RESTService):
    
    def __init__(self, configFilePath:str) -> None :
        super().__init__(configFilePath)
        
        self.catalogPath = self.configLocal.get("CatalogPath", "catalog.json")
        self.catalog = {}
        
        self.updateCatalog()
           
    def getCatalogPath(self) -> str :
        return self.catalogPath
    
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
            
    def POST(self, *uri, **params):
        return NotImplementedError("POST method not implemented.")
    
    def GET(self, *uri, **params):
        return NotImplementedError("GET method not implemented.")
    
    def PUT(self, *uri, **params):
        return NotImplementedError("PUT method not implemented.")
    
    def DELETE(self, *uri, **params):
        return NotImplementedError("DELETE method not implemented.")
    
    def updateLoopStart(self, updateInterval:int=12) -> None : # we don't need to update, this service provides static catalog
        pass
    
    def updateLoopRunTime(self, updateInterval:int=12) -> None : # we don't need to update, this service provides static catalog
        pass
    
    def serviceRunTime(self) -> None :
        pass
    
    def killServiceRunTime(self) -> None:
        return super().killServiceRunTime()
        