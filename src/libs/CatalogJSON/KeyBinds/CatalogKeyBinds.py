class CatalogKeyBinds:
    
    def __init__(self, catalog, configLocal) -> None:
        self.catalog = catalog
        self.configLocal = configLocal
    
    # Propriété pour clientID
    @property 
    def clientID(self):
        return self.catalog.get("clientID", self.configLocal.getKey.ClientID)
    
    # Propriété pour deviceName
    @property
    def deviceName(self):
        return self.catalog.get("deviceName", self.configLocal.getKey.DeviceName)
     
    # Propriété pour lifeTimeInterval
    @property
    def lifeTimeInterval(self):
        return self.catalog.get("lifeTimeInterval", self.configLocal.getKey.LifeTimeInterval)
    
    # Propriété pour CatalogUpdateIntervalCycles
    @property
    def catalogUpdateIntervalCycles(self):
        return self.catalog.get("catalogUpdateIntervalCycles", self.configLocal.getKey.CatalogUpdateIntervalCycles)
    
    # Propriété pour measureType
    @property
    def measureType(self):
        return self.catalog.get("measureType", [""])
    
    # Propriété pour availableServices
    @property
    def availableServices(self):
        return self.catalog.get("availableServices", [""])
    
    # Propriétés pour MQTT
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
    
    # Propriétés pour REST
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
    
    # Propriété pour extra
    @property
    def extra(self):
        return self.catalog.get("extra", {})
    
    # Propriété pour lastUpdate
    @property
    def lastUpdate(self):
        return self.catalog.get("lastUpdate", "")