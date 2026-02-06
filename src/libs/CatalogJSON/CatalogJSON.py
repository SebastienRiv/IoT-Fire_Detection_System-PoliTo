import json
from src.libs.CatalogJSON.KeyBinds.CatalogKeyBinds import CatalogKeyBinds

class CatalogJSON:
    
    def __init__(self, configLocal, type) -> None: 
        self.configLocal = configLocal
        
        self.type = type
        
        self.catalog = {}
        self.templates = {}
        
        self.loadTemplates('./src/libs/CatalogJSON/Templates/CatalogTemplate.json')
        self.catalog = self.getTemplate(type)
        
        self.get = CatalogKeyBinds(self.catalog, self.configLocal)
        
    def loadTemplates(self, template_file: str) -> None:
        try :
            with open(template_file, 'r') as file:
                self.templates = json.load(file)
        except FileNotFoundError:
            print(f"Error loading templates: {template_file} not found.")
           
    def updateWithStatus(self, target:dict, updates:dict) :
        modified = False
        
        for key, value in updates.items():
            if key in target:
                if isinstance(target[key], dict) and isinstance(value, dict):
                    if self.updateWithStatus(target[key], value):
                        modified = True
                elif target[key] != value:
                    target[key] = value
                    modified = True

        return modified
            
    def updateCatalog(self, newCatalog) -> bool:
        modified = self.updateWithStatus(self.catalog, newCatalog)
        return modified
    
    def getTemplate(self, type) -> dict :
        match type :
            case 'devices' :
                return self.templates['devicesList'][0].copy()
            case 'services' :
                return self.templates['servicesList'][0].copy()
            case 'all' :
                return self.templates.copy()
            case _ :
                return {}
    
    def getCatalog(self) -> dict :
        return self.catalog.copy()
    
    def getType(self) -> str :
        return self.type