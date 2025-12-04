import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../..")

from src.libs.MQTT.MyMQTT import MyMQTT
import time

broker = "broker.hivemq.com"
port = 1883
clientID = "TestSubscriberFireDev"
topic = "IoT/firedev001/data"

def callback(topic, msg):
    print(f"Message reçu sur {topic} : {msg}")

mqttClient = MyMQTT(clientID, broker, port)
mqttClient.start()
mqttClient.mySubscribe(topic)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    mqttClient.stop()
    print("Arrêt du subscriber.")