import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.libs.MQTT.SubscriberMQTT import SubscriberMQTT
import time

def callback(topic, msg):
    print(f"[SUBSCRIBER] Message received on topic {topic}: {msg}")

if __name__ == "__main__":
    broker = "broker.hivemq.com"
    port = 1883
    ClientID = "TestSubscriberMultiTopics"
    topics = [
        "IoT/test/topic1",
        "IoT/test/topic2",
        "IoT/test/topic3"
    ]
    subscriber = SubscriberMQTT(ClientID, broker, port, topics, callback)
    subscriber.startClient()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        subscriber.stopClient()
        print("Subscriber stopped.")
