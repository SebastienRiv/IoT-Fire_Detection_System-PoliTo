from abc import ABC, abstractmethod
from src.Services.REST.RESTService import RESTService
from src.Services.MQTT.MQTTService import MQTTService
from time import sleep

class RESTandMQTTService(RESTService, MQTTService, ABC):
    
    def __init__(self, configFilePath:str) -> None :
        super().__init__(configFilePath)
        
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.serviceRunTimeStatus :
            modified = self.updateCatalogConfig()
            
            if modified :
                MQTTService.mqttSetupClient(self)
                RESTService.restSetupServer(self)
                        
            sleep(self.configCatalog.get.catalogUpdateIntervalCycles)
            
    @abstractmethod 
    def POST(self, *uri, **params):
        return RESTService.POST(self, *uri, **params)
    
    @abstractmethod 
    def GET(self, *uri, **params):
        return RESTService.GET(self, *uri, **params)
    
    @abstractmethod 
    def PUT(self, *uri, **params):
        return RESTService.PUT(self, *uri, **params)
    
    @abstractmethod
    def DELETE(self, *uri, **params):
        return RESTService.DELETE(self, *uri, **params)
    
    @abstractmethod
    def mqttCallback(self, topic, message) -> None :
        return MQTTService.mqttCallback(self, topic, message)
        
    @abstractmethod
    def serviceRunTime(self) -> None :
        pass

    @abstractmethod
    def killServiceRunTime(self) -> None :
        self.serviceRunTimeStatus = False
        if self.serverREST is not None:
            self.serverREST.killServerRunTime()
        if self.clientMQTT is not None :
            self.clientMQTT.stop()