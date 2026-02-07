import json
import requests
from src.libs.REST.RequestREST import RequestREST
from queue import Queue
from src.Services.MQTT.MQTTService import MQTTService
from src.libs.SensML.SensML import SensML
from time import sleep
from math import radians, sin, cos, sqrt, atan2

def haversine(latBuilding, longitBuilding, latFireFighter, longitFireFighter):
    R=6371
    latBuilding, longitBuilding, latFireFighter, longitFireFighter = map(radians, [latBuilding, longitBuilding, latFireFighter, longitFireFighter])
    dlat = latFireFighter - latBuilding
    dlongit = longitFireFighter - longitBuilding
    a = sin(dlat / 2)**2 + cos(latBuilding) * cos(latFireFighter) * sin(dlongit / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R*c

class AlarmTriggerManager(MQTTService):
    def __init__(self, configFile:str):
        super().__init__(configFile)
        
        self.sensML = SensML()
        self.queue = Queue()
        
        self.inferenceURL = self.configLocal.getKey.Extra.get("InferenceServiceURL", "")
        self.requestRESTInference = RequestREST(self.inferenceURL)
        
        if not self.inferenceURL:
            print("Warning: InferenceServiceURL not found in config")
  
    def mqttCallback(self, topic, message) -> None :
        try:
            data = dict(message)
            self.queue.put(data)
            print(f"Received from {topic}: {data}")
        except json.JSONDecodeError:
            print("Warning: Failed to decode MQTT message due to invalid JSON")
        except Exception as e:
            print(f"Warning: Error in mqttCallback: {e}")
    
    def postData(self, data):
        if not self.inferenceURL:
            print("Error: Inference URL not configured")
            return None
        try:
            inference_data = self.requestRESTInference.POST("fireDetection", data=data)
            return inference_data
        except requests.exceptions.RequestException as e:
            print(f"Connection error to Inference Service: {e}")
            return None
    
    def buildTelegramMessage(self, buildingID, buildingName, address, lat, longit, floorID, roomID, fireFighterChatID, userChatIDList) -> dict:
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

    def evaluateAndTrigger(self, inferenceData, clientID):
        if not inferenceData:
            print("Inference data not present")
            return
        
        fireProb = inferenceData.get("fire_probability", 0)
        isFire = inferenceData.get("is_fire", False)
        alertLevel = inferenceData.get("alert_level", "NORMAL")
        
        threshold = self.configLocal.getKey.Extra.get("threshold", 0.5)
        
        print(f"Fire Probability: {fireProb:.2f}, Alert Level: {alertLevel}")
        
        if isFire or fireProb >= threshold:
            print(f"ALARM! Fire Probability: {fireProb:.2f} (threshold: {threshold})")
            
            if self.clientMQTT is not None:
                deviceInfo = self.requestREST.GET("getResourceByID", params={"clientID": clientID})
                
                if deviceInfo and "status" in deviceInfo and deviceInfo["status"] == "success":
                    device = deviceInfo.get("data", {})
                    
                    buildingID = device.get("building", {}).get("id", "")
                    buildingFloor = device.get("building", {}).get("floor", "")
                    buildingRoom = device.get("building", {}).get("room", "")
                    
                    baseTopic = self.configCatalog.get.MQTT.topicPub[0].rstrip("/fireAlarm")
                    topic = f"{baseTopic}/{buildingID}/{buildingFloor}/{buildingRoom}/{clientID}/alarm"
                    
                    alarmMessage = {
                        "alarmStatus": True,
                        "fire_probability": fireProb,
                        "alert_level": alertLevel,
                        "anomaly_score": inferenceData.get("anomaly_score", 0),
                        "clientID": clientID,
                        "buildingID": buildingID,
                        "floor": buildingFloor,
                        "room": buildingRoom
                    }
                    
                    self.clientMQTT.myPublish(topic, alarmMessage)
                    print(f"Alarm published to {topic}")
                    print(f"   Message: {alarmMessage}")
                else:
                    print(f"Could not retrieve device information for clientID: {clientID}")
            else:
                print("MQTT Client not connected")
        else:
            print(f"Status Normal. Fire probability: {fireProb:.2f}")

    def serviceRunTime(self) -> None:
        self.serviceRunTimeStatus = True
        self.updateLoopStart()
        
        while self.serviceRunTimeStatus:
            if not self.queue.empty():
                while not self.queue.empty():
                    data = self.queue.get()
                    
                    if "e" in data and "bn" in data:
                        clientID = data["bn"]
                        sensors = data["e"]
                        
                        inferenceInput = {}
                        for sensor in sensors:
                            sensorName = sensor.get("n", "").lower()
                            sensorValue = sensor.get("v", 0)
                            
                            if "smoke" in sensorName:
                                inferenceInput["smoke"] = sensorValue
                            elif "co" in sensorName:
                                inferenceInput["co"] = sensorValue
                            elif "tvoc" in sensorName:
                                inferenceInput["tvoc"] = sensorValue
                            elif "temp" in sensorName:
                                inferenceInput["temperature"] = sensorValue
                        
                        print(f"Sending to inference: {inferenceInput}")
                        inference = self.postData(inferenceInput)
                        
                        if inference:
                            self.evaluateAndTrigger(inference, clientID)
                    else:
                        print(f"Invalid data format in queue: {data}")
            
            sleep(self.configCatalog.get.lifeTimeInterval if self.configCatalog.get.lifeTimeInterval else int(self.configLocal.getKey.LifeTimeInterval))
            
    def killServiceRunTime(self) -> None :
        return super().killServiceRunTime()