import json
import requests
from queue import Queue
from src.Services.Hybrid.RESTandMQTTService import RESTandMQTTService
from src.libs.SensML.SensML import SensML
from time import sleep
class AlarmTriggerManager(RESTandMQTTService):
    def __init__(self,configFile:str):
        super().__init__(configFile)
        self.sensML = SensML()
        self.queue=Queue()
    
    def updateCatalogConfig(self) -> bool :
        if self.configLocal.getKey.CatalogURL != "" :
            update = self.requestREST.GET("", params={"clientID": self.configLocal.getKey.ClientID})
            modified = self.configCatalog.updateCatalog(update)
            return modified
        return False
  
    def mqttCallback(self, topic, message) -> None :
        try:
            data=json.loads(message.decode())
            self.queue.put(data)
            print(f"Received from {topic}: {data}")
        except:
            print("Warning")
    
    def GET(self,*uri,**params):
        if len(uri)>0:
            clientID=uri[0]
            buildingID=self.configCatalog.get.buildingID(clientID)
            buildingName=self.configCatalog.get.buildingName(buildingID)
            address=self.configCatalog.get.address(buildingID)
            lat=self.configCatalog.get.lat(buildingID)
            longit=self.configCatalog.get.longit(buildingID)
            floorID=self.configCatalog.get.floorID(clientID)
            roomID=self.configCatalog.get.roomID(clientID)
            fireFighterChatID=self.configCatalog.get.fireFighterChatID(buildingID)
            userChatIDList=self.configCatalog.get.userChatIDList(buildingID)
            device={
                "buildingID":buildingID,
                "buildingName":buildingName,
                "address":address,
                "lat":lat,
                "longit":longit,
                "floorID":floorID,
                "roomID":roomID,
                "fireFighterChatID":fireFighterChatID,
                "userChatIDList":userChatIDList
            }
            return json.dumps(device)
    def postData(self,data):#to implement
        self.requestREST.POST(url,data)#data is sent to the inference service
    def getInference(self):
        inference=self.requestREST.GET("getInference")
        return inference
    def buildTelegramMessage(buildingID,buildingName,address,lat,longit,floorID,roomID,fireFighterChatID,userChatIDList)->dict:
        msg={
            "build" : {
                "buildingID": buildingID,
                "buildingName":buildingName,
                "address": address,
                "GPS":{
                    "lat": lat,
                    "long": longit
                },
                "floorID": floorID,
                "roomID":roomID
            },
            "fireFighterChatID": fireFighterChatID,
            "userChatIDList": userChatIDList
        } 
        return msg

    def evaluateAndTrigger(self,inferenceData,clientID):
        if not inferenceData:
            print("Inference data not present")
            return
        fireRisk=inferenceData["fireRisk"]
        if fireRisk>=self.configLocal.getKey.Threshold:
            if self.clientMQTT.isConnect():
                params={"clientID":clientID}
                deviceInfo=self.requestREST.GET("getBuildingInformation",params)
                msg=self.buildTelegramMessage(deviceInfo['buildingID'],deviceInfo['buildingName'],deviceInfo["address"],deviceInfo['lat'],deviceInfo['longit'],deviceInfo['floorID'],deviceInfo['roomID'],deviceInfo['fireFighterChatID'],deviceInfo['userChatIDList'])
                json_payload=json.dumps(msg)
                self.configCatalog.setFireStatus(clientID)
                self.clientMQTT.myPublish(f"/IOT-project/{deviceInfo['buildingID']}/{deviceInfo['floorID']}/{deviceInfo['roomID']}/{clientID}",json_payload)
            else:
                print("MQTT doesn't work")
        else:
            print(f"Risk of fire with fire risk {fireRisk}")
    def setRunTimeStatus(self, status:bool) -> None :
        self.RunTimeStatus = status
    def serviceRunTime(self)->None:
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
            self.killServiceRunTime()