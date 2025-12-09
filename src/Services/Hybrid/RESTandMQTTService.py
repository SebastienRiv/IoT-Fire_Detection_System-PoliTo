from Services.REST.RESTService import RESTService
from Services.MQTT.MQTTService import MQTTService
from time import sleep

class RESTandMQTTService(RESTService, MQTTService):
    
    def __init__(self, configFilePath:str) -> None :
        super().__init__(configFilePath)
        
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.serviceRunTimeStatus :
            modified = self.updateCatalogConfig()
            
            if modified :
                MQTTService.mqttSetupClient(self)
                RESTService.restSetupServer(self)
                        
            sleep(self.configCatalog.get.catalogUpdateIntervalCycles)
        
    def serviceRunTime(self) -> None :
        pass

    def killServiceRunTime(self) -> None :
        self.serviceRunTimeStatus = False
        if self.serverREST is not None:
            self.serverREST.killServerRunTime()
        if self.clientMQTT is not None :
            self.clientMQTT.stop()