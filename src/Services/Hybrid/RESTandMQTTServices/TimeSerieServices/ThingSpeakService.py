from src.Services.Hybrid.RESTandMQTTServices.TimeSerieService import TimeSerieService
from src.libs.SensML.SensML import SensML
import json
import cherrypy

import random
import time

class ThingspeakService(TimeSerieService):
    
    def __init__(self, configFilePath:str, envFilePath:str) -> None :
        super().__init__(configFilePath, envFilePath)
        
        self.sensML = SensML()
        
        self.channelWriteAPIkey = None
        self.channelReadAPIkey = None
        
        self.envLoadConfig()
        
    def envLoadConfig(self) -> None :
        with open(self.envFilePath, 'r') as envFile:
            for line in envFile:
                key, value = line.strip().split('=', 1)
                if key == "USERAPIKEY":
                    self.userApiKey = value
                elif key == "CHANNELWRITEAPIKEY":
                    self.channelWriteAPIkey = value
                elif key == "CHANNELREADAPIKEY":
                    self.channelReadAPIkey = value
        
    def uploadThingspeak(self, fieldNumber, fieldValue):
        ressource = "update"
        params = {
            "api_key": self.channelWriteAPIkey,
            f"field{fieldNumber}": fieldValue
        }
        r = self.requestRESTTimeSeries.GET(ressource, params)
    
    def uploadThingspeakMultiple(self, fieldsData):
        ressource = "update"
        params = {"api_key": self.channelWriteAPIkey}
        for fieldNumber, fieldValue in fieldsData.items():
            params[f"field{fieldNumber}"] = fieldValue
        r = self.requestRESTTimeSeries.GET(ressource, params)
        return r
        
    def readThingspeak(self, results=100):
        channelId = self.configCatalog.get.extra.get("channelId", self.configLocal.get("ChannelId", None))
        ressource = f"channels/{channelId}/feeds.json"
        params = {
            "api_key": self.channelReadAPIkey,
            "results": results
        }
        r = self.requestRESTTimeSeries.GET(ressource, params)
        return r
    
    def formatThingspeakData(self, rawData, results=100):
        channelConfig = self.configCatalog.get.extra.get("channelConfig", self.configLocal.get("ChannelConfig", {}))
        
        feeds = rawData.get("feeds", [])
        lastUpdate = feeds[-1].get("created_at", None) if feeds else None
        
        sensors = {}
        for sensorName, fieldNumber in channelConfig.items():
            fieldKey = f"field{fieldNumber}"
            values = []
            for feed in feeds:
                val = feed.get(fieldKey, None)
                if val is not None:
                    values.append(float(val))
            sensors[sensorName] = values
        
        return {
            "lastUpdate": lastUpdate,
            "sensors": sensors
        }
        
    def GET(self, *uri, **params):
        if uri[0] == "readData":
            results = int(params.get("size", 100))
            rawData = self.readThingspeak(results)
            data = self.formatThingspeakData(rawData, results)
            return json.dumps(data)
        else : 
            return cherrypy.HTTPError(404, "Unknown GET request")
    
    def mqttCallback(self, topic, message) -> None :
        messageRead = self.sensML.getIn(message)
        
        deviceID = messageRead.device_bn
        channelConfig = self.configCatalog.get.extra.get("channelConfig", self.configLocal.get("ChannelConfig", {}))
        
        fieldsData = {}
        for sensor in messageRead.device_e:
            sensorRead = self.sensML.getIn(sensor)
            sensorName = sensorRead.sensor_n
            sensorValue = sensorRead.sensor_v
            
            fieldNumber = channelConfig.get(sensorName, None)
            if fieldNumber is not None:
                fieldsData[fieldNumber] = sensorValue
        
        if fieldsData:
            self.uploadThingspeakMultiple(fieldsData)        
        
    def serviceRunTime(self) -> None :
        self.serviceRunTimeStatus = True
        self.updateLoopStart()
        
        while self.serviceRunTimeStatus :
            time.sleep(1)
    
    def killServiceRunTime(self) -> None :
        return super().killServiceRunTime()
