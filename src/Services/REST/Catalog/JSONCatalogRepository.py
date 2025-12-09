import json
import time
from src.libs.CatalogJSON.CatalogJSON import CatalogJSON
from src.Services.REST.Catalog.ICatalogRepository import ICatalogRepository  

class JSONCatalogRepository(ICatalogRepository):

    def __init__(self, filePath:str, configLocal) -> None:
        self.filePath = filePath
        self.catalogHelper = CatalogJSON(configLocal)
        self.catalogData = {}
        self._load()

    def _load(self) -> None:

        # Open the JSON file
        try:
            with open(self.filePath, 'r') as file:
                self.catalogData = json.load(file)
        except FileNotFoundError:
            # if file does not exist, takes template --> initialize
            self.catalogData = self.catalogHelper.getTemplate()
            self._save()
        except json.JSONDecodeError:
            # if file is corrupted, takes template --> initialize
            self.catalogData = self.catalogHelper.getTemplate()
            self._save()
        
    def _save(self) -> None:

        try:
            with open(self.filePath, 'w') as file:
                json.dump(self.catalogData, file, indent=4)
        except FileNotFoundError:
            print(f"Error saving catalog: {self.filePath} not found.")
        except IOError:
            print(f"Error saving catalog: I/O error occurred while writing to {self.filePath}.")        
        

    
    # GET
    def getCatalog(self) -> dict:
        return self.catalogData.copy()
    
    # PUT == UPDATE
    def updateCatalog(self, new_data: tuple[str, dict] | list[tuple[str, dict]]) -> bool:

        modified = False

        # check if new_data is a single tuple or list
        if isinstance(new_data, tuple):
            # if is a tuple, key = deviceID, value = dict
            key, value = new_data 
            for device in self.catalogData["devicesList"]:
                if device["deviceID"] == key:
                    lastUpdate = time.time()
                    value["lastUpdate"] = lastUpdate
                    modified = self.catalogHelper.updateWithStatus(device, value)
                    break
        elif isinstance(new_data, list):
            
            for item in new_data:
                key, value = item
                # if it exists, update == overwrite
                for device in self.catalogData["devicesList"]:
                    if device["deviceID"] == key:
                        lastUpdate = time.time()
                        value["lastUpdate"] = lastUpdate
                        modified = self.catalogHelper.updateWithStatus(device, value)
                        break
        
        if modified:
            self._save()
        return modified
    
    # GET BY ID
    def getResourceById(self, resource_id: str | list[str]) -> dict | list[dict]:
    
        data_tobe_returned = {} # initialized as empty dict because the return must be dict or list

        if isinstance(resource_id, str):
            for device in self.catalogData["devicesList"]:
                if device["deviceID"] == resource_id:
                    data_tobe_returned = device
                    break
        elif isinstance(resource_id, list):
            results = []
            for dev_id in resource_id:
                for device in self.catalogData["devicesList"]:
                    if device["deviceID"] == dev_id:
                        results.append(device)
                        break
            
            data_tobe_returned = results
        
        return data_tobe_returned
    
    # DELETE (BY ID)
    def removeResourceById(self, resource_id: str | list[str]) -> bool:
        
        modified = False

        if isinstance(resource_id, str):
            for index, device in enumerate(self.catalogData["devicesList"]):
                if device["deviceID"] == resource_id:
                    del self.catalogData["devicesList"][index]
                    modified = True
                    break
        elif isinstance(resource_id, list):
            for dev_id in resource_id:
                for index, device in enumerate(self.catalogData["devicesList"]):
                    if device["deviceID"] == dev_id:
                        del self.catalogData["devicesList"][index]
                        modified = True
                        break
        
        if modified:
            self._save()
        return modified
    
    # POST == ADD
    def addResource(self, new_resource: dict | list[dict]) -> bool:
        
        modified = False

        if isinstance(new_resource, dict):
            self.catalogData["devicesList"].append(new_resource)
            modified = True
        elif isinstance(new_resource, list):
            for resource in new_resource:
                self.catalogData["devicesList"].append(resource)
                modified = True
        
        if modified:
            self._save()
        return modified

