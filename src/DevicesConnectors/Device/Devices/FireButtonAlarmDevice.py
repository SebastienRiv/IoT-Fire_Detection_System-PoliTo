from src.DevicesConnectors.Device.Device import Device
import json
from time import sleep

class FireButtonAlarmDevice(Device) :
    
    def __init__(self, configFile:str, sensorsArray:list) -> None :
        super().__init__(configFile, sensorsArray)
        
    def mqttCallback(self, topic, message) -> None:
        pass
    
    def deviceRunTime(self) -> None :
        super().updateLoopStart(20)
        
        while self.deviceRunTimeStatus :
            super().updateSensorsValues()
            
            values = super().getSensorsValues()
            super().mqttPublish(self.configCatalog.get.mqttTopicPub, json.dumps(values))
            
            sleep(self.configCatalog.get.lifeTimeInterval)
            
    def killDeviceRunTime(self) -> None:
        super().killDeviceRunTime()