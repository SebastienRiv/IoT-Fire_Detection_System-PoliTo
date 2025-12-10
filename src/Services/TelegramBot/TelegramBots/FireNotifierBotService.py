from src.Services.TelegramBot.TelegramBotService import TelegramBotService
from src.Services.MQTT.MQTTService import MQTTService
from time import sleep
import telepot
from telepot.loop import MessageLoop
import json

class FireNotifierBotService(TelegramBotService, MQTTService):
    
    def __init__(self, configFilePath:str) -> None:
        
        self.handler = {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}
        
        TelegramBotService.__init__(self, configFilePath, self.handler)
        MQTTService.__init__(self, configFilePath)

        self.setupTelegramBot()
        self.mqttSetupClient()

        self.chatIDs = []

        
    def updateLoopRunTime(self, updateInterval:int=12) -> None :
        while self.serviceRunTimeStatus :
            modified = self.updateCatalogConfig()
            
            if modified :
                print("Info: Service catalog updated. Restarting Telegram Bot with new configuration.")
                self.setupTelegramBot()
                self.mqttSetupClient()
                        
            sleep(self.configCatalog.get.catalogUpdateIntervalCycles)
        
    def on_chat_message(self, msg) -> None:
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start":
            if chat_ID not in self.chatIDs:
                self.chatIDs.append(chat_ID)
                self.telegramBot.sendMessage(chat_ID, "Welcome! You've registered to the fire detection system.")
            else:
                self.telegramBot.sendMessage(chat_ID, "Already registered successfully.")
    
        elif message == "/checkDevice": # Must be defined
            pass


    
    def on_callback_query(self, msg): # Must be defined
        pass
    
    def mqttCallback(self, topic, payload) -> None :
        try:
            message = json.loads(payload)
            device_id = message["deviceID"]

            print(f"Alarm received from {device_id}!")

            dev_info = self.configCatalog.getDeviceFromCatalog(device_id)
            if dev_info is None:
                print("Device not found.")
            else:
                location = dev_info.get("location", {})
                address = location.get("address", "Unknown")
                floor = location.get("floor", "Unknown")
                room = location.get("room", "Unknown")
                alert_msg = (f"🚨⚠️ FIRE ALLERT 🚨⚠️\n\n"
                            f"📍 Position: {address}, Floor: {floor}, Room: {room}"
                            f"💻 Device: {device_id}\n\n"
                            "Intervention needed immediately!")
                
                for chatID in self.chatIDs:
                    self.telegramBot.sendMessage(chatID, alert_msg)

        except json.JSONDecodeError:
            print("Invalid json message.")
        except Exception as e:
            print(f"Error in the processing of the mqtt message: {e}")
    
    def serviceRunTime(self) -> None : # Must be defined
        pass