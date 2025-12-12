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
        self.RunTimeStatus=False
        self.configLocal = ConfigYAML(self.configFile)
        self.configCatalog = CatalogJSON(self.configLocal)
        self.updateCatalogConfig()
        self.requestREST = RequestREST(self.configLocal.getKey.CatalogURL)
        self.clientMQTT = None
        self.queue=Queue()
        self.mqttSetupClient()
    
    def updateCatalogConfig(self) -> bool :
        if self.configLocal.getKey.CatalogURL != "" :
            update = self.requestREST.GET("", params={"device_id": self.configLocal.getKey.ClientID})
            modified = self.configCatalog.updateCatalog(update)
            return modified
        return False
    
    def mqttSetupClient(self) -> None :
        if self.configCatalog.get.mqttBroker != "" :
            if self.clientMQTT is not None :
                self.clientMQTT.stop()
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
        try:
            data=message.decode()
            self.queue.put(data)
            print(f"Received from {topic}: {data}")
        except:
            print("Warning")
    
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
    
    def postData(self,data):
        self.requestREST.POST(data)#data is sent to the inference service
    def getInference(self):
        return self.requestREST.GET()#data is retrieve from the inference service
    def evaluateAndTrigger(self,inference_data):
        if not inference_data or 'fire_risk' not in inference_data:#payload: {"deviceName":"...","fire_risk":"...",""}
            print("Inference data not present or not valid")
            return
        fire_risk=inference_data.get('fire_risk')
        if fire_risk>=self.configLocal.getKey.Threshold:
            payload={
                "condition":"CRITICAL",
                "fire_risk":f"Fire_risk of {fire_risk} exceeds the threshold {self.configLocal.getKey.Threshold}",
                "deviceName":inference_data["deviceName"],
                "time":time.time()
            }
            if self.clientMQTT.isConnect():
                json_payload=json.dumps(payload)
                self.clientMQTT.myPublish(self.configCatalog.get.mqttTopicPub,json_payload)
            else:
                print("MQTT doesn't work")
        else:
            print(f"Risk of fire with fire risk {fire_risk}")
    def setRunTimeStatus(self, status:bool) -> None :
        self.RunTimeStatus = status
    def RunTime(self)->None:
        try:
            while self.RunTimeStatus:
                if not self.queue.empty():
                    data=self.queue.get()
                    self.postData(data)
                inference=self.getInference()
                self.evaluateAndTrigger(inference)
                sleep(self.configCatalog.get.lifeTimeInterval)
        except KeyboardInterrupt:
            print("Terminated code")
            self.RunTimeStatus=False
        finally:
            self.clientMQTT.stop()
    def killRunTime(self) -> None:
        self.RunTimeStatus=False