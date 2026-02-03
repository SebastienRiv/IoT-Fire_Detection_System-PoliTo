from abc import ABC, abstractmethod
from src.Services.Hybrid.RESTandMQTTService import RESTandMQTTService
import cherrypy

class TimeSerieService(RESTandMQTTService, ABC):
    
    def __init__(self, configFilePath:str, envFilePath:str) -> None :
        super().__init__(configFilePath)
        
        self.envFilePath = envFilePath
        self.userApiKey = None
        self.userChannelApiKey = None
        self.envLoadConfig()
        
    def envLoadConfig(self) -> None :
        with open(self.envFilePath, 'r') as envFile:
            for line in envFile:
                key, value = line.strip().split('=', 1)
                if key == "USERAPIKEY":
                    self.userApiKey = value
                elif key == "CHANNELAPIKEY":
                    self.userChannelApiKey = value
              
    def POST(self, *uri, **params):
        return super().POST(*uri, **params)
    
    @abstractmethod 
    def GET(self, *uri, **params):
        return cherrypy.HTTPError(404, "GET method not implemented")
    
    def PUT(self, *uri, **params):
        return super().PUT(*uri, **params)
    
    def DELETE(self, *uri, **params):
        return super().DELETE(*uri, **params)
    
    @abstractmethod
    def mqttCallback(self, topic, message) -> None :
        pass
     
    @abstractmethod               
    def serviceRunTime(self) -> None :
        pass
    
    @abstractmethod
    def killServiceRunTime(self) -> None :
        return super().killServiceRunTime()