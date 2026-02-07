from src.DevicesConnectors.Device.Device import Device
from playsound import playsound
import threading
from time import sleep
import threading
import json

class FireDetectorDevice(Device) :
    
    def __init__(self, configFile:str, sensorsArray:list) -> None :
        super().__init__(configFile, sensorsArray)
        
        self.alarmStatus = False
        self.alarmThread = None
        
        if "AlarmSoundFilePath" in self.configLocal.getConfig() :
            self.alarmSoundFilePath = self.configLocal.getKey.Extra.get("AlarmSoundFilePath", None)
        else :
            self.alarmSoundFilePath = None
            print("Warning: AlarmSoundFilePath not found in local configuration. Alarm sound will be disabled.")
        
    def mqttCallback(self, topic, message) -> None :
        if topic in self.configCatalog.get.mqttTopicSub :
            if "alarmStatus" in message:
                self.setAlarmStatus(message["alarmStatus"])
        
    def getAlarmStatus(self) -> bool :
        return self.alarmStatus
    
    def setAlarmStatus(self, status:bool) -> None :
        self.alarmStatus = status
        if status and self.alarmSoundFilePath is not None and (self.alarmThread is None or not self.alarmThread.is_alive()):
            self.alarmThread = threading.Thread(target=self.playAlarmLoop, daemon=True)
            self.alarmThread.start()

    def playAlarmLoop(self) -> None :
        while self.alarmStatus :
            playsound(self.alarmSoundFilePath)
            sleep(self.configCatalog.get.extra.get("SoundLoopDelay", self.configLocal.getKey.Extra.get("SoundLoopDelay", 0.1)))
    
    def updateMQTTClients(self) -> None :
        print("Updating MQTT clients with new configuration...")
        if self.clientMQTT is not None :
            self.clientMQTT.stop()
        self.mqttSetupClient()
            
    def deviceRunTime(self) -> None :
        super().updateLoopStart(20)
        
        while self.deviceRunTimeStatus :
            super().updateSensorsValues()
            
            values = super().getSensorsValues()
            super().mqttPublish(self.configCatalog.get.mqttTopicPub[0], values)
                    
            sleep(self.configCatalog.get.lifeTimeInterval)
            
    def killDeviceRunTime(self) -> None:
        super().killDeviceRunTime()
        self.setAlarmStatus(False)
        