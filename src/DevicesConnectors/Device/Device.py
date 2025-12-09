from abc import ABC, abstractmethod
import yaml
import requests
from time import sleep
from src.libs.MQTT.MyMQTT import MyMQTT
from src.libs.REST.RequestREST import RequestREST
from src.libs.SensML.SensML import SensML
from src.libs.CatalogJSON.CatalogJSON import CatalogJSON
from src.libs.ConfigYAML.ConfigYAML import ConfigYAML
import threading

class Device(ABC):
    
    def __init__(self, configFile:str, sensorsArray:list) -> None :
        self.sensML = SensML()
        
        self.configFile = configFile
        self.sensorsArray = sensorsArray
        self.deviceRunTimeStatus = False
        self.globalEventTriggered = False
        
        # Load local configuration from file
        self.configLocal = ConfigYAML(self.configFile)
        
        self.requestREST = RequestREST(self.configLocal.getKey.CatalogURL)
        
        # Fetch device catalog from URL if provided
        self.configCatalog = CatalogJSON(self.configLocal)
        self.updateCatalogConfig()
        
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
            if self.configCatalog.get.mqttTopicSub[0] != "" and self.configCatalog.get.mqttTopicSub is not None:
                self.mqttSubscribe(self.configCatalog.get.mqttTopicSub)
        else :
            print("Warning: MQTT configuration not found in device catalog. MQTT functionalities will be disabled.")
            self.clientMQTT = None
    
    @abstractmethod
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
        deviceID = self.configLocal.getKey.ClientID
        if deviceID is not None :
            return deviceID
        else :
            print("Warning: DeviceID not found in local configuration.")
            return "UnknownID"
    
    def getConfigFile(self) -> str :
        return self.configFile
    
    def getDeviceName(self) -> str :
        deviceName = self.configLocal.getKey.ClientName
        if deviceName is not None :
            return deviceName
        else :
            print("Warning: DeviceName not found in local configuration.")
            return "UnknownName"
    
    def getSensorsArray(self) -> list :
        return self.sensorsArray
    
    def getDeviceRunTimeStatus(self) -> bool :
        return self.deviceRunTimeStatus
    
    def getConfigLocal(self) -> dict :
        return self.configLocal.getConfig()
    
    def getSensorsValues(self) -> dict :
        msg = self.sensML.genSensMLDeviceMsg(self.getDeviceID(), [ sensor.getValue() for sensor in self.sensorsArray ])
        return msg
            
    def setDeviceRunTimeStatus(self, status:bool) -> None :
        self.deviceRunTimeStatus = status
            
    def updateCatalogConfig(self) -> bool :
        if self.configLocal.getKey.CatalogURL != "" :
            update = self.requestREST.GET("", params={"device_id": self.configLocal.getKey.ClientID})
            modified = self.configCatalog.updateCatalog(update)
            return modified
        return False
    
    def updateSensorsValues(self) -> None :
        for sensor in self.sensorsArray :
            sensor.updateValue(context={"globalEvent": self.globalEventTriggered})
    
    def updateLoopStart(self, updateInterval:int=12) -> None :
        if not hasattr(self, 'updateThread') or not self.updateThread.is_alive():
            self.updateThread = threading.Thread(target=self.updateLoopRunTime, args=(updateInterval,), daemon=True)
            self.updateThread.start()
           
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.deviceRunTimeStatus :
            modified = self.updateCatalogConfig()

            if modified :
                print(modified)
                print("MQTT configuration has changed. Updating MQTT client...")
                self.mqttSetupClient()
            
            sleep(self.configCatalog.get.catalogUpdateIntervalCycles)
    
    @abstractmethod
    def killDeviceRunTime(self) -> None :
        self.deviceRunTimeStatus = False
    
    @abstractmethod
    def deviceRunTime(self) -> None :
        pass