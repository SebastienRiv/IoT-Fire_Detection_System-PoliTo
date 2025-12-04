import paho.mqtt.client as PahoMQTT
import json

class MyMQTT:
    def __init__(self, clientID, broker, port, notifier=None):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.clientID = clientID
        self._topic = []
        self._isSubscriber = False
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived
    
    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))
        
    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        # A new message is received
        if self.notifier != None:
            json_payload = json.loads(msg.payload)
            self.notifier(msg.topic, json_payload)
        else :
            print ("ERROR - Message received without notifier: " + msg.payload.decode("utf-8") + " on topic " + msg.topic)
        
    def myPublish (self, topic, msg):
        if topic is None :
            print("Warning: Topic is None. Cannot publish message.")
            return
        if (msg is None) :
            print("Warning: Message is None. Cannot publish message.")
            return
        # if needed, you can do some computation or error-check before publishing
        print ("publishing '%s' with topic '%s'" % (msg, topic))
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, json.dumps(msg), 2)
    
    def mySubscribe (self, topic):
        if topic is None :
            print("Warning: Topic is None. Cannot subscribe.")
            return

        if (type(topic) is str):
            topic = [topic]
            
        if (len(topic) == 0):
            print("Warning: Topic list is empty. Cannot subscribe.")
            return
            
        for t in topic :
            # if needed, you can do some computation or error-check before subscribing
            print ("subscribing to %s" % (topic))
            # subscribe for a topic
            self._paho_mqtt.subscribe(t, 2)
            self._topic.append(t)
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
    
    def start(self):
        if self.broker is None or self.port is None :
            print("Error: Broker or Port is None. Cannot start MQTT client.")
            return
        #manage connection to broker
        self._paho_mqtt.connect(self.broker , self.port)
        self._paho_mqtt.loop_start()
    
    def stop (self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            for t in self._topic:
                self._paho_mqtt.unsubscribe(t)
            self._paho_mqtt.loop_stop()
            self._paho_mqtt.disconnect()