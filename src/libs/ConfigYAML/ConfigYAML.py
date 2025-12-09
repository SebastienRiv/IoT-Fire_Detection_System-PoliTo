from src.libs.ConfigYAML.KeyBinds.ConfigKeyBinds import ConfigKeyBinds
import yaml

class ConfigYAML:
    
    def __init__(self, filePath: str) -> None:        
        self.filePath = filePath
        self.config = {}
        self.loadConfig()
        
        self.getKey = ConfigKeyBinds(self.config)
        
    def loadConfig(self) -> None:
        try:
            with open(self.filePath, 'r') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Configuration file {self.filePath} not found.")
    
    def getConfig(self) -> dict:
        return self.config.copy()
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)