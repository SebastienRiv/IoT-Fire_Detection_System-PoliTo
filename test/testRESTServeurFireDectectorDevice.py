import cherrypy
import os
import json

class FireConfigServer(object):
    exposed = True

    def __init__(self):
        self.config = {
            "devices": [
                {
                    "clientID": "firedev001",
                    "deviceName": "Fire Detector",
                    "SensorUpdateInterval": 5,
                    "MQTT": {
                        "broker": "broker.hivemq.com",
                        "port": 1883,
                        "topicPub": "IoT/firedev001/data",
                        "topicSub": ["IoT/firedev001/cmd"]
                    }
                },
                {
                    "clientID": "firebutton001",
                    "deviceName": "Fire Button",
                    "SensorUpdateInterval": 5,
                    "MQTT": {
                        "clientID": "FireButton",
                        "broker": "broker.hivemq.com",
                        "port": 1883,
                        "topicPub": "IoT/firebutton001/data",
                        "topicSub": None
                    }
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