from src.Services.Service import Service
from src.libs.MQTT.MyMQTT import MyMQTT
from time import sleep

class MQTTService(Service):
    
    def __init__(self, configFilePath: str) -> None:
        super().__init__(configFilePath)
        
        self.clientMQTT = None
        self.mqttSetupClient()
        
    def mqttSetupClient(self) -> None :
        if self.configCatalog.get.mqttBroker != "" :
            
            if self.clientMQTT is not None :
                self.clientMQTT.stop()
                self.clientMQTT.myOnConnect(self.clientMQTT._paho_mqtt, None, None, 0)
            
            self.clientMQTT = MyMQTT(self.configCatalog.get.clientID,
                                            self.configCatalog.get.mqttBroker,
                                            self.configCatalog.get.mqttPort,
                                            notifier=self.mqttCallback)
            
            self.mqttStartClient()
            if self.configCatalog.get.mqttTopicSub[0] != "" and self.configCatalog.get.mqttTopicSub is not None :
                for topic in self.configCatalog.get.mqttTopicSub:
                    self.clientMQTT.mySubscribe(topic)
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
            modfied = self.updateCatalogConfig()
            
            if modfied :
                print("MQTT configuration has changed. Updating MQTT client...")
                self.mqttSetupClient()
                        
            sleep(self.configCatalog.get.catalogUpdateIntervalCycles)
            
    def serviceRunTime(self) -> None :
        pass
              
    def killServiceRunTime(self) -> None :
        self.serviceRunTimeStatus = False
        if self.clientMQTT is not None :
            self.clientMQTT.stop()