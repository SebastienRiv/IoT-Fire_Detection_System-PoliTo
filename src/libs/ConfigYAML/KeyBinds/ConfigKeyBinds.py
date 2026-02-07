class ConfigKeyBinds:
    def __init__(self, config):
        self.config = config

    @property
    def ClientID(self) -> str:
        return self.config.get("ClientID", "")
    
    @property
    def ClientName(self) -> str:
        return self.config.get("ClientName", "")
    
    @property
    def ConfigFile(self) -> str:
        return self.config.get("ConfigFile", "")
    
    @property
    def CatalogURL(self) -> str:
        return self.config.get("CatalogURL", "")
    
    @property
    def LifeTimeInterval(self) -> int:
        return self.config.get("LifeTimeInterval", 5)
    
    @property
    def CatalogUpdateIntervalCycles(self) -> int:
        return self.config.get("CatalogUpdateIntervalCycles", 20)
    
    @property
    def Threshold(self)->float:
        return self.config.get("Threshold",0.8)
    