import json
from src.libs.CatalogJSON.KeyBinds.CatalogKeyBinds import CatalogKeyBinds

class CatalogJSON:
    
    def __init__(self, configLocal) -> None: 
        self.configLocal = configLocal
        
        self.catalog = {}
        self.templates = {}
        
        self.loadTemplates('./src/libs/CatalogJSON/Templates/CatalogTemplate.json')
        self.catalog = self.getTemplate()
        
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
            if key in target and target[key] != value:
                target[key] = value
                modified = True
        return modified
            
    def updateCatalog(self, newCatalog) -> bool:
        modified = self.updateWithStatus(self.catalog, newCatalog)
        return modified
    
    def getTemplate(self) -> dict :
        return self.templates.copy()
    
    def getCatalog(self) -> dict :
        return self.catalog.copy()