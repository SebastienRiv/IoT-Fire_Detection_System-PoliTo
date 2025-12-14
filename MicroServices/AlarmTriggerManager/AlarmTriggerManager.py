import json
from queue import Queue
import time
import requests
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
        self.requestREST = RequestREST(self.configLocal.getKey.CatalogURL)
        self.configCatalog = CatalogJSON(self.configLocal)
        self.updateCatalogConfig()
        self.clientMQTT = None
        self.queue=Queue()
        self.mqttSetupClient()
    
    def updateCatalogConfig(self) -> bool :
        if self.configLocal.getKey.CatalogURL != "" :
            update = self.requestREST.GET("", params={"clientID": self.configLocal.getKey.ClientID})
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
            if self.configCatalog.get.mqttTopicSub and self.configCatalog.get.mqttTopicSub[0] != "" :
                self.mqttSubscribe(self.configCatalog.get.mqttTopicSub)
        else :
            print("Warning: MQTT configuration not found in device catalog. MQTT functionalities will be disabled.")
            self.clientMQTT = None    
    def mqttCallback(self, topic, message) -> None :
        try:
            data=json.loads(message.decode())
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
        inference=self.requestREST.GET("getInference")
        return inference
    def evaluateAndTrigger(self,inferenceData,clientID):
        if not inferenceData:
            print("Inference data not present")
            return
        fireRisk=inferenceData["fireRisk"]
        if fireRisk>=self.configLocal.getKey.Threshold:
            data=self.sensML.genSensMLActuatorMsg("AlarmTriggerManager",True,time.time())
            if self.clientMQTT.isConnect():
                json_payload=json.dumps(data)
                params={"clientID":clientID}
                deviceInfo=self.requestREST.GET("getBuildingInformation",params)
                self.configCatalog.setFireStatus(clientID)
                self.clientMQTT.myPublish(f"/IOT-project/{deviceInfo['buildingID']}/{deviceInfo['floorID']}/{deviceInfo['roomID']}/{clientID}",json_payload)
                
            else:
                print("MQTT doesn't work")
        else:
            print(f"Risk of fire with fire risk {fireRisk}")
    def setRunTimeStatus(self, status:bool) -> None :
        self.RunTimeStatus = status
    def RunTime(self)->None:
        try:
            while self.RunTimeStatus:
                if not self.queue.empty():
                    data=self.queue.get()
                    self.postData(data["e"])
                    inference=self.getInference()
                    self.evaluateAndTrigger(inference,data["bn"])
                sleep(self.configCatalog.get.lifeTimeInterval())
        except KeyboardInterrupt:
            print("Terminated code")
            self.RunTimeStatus=False
        finally:
            self.clientMQTT.stop()
    def killRunTime(self) -> None:
        self.RunTimeStatus=False