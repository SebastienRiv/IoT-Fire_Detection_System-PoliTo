import yaml
import requests
from time import sleep
from src.libs.MQTT.MyMQTT import MyMQTT
from src.libs.REST.RequestREST import RequestREST
import threading

class Device :
    
    def __init__(self, configFile:str, sensorsArray:list) -> None :
        self.configFile = configFile
        self.sensorsArray = sensorsArray
        self.deviceRunTimeStatus = False
        self.globalEventTriggered = False
        
        # Load local configuration from file
        self.configLocal = {}
        self.updateLocalConfig()
        
        self.requestREST = RequestREST(self.configLocal.get("DeviceCatalogURL", ""))
        
        # Fetch device catalog from URL if provided
        self.configCatalog = {}
        self.updateCatalogConfig()
        
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
    
    def triggerGlobalEvent(self) -> None :
        self.globalEventTriggered = True
        
    def getDeviceID(self) -> str :
        deviceID = self.configLocal.get("DeviceID", None)
        if deviceID is not None :
            return deviceID
        else :
            print("Warning: DeviceID not found in local configuration.")
            return "UnknownID"
    
    def getConfigFile(self) -> str :
        return self.configFile
    
    def getDeviceType(self) -> str :
        deviceType = self.configLocal.get("DeviceType", None)
        if deviceType is not None :
            return deviceType
        else :
            print("Warning: DeviceType not found in local configuration.")
            return "UnknownType"
    
    def getSensorsArray(self) -> list :
        return self.sensorsArray
    
    def getDeviceRunTimeStatus(self) -> bool :
        return self.deviceRunTimeStatus
    
    def getConfigLocal(self) -> dict :
        return self.configLocal
    
    def getSensorsValues(self) -> dict :
        return {
            "bn" : self.getDeviceID(),
            "e" : [ sensor.getValue() for sensor in self.sensorsArray ]
        }
    
    def setDeviceRunTimeStatus(self, status:bool) -> None :
        self.deviceRunTimeStatus = status
        
    def updateLocalConfig(self) -> None :
        try : 
            with open(self.configFile, 'r') as file:
                self.configLocal = yaml.safe_load(file)
        except Exception as e :
            print(f"Error loading config file: {e}")
            
    def updateCatalogConfig(self) -> None :
        if "DeviceCatalogURL" in self.configLocal:
            self.configCatalog = self.requestREST.GET("", params={"device_id": self.configLocal.get("DeviceID", "")})
    
    def updateSensorsValues(self) -> None :
        for sensor in self.sensorsArray :
            sensor.updateValue(context={"globalEvent": self.globalEventTriggered})
    
    def updateLoopStart(self, updateInterval:int=12) -> None :
        if not hasattr(self, 'updateThread') or not self.updateThread.is_alive():
            self.updateThread = threading.Thread(target=self.updateLoopRunTime, args=(updateInterval,), daemon=True)
            self.updateThread.start()
           
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.deviceRunTimeStatus :
            oldCatalog = self.configCatalog.copy()
            self.updateCatalogConfig()
            if oldCatalog.get("MQTT") != self.configCatalog.get("MQTT"):
                print("MQTT configuration has changed. Updating MQTT client...")
                self.mqttSetupClient()
            
            sleep(self.configCatalog.get("CatalogUpdateIntervalCycles", self.configLocal.get("CatalogUpdateIntervalCycles", updateInterval)))
    
    def killDeviceRunTime(self) -> None :
        self.deviceRunTimeStatus = False
    
    def deviceRunTime(self) -> None :
        pass