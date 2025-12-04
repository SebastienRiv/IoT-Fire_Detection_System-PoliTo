from src.Services.Service import Service
from src.libs.MQTT.MyMQTT import MyMQTT
from time import sleep

class MQTTService(Service):
    
    def __init__(self, configFilePath: str) -> None:
        super().__init__(configFilePath)
        
        self.clientMQTT = None
        
        self.mqttSetupClient()
        
    def mqttSetupClient(self) -> None :
        if "MQTT" in self.configCatalog :
            
            if self.clientMQTT is not None :
                self.clientMQTT.stop()
                self.clientMQTT.myOnConnect(self.clientMQTT._paho_mqtt, None, None, 0)
            
            self.clientMQTT = MyMQTT(self.configCatalog["MQTT"].get("ClientID", None),
                                            self.configCatalog["MQTT"].get("Broker", None),
                                            self.configCatalog["MQTT"].get("Port", None),
                                            notifier=self.mqttCallback)
            
            self.mqttStartClient()
            if "TopicSub" in self.configCatalog and self.configCatalog.get("TopicSub", None) is not None :
                self.mqttSubscribe(self.configCatalog.get("TopicSub", None))
        else :
            print("Warning: MQTT configuration not found in device catalog. MQTT functionalities will be disabled.")
            self.clientMQTT = None
        
    def mqttCallback(self, topic, message) -> None :
        pass
    
    def mqttPublish(self, topic, message) -> None :
        if self.clientMQTT is not None :
            if topic is None :
                print("Info: No Topic to publish.")
                return
            self.clientMQTT.myPublish(topic, message)
        else :
            print("Warning: ClientMQTT is not initialized. Cannot publish message.")
            
    def mqttSubscribe(self, topic) -> None :
        if self.clientMQTT is not None :
            if topic is None :
                print("Info: No Topic to subscribe.")
                return
            self.clientMQTT.mySubscribe(topic)
        else :
            print("Warning: ClientMQTT is not initialized. Cannot subscribe.")
            
    def mqttStartClient(self) -> None :
        if self.clientMQTT is not None :
            self.clientMQTT.start()
        else :
            print("Warning: ClientMQTT is not initialized. Cannot start client.")
            
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.serviceRunTimeStatus :
            oldCatalog = self.configCatalog.copy()
            self.updateCatalogConfig()
            
            if oldCatalog.get("MQTT") != self.configCatalog.get("MQTT"):
                print("MQTT configuration has changed. Updating MQTT client...")
                self.mqttSetupClient()
                        
            sleep(self.configCatalog.get("CatalogUpdateIntervalCycles", self.configLocal.get("CatalogUpdateIntervalCycles", updateInterval)))
            
    def serviceRunTime(self) -> None :
        pass
              
    def killServiceRunTime(self) -> None :
        self.serviceRunTimeStatus = False
        if self.clientMQTT is not None :
            self.clientMQTT.stop()