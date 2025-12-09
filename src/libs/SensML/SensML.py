from src.libs.SensML.KeyBinds.SensMLKeyBinds import SensMLKeyBinds
import json
import datetime

class SensML :
    
    def __init__(self) :
        
        self.deviceTemplate = {}
        self.sensorTemplate = {}
        self.actuatorTemplate = {}
        
        self.sensMLReading = SensMLKeyBinds({})
        
    def loadTemplates(self) -> None:
        
        try :
            with open("./src/libs/SensML/Templates/SensMLDeviceTemplate.json", "r") as deviceFile :
                self.deviceTemplate = json.load(deviceFile)
        except FileNotFoundError :
            print("Error: deviceTemplate.json file not found.")
            self.deviceTemplate = {}
        
        try :
            with open("./src/libs/SensML/Templates/SensMLSensorTemplate.json", "r") as sensorFile :
                self.sensorTemplate = json.load(sensorFile)
        except FileNotFoundError :
            print("Error: sensorTemplate.json file not found.")
            self.sensorTemplate = {}
            
        try : 
            with open("./src/libs/SensML/Templates/SensMLActuatorTemplate.json", "r") as actuatorFile :
                self.actuatorTemplate = json.load(actuatorFile)
        except FileNotFoundError :
            print("Error: actuatorTemplate.json file not found.")
            self.actuatorTemplate = {}
            
    def getIn(self, SensMLReading) -> SensMLKeyBinds:
        self.sensMLReading.updateSensMLReading(SensMLReading)
        return self.sensMLReading
            
    def getDeviceTemplate(self) :
        return self.deviceTemplate.copy()
    
    def getSensorTemplate(self) :
        return self.sensorTemplate.copy()
    
    def getActuatorTemplate(self) :
        return self.actuatorTemplate.copy()
    
    def genSensMLDeviceMsg(self, bn, e, t=None) -> dict :
        gen = self.getDeviceTemplate()
        gen["bn"] = bn
        gen["e"] = e
        gen["t"] = int(datetime.datetime.now().timestamp()) if t is None else t
        return gen
    
    def genSensMLSensorMsg(self, n, u, v, t) -> dict :
        gen = self.getSensorTemplate()
        gen["n"] = n
        gen["u"] = u
        gen["v"] = v
        gen["t"] = t
        return gen
    
    def genSensMLActuatorMsg(self, n, v, t, u="bool", a=True) -> dict :
        gen = self.getActuatorTemplate()
        gen["n"] = n
        gen["u"] = u
        gen["v"] = v
        gen["t"] = t
        gen["a"] = a
        return gen