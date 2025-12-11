import json
from queue import Queue
import time
from src.libs.MQTT.MyMQTT import MyMQTT
from src.libs.REST.RequestREST import RequestREST
from src.libs.SensML.SensML import SensML
from src.libs.CatalogJSON.CatalogJSON import CatalogJSON
from src.libs.ConfigYAML.ConfigYAML import ConfigYAML
from time import sleep
class AlarmTriggerManager:
    def __init__(self,configFile:str):
        self.sensML = SensML()
        self.configFile = configFile
        self.configLocal = ConfigYAML(self.configFile)
        self.configCatalog = CatalogJSON(self.configLocal)
        self.updateCatalogConfig()
        self.requestREST = RequestREST(self.configLocal.getKey.CatalogURL)
        self.clientMQTT = None
        self.queue=Queue()
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
            if self.configCatalog.get.mqttTopicSub[0] != "" and self.configCatalog.get.mqttTopicSub is not None:
                self.mqttSubscribe(self.configCatalog.get.mqttTopicSub)
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
    
    def onMessage(self,client,userdata,msg):
        data=msg.payload.decode()
        self.queue.put(data)
            
    def mqttStartClient(self) -> None :
        if self.clientMQTT is not None :
            self.clientMQTT.start()
        else :
            print("Warning: ClientMQTT is not initialized. Cannot start client.")
    
    def postData(self,data):
        RequestREST.POST(self,data)
    def getInference(self):
        inferenceData=RequestREST.GET()
        return inferenceData
    def evaluateAndTrigger(self,inference_data):
        if not inference_data or 'fire_risk' not in inference_data:
            print("Inference data not present or not valid")
            return
        fire_risk=inference_data.get('fire_risk')
        if fire_risk>=self.configLocal.getKey.Threshold:
            payload={
                "condition":"CRITICAL",
                "fire_risk":f"Fire_risk of {fire_risk} exceeds the threshold {self.configLocal.getKey.Threshold}",
                "details":inference_data,
                "time":time.time()
            }
            if self.clientMQTT.isConnect():
                self.clientMQTT.myPublish(self.configCatalog.get.mqttBroker,payload)
            else:
                print("MQTT doesn't work")
        else:
            print(f"Risk of fire with fire risk {fire_risk}")
    
    def run(self):
        self.MQTT_client.start()
        try:
            while True:
                if not self.queue.not_empty():
                    self.postData(self.queue.get())
                inference=self.getInference()
                self.evaluateAndTrigger(inference)
                sleep(self.configCatalog.get.lifeTimeInterval)
        except KeyboardInterrupt:
            print("Terminated code")
        finally:
            self.MQTT_client.stop()
