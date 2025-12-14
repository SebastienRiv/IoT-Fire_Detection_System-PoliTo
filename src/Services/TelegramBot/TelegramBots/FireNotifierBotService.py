from dataclasses import dataclass
from src.Services.TelegramBot.TelegramBotService import TelegramBotService
from src.Services.MQTT.MQTTService import MQTTService
from time import sleep
import telepot
from telepot.loop import MessageLoop
import json

@dataclass
class FireAlarmData:
    buildingID: str
    buildingName: str
    address: str
    GPS_coordinates: dict
    floorID: str
    roomID: str
    clientID: str
    firefighterChatID: str
    userChatIDs: list


class FireNotifierBotService(TelegramBotService, MQTTService):
    
    def __init__(self, configFilePath:str) -> None:
        
        self.handler = {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}
        
        TelegramBotService.__init__(self, configFilePath, self.handler)
        MQTTService.__init__(self, configFilePath)

        self.setupTelegramBot()
        self.mqttSetupClient()

        self.userChatIDs = []
        self.firefighterChatID = ""

        
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
            if chat_ID not in self.userChatIDs:
                self.userChatIDs.append(chat_ID)
                self.telegramBot.sendMessage(chat_ID, "Welcome! You've registered to the fire detection system.")
            else:
                self.telegramBot.sendMessage(chat_ID, "Already registered successfully.")
    
        elif message == "/checkDevice": # Must be defined
            pass
    
    def on_callback_query(self, msg): # Must be defined
        pass

    def parse_alarm_info(self, payload) -> FireAlarmData:
        try:
            info = json.loads(payload)
            building_info = info.get("building", {})

            return FireAlarmData(
                buildingID=building_info.get("buildingID", ""),
                buildingName=building_info.get("buildingName", ""),
                address=building_info.get("address", ""),
                GPS_coordinates=building_info.get("GPS", {}),
                floorID=building_info.get("floorID", ""),
                roomID=building_info.get("roomID", ""),
                clientID=info.get("clientID", ""),
                firefighterChatID=info.get("fireFighterChatID", ""),
                userChatIDs=info.get("userChatIDList", "")
            )
        
        except Exception as e:
            print(f"Error in the payload: {e}")
            return None
    
    def create_telegram_msg(self, alarmData: FireAlarmData):

        return (f"🚨⚠️ FIRE ALLERT 🚨⚠️\n\n"
                f"🏢 Building name: {alarmData.buildingName}"
                f"📍 Address: {alarmData.address} | Floor: {alarmData.floorID} | Room: {alarmData.roomID}"
                f"🗺️ GPS coordinates: {alarmData.GPS_coordinates.get('lat', 'N/A')}, {alarmData.GPS_coordinates.get('long', 'N\A')}"
                f"💻 Device: {alarmData.clientID}\n\n"
                "❗INTERVENTION NEEDED IMMEDIATELY❗")
    
    def mqttCallback(self, topic, payload) -> None :
        try:
            alarmData = self.parse_alarm_info(payload)

            if not alarmData:
                print("Invalid mqtt message received.")
                return

            print(f"Alarm received from {alarmData.clientID}!")

            alert_msg = self.create_telegram_msg(alarmData)
                
            for chatID in alarmData.userChatIDs:
                if chatID in self.userChatIDs:
                    self.telegramBot.sendMessage(chatID, alert_msg)
                else:
                    print(f"ChatID '{chatID}' is not registered in the system.")
            
            if alarmData.firefighterChatID != self.firefighterChatID:
                self.firefighterChatID = alarmData.firefighterChatID
            
            self.telegramBot.sendMessage(self.firefighterChatID, alert_msg)


        except json.JSONDecodeError:
            print("Invalid json message.")
        except Exception as e:
            print(f"Error in the processing of the mqtt message: {e}")
    
    def serviceRunTime(self) -> None : # Must be defined
        pass