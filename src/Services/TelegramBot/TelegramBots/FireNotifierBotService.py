from src.Services.TelegramBot.TelegramBotService import TelegramBotService
from src.Services.MQTT.MQTTService import MQTTService
from src.libs.Telegram.TelegramBot import TelegramBot
from time import sleep

class FireNotifierBotService(TelegramBotService, MQTTService):
    
    def __init__(self, configFilePath:str, token:str) -> None:
        
        self.handler = {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}
        
        TelegramBotService.__init__(self, configFilePath, self.handler)
        MQTTService.__init__(self, configFilePath)
        
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.serviceRunTimeStatus :
            modified = self.updateCatalogConfig()
            
            if modified :
                print("Info: Service catalog updated. Restarting Telegram Bot with new configuration.")
                self.setupTelegramBot()
                self.mqttSetupClient()
                        
            sleep(self.configCatalog.get.catalogUpdateIntervalCycles)
        
    def on_chat_message(self, msg): # Must be defined
        pass
    
    def on_callback_query(self, msg): # Must be defined
        pass
    
    def mqttCallback(self, topic, message) -> None : # Must be defined
        pass
    
    def serviceRunTime(self) -> None : # Must be defined
        pass