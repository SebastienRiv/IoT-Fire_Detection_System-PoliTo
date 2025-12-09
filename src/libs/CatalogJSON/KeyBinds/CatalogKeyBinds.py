class CatalogKeyBinds:
    
    def __init__(self, catalog, configLocal) -> None:
        self.catalog = catalog
        self.configLocal = configLocal
    
    # Property for clientID
    @property 
    def clientID(self):
        return self.catalog.get("clientID", self.configLocal.getKey.ClientID)
    
    # Property for deviceName
    @property
    def deviceName(self):
        return self.catalog.get("deviceName", self.configLocal.getKey.DeviceName)
     
    # Property for lifeTimeInterval
    @property
    def lifeTimeInterval(self):
        return self.catalog.get("lifeTimeInterval", self.configLocal.getKey.LifeTimeInterval)
    
    # Property for CatalogUpdateIntervalCycles
    @property
    def catalogUpdateIntervalCycles(self):
        return self.catalog.get("catalogUpdateIntervalCycles", self.configLocal.getKey.CatalogUpdateIntervalCycles)
    
    # Property for measureType
    @property
    def measureType(self):
        return self.catalog.get("measureType", [""])
    
    # Property for availableServices
    @property
    def availableServices(self):
        return self.catalog.get("availableServices", [""])
    
    # Properties for MQTT
    @property
    def MQTT(self):
        return self.catalog.get("MQTT", {})
    
    @property
    def mqttTopicSub(self):
        return self.MQTT.get("topicSub", [""])
    
    @property
    def mqttTopicPub(self):
        return self.MQTT.get("topicPub", "")
    
    @property
    def mqttBroker(self):
        return self.MQTT.get("broker", "")
    
    @property
    def mqttPort(self):
        return self.MQTT.get("port", 1883)
    
    # Properties for REST
    @property
    def REST(self):
        return self.catalog.get("REST", {})
    
    @property
    def restServerHost(self):
        return self.REST.get("serverHost", "")
    
    @property
    def restServerPort(self):
        return self.REST.get("serverPort", 8080)
    
    @property
    def restServerConfig(self):
        return self.REST.get("serverConfig", {})
    
    # Property for extra
    @property
    def extra(self):
        return self.catalog.get("extra", {})
    
    # Property for lastUpdate
    @property
    def lastUpdate(self):
        return self.catalog.get("lastUpdate", "")