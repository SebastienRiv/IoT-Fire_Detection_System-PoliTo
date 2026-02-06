import json
import requests
from queue import Queue
from src.Services.Hybrid.RESTandMQTTService import RESTandMQTTService
from src.libs.SensML.SensML import SensML
from time import sleep
class AlarmTriggerManager(RESTandMQTTService):
    def __init__(self, configFile:str):
        super().__init__(configFile)
        self.sensML = SensML()
        self.queue = Queue()
        self.inferenceURL = self.configLocal.get("InferenceServiceURL")
        if not self.inferenceURL:
            print("Warning: InferenceServiceURL not found in config")
    
    def updateCatalogConfig(self) -> bool :
        catalogURL = self.configLocal.get("CatalogURL")
        clientID = self.configLocal.get("ClientID")
        if catalogURL:
            try:
                response = requests.get(catalogURL,params={"clientID":clientID})
                if response.status_code == 200:
                    modified = self.configCatalog.updateCatalog(response.json())
                    return modified
            except Exception as e:
                print(f"Error updating catalog: {e}")
        return False
  
    def mqttCallback(self, topic, message) -> None :
        try:
            data = json.loads(message.decode())
            self.queue.put(data)
            print(f"Received from {topic}: {data}")
        except json.JSONDecodeError:
            print("Warning: Failed to decode MQTT message due to invalid JSON")
        except Exception as e:
            print(f"Warning: Error in mqttCallback: {e}")
    
    def GET(self, *uri, **params):
        try:
            if len(uri)>0:
                endpoint = uri[0]
                if endpoint == "ping":
                    return json.dumps({
                        "service": "AlarmTriggerManager",
                        "status": "running",
                        "queue_size": self.queue.qsize()
                    })
                elif endpoint == "getBuildingInformation":
                    clientID = params.get("clientID")
                    if clientID is None:
                        return json.dumps({"Error":"Missing clientID"})
                    try:
                        buildingID = self.configCatalog.get.buildingID(clientID)
                        device={
                            "buildingID": buildingID,
                            "buildingName": self.configCatalog.get.buildingName(buildingID),
                            "address": self.configCatalog.get.address(buildingID),
                            "lat": self.configCatalog.get.lat(buildingID),
                            "longit": self.configCatalog.get.longit(buildingID),
                            "floorID": self.configCatalog.get.floorID(clientID),
                            "roomID": self.configCatalog.get.roomID(clientID),
                            "fireFighterChatID": self.configCatalog.get.fireFighterChatID(buildingID),
                            "userChatIDList": self.configCatalog.get.userChatIDList(buildingID)
                        }
                        return json.dumps(device)
                    except Exception:
                        return json.dumps({"Error":"Device not found or Catalog Error"})
                return json.dumps({"Error":"Invalid endpoint"})
        except Exception as e:
            return json.dumps({"Error":f"Internal Server Error {e}"})
    def POST(self, *uri, **params) -> None:
        return None
    def PUT(self, *uri, **params) -> None:
        return None
    def DELETE(self, *uri, **params) -> None:
        return None
    def postData(self, data):
        if not self.inferenceURL:
            print("Error: Inference URL not configured")
            return None
        try:
            response = requests.post(self.inferenceURL,json=data)
            if response.status_code == 200:
                inference_data = response.json()
                return inference_data
            else:
                print("Error from Inference Service: ",response.status_code)
                return None
        except requests.exceptions.RequestException:
            print("Connection error to Inference Service")
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
        fireRisk = inferenceData.get("fireRisk")
        threshold = self.configLocal.get("threshold")
        if fireRisk >= threshold:
            print(f"ALARM! Fire Risk: {fireRisk} exceeds threshold {threshold}")
            if self.clientMQTT is not None and self.clientMQTT.isConnect():
                deviceInfoJson = self.GET("getBuildingInformation",clientID=clientID)
                deviceInfo = json.loads(deviceInfoJson)
                if "Error" not in deviceInfo:
                    msg = self.buildTelegramMessage(deviceInfo['buildingID'], deviceInfo['buildingName'], deviceInfo["address"], deviceInfo['lat'], deviceInfo['longit'], deviceInfo['floorID'], deviceInfo['roomID'], deviceInfo['fireFighterChatID'], deviceInfo['userChatIDList'])
                    json_payload = json.dumps(msg)
                    topic = f"/IOT-project/{deviceInfo['buildingID']}/{deviceInfo['floorID']}/{deviceInfo['roomID']}/{clientID}"
                    self.configCatalog.setFireStatus(clientID)
                    self.clientMQTT.myPublish(topic,json_payload)
                    print(f"Alarm published to {topic}")
                else:
                    print("Could not retrieve building information for the alarm")
            else:
                print("MQTT Client not connected")
        else:
            print(f"Status Normal. Fire risk: {fireRisk}")
    def setRunTimeStatus(self, status:bool) -> None :
        self.serviceRunTimeStatus = status
    def serviceRunTime(self) -> None:
        try:
            while self.serviceRunTimeStatus:
                if not self.queue.empty():
                    data = self.queue.get()
                    if "e" in data and "bn" in data:
                        inference = self.postData(data["e"])
                        self.evaluateAndTrigger(inference,data["bn"])
                    else:
                        print("Invalid data format in the queue")
                sleep(self.configCatalog.get.lifeTimeInterval())
        except KeyboardInterrupt:
            print("Terminated code")
            self.serviceRunTimeStatus = False
        finally:
            self.killServiceRunTime()