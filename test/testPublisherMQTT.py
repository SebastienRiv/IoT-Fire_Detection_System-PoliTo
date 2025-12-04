import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.libs.MQTT.PublisherMQTT import PublisherMQTT
import time
import json

if __name__ == "__main__":
    broker = "broker.hivemq.com"
    port = 1883
    ClientID = "TestPublisherMultiTopics"
    topics = [
        "IoT/test/topic1",
        "IoT/test/topic2",
        "IoT/test/topic3"
    ]
    publisher = PublisherMQTT(ClientID, broker, port)
    publisher.startClient()
    try:
        while True:
            for i, topic in enumerate(topics):
                message = {"msg": f"Hello from publisher {i}", "timestamp": time.time()}
                publisher.publish(topic, json.dumps(message))
                print(f"Published to {topic}: {message}")
            time.sleep(2)
    except KeyboardInterrupt:
        publisher.stopClient()
        print("Publisher stopped.")
