import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../..")

from src.libs.MQTT.MyMQTT import MyMQTT
import time
import json

broker = "broker.hivemq.com"
port = 1883
clientID = "TestPublisherFireDev"
topic = "IoT/firedev001/cmd"

mqttClient = MyMQTT(clientID, broker, port)
mqttClient.start()

try:
    while True:
        print("Tapez 'ON' pour activer l'alarme, 'OFF' pour la désactiver :")
        user_input = input(">> ").strip().upper()
        if user_input in ["ON", "OFF"]:
            message = {"alarmStatus": True if user_input == "ON" else False}
            mqttClient.myPublish(topic, message)
            print(f"Message publié : {message}")
        time.sleep(1)
except KeyboardInterrupt:
    mqttClient.stop()
    print("Arrêt du publisher.")