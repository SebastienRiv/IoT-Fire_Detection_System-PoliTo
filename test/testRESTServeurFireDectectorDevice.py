import cherrypy
import os
import json

class FireConfigServer(object):
    exposed = True

    def __init__(self):
        self.config = {
            "devices": [
                {
                    "deviceID": "firedev001",
                    "deviceName": "Fire Detector",
                    "SensorUpdateInterval": 5,
                    "MQTT": {
                        "ClientID": "FireDev",
                        "Broker": "broker.hivemq.com",
                        "Port": 1883
                    },
                    "TopicPub": "IoT/firedev001/data",
                    "TopicSub": "IoT/firedev001/cmd"
                },
                {
                    "deviceID": "firebutton001",
                    "deviceName": "Fire Button",
                    "SensorUpdateInterval": 5,
                    "MQTT": {
                        "ClientID": "FireButton",
                        "Broker": "broker.hivemq.com",
                        "Port": 1883
                    },
                    "TopicPub": "IoT/firebutton001/data",
                    "TopicSub": None
                }
            ]
        }

    def GET(self, *uri, **params):
        if len(uri) == 0 or uri[0] == "config":
            deviceID = params.get("device_id", None)
            if deviceID:
                return json.dumps(self.config["devices"][int(deviceID) - 1])
            else : 
                raise cherrypy.HTTPError(404, "Device not found")
        else:
            raise cherrypy.HTTPError(404, "Resource not found")

if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(FireConfigServer(), '/', conf)
    cherrypy.config.update({'server.socket_port': 8081})
    cherrypy.engine.start()
    cherrypy.engine.block()