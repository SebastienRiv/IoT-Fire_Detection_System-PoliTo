from src.Services.Service import Service
from src.libs.Telegram.TelegramBot import TelegramBot
from time import sleep

class TelegramBotService(Service):
    
    def __init__(self, configFilePath:str, token:str, handler:dict) -> None:
        super().__init__(configFilePath)
        
        self.token = token
        self.telegramBot = None
        self.handler = handler
        
    def getToken(self) -> str:
        return self.token
    
    def getTelegramBot(self):
        return self.telegramBot
    
    def getHandler(self) -> dict:
        return self.handler

    def setupTelegramBot(self) -> None:
        self.telegramBot = TelegramBot(self.token, self.handler)
    
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.serviceRunTimeStatus :
            oldCatalog = self.configCatalog.copy()
            self.updateCatalogConfig()
            
            if oldCatalog != self.configCatalog :
                print("Info: Service catalog updated. Restarting Telegram Bot with new configuration.")
                self.setupTelegramBot()
                        
            sleep(self.configCatalog.get("CatalogUpdateIntervalCycles", self.configLocal.get("CatalogUpdateIntervalCycles", updateInterval)))
            
    def serviceRunTime(self) -> None :
        pass
              
    def killServiceRunTime(self) -> None :
        self.serviceRunTimeStatus = False