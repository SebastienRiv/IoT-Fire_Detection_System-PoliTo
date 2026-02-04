from dataclasses import dataclass
from src.Services.TelegramBot.TelegramBotService import TelegramBotService
from src.Services.MQTT.MQTTService import MQTTService
from time import sleep
import telepot
from telepot.loop import MessageLoop
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import json
import threading

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
    userChatIDList: list


class FireNotifierBotService(TelegramBotService, MQTTService):
    
    def __init__(self, configFilePath:str) -> None:
        
        self.handler = {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}
        
        TelegramBotService.__init__(self, configFilePath, self.handler)
        MQTTService.__init__(self, configFilePath)

        self.setupTelegramBot()
        self.mqttSetupClient()

        self.userChatIDs = []
        self.firefighterChatIDs = []
        self.passwordFF = "firestation_123"

        self.timer = None

    def onConfigUpdate(self):
        print("Info: Service catalog updated. Restarting Telegram Bot with new configuration.")
        self.setupTelegramBot()
        self.mqttSetupClient()
        
    def on_chat_message(self, msg) -> None:
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start":
            if chat_ID not in self.userChatIDs:
                self.userChatIDs.append(chat_ID)
                self.telegramBot.sendMessage(chat_ID, "Welcome! You have registered to the fire detection system as a user.")
            else:
                self.telegramBot.sendMessage(chat_ID, "Already registered successfully.")
        elif message == f"/start {self.passwordFF}":
            if chat_ID not in self.firefighterChatIDs:
                self.firefighterChatIDs.append(chat_ID)
                self.telegramBot.sendMessage(chat_ID, "Welcome! You have registered to the fire detecction system as a fire station.")
            else:
                self.telegramBot.sendMessage(chat_ID, "Already registered successfully.")
        elif message == "/checkDevice": # Must be defined
            pass
    
    def on_callback_query(self, msg): # Must be defined
        content_type, chat_type, chat_ID = telepot.glance(msg)

        
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
                userChatIDList=info.get("userChatIDList", [])
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
    
    def sendToUsers(self, message, usersList) -> None:
        for chatID in usersList:
            if chatID in self.userChatIDs:
                self.telegramBot.sendMessage(chatID, message)
            else:
                print(f"ChatID '{chatID}' is not registered in the system.")

    def broadcastToFirefighters(self, alert, priorStation) -> None:
        print("TIME EXPIRED! Sending the intervention request to all stations...")

        keyboard = InlineKeyboardMarkup(inline_keyboard = 
                                                [InlineKeyboardButton(text="🚒 Accept Intervention (broadcast)", callback_data="accept_intervention")])

        updated_alert = f"⚠️​⚠️​ Closest station is not responding ⚠️​⚠️​\n\n{alert}"

        for chatID in self.firefighterChatIDs:
            if str(chatID) != str(priorStation):
                self.telegramBot.sendMessage(chatID, updated_alert, reply_markup=keyboard)

    
    def mqttCallback(self, topic, payload) -> None :
        try:
            alarmData = self.parse_alarm_info(payload)

            if not alarmData:
                print("Invalid mqtt message received.")
                return

            print(f"Alarm received from {alarmData.clientID}!")

            alert_msg = self.create_telegram_msg(alarmData)

            self.sendToUsers(alert_msg, alarmData.userChatIDList)

            keyboard = InlineKeyboardMarkup(inline_keyboard = 
                                                [InlineKeyboardButton(text="🚒 Accept Intervention", callback_data="accept_intervention")])

            if alarmData.firefighterChatID in self.firefighterChatIDs:
                print(f"Sending the alert to the closest fire station {alarmData.firefighterChatID}...")
                self.telegramBot.sendMessage(alarmData.firefighterChatID, alert_msg, reply_markup=keyboard)

                if self.timer is not None:
                    self.timer.cancel()
                
                self.timer = threading.Timer(15.0, self.broadcastToFirefighters, args=[alert_msg, alarmData.firefighterChatID])
                self.timer.start()
                print("Timer activated: 15 seconds until broadcast.")
            else:
                self.broadcastToFirefighters(self, alert_msg, alarmData.firefighterChatID)


        except json.JSONDecodeError:
            print("Invalid json message.")
        except Exception as e:
            print(f"Error in the processing of the mqtt message: {e}")
    
    def serviceRunTime(self) -> None :
        self.serviceRunTimeStatus = True

        self.updateLoopStart()

        while self.serviceRunTimeStatus:
            sleep(1)