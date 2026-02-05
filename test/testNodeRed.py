import cherrypy
import json
import time

# Base de données en mémoire
catalogDB = {
    "projectOwner": "PoliTo",
    "projectName": "IoT Fire Detection System",
    "lastUpdate": "",
    "broker": {
        "broker_name": "mqtt.eclipseprojects.io",
        "port": 1883
    },
    "devicesList": [],
    "servicesList": [],
    "fireFightersList": [],
    "usersList": [],
    "buildingList": []
}

def updateTimestamp():
    catalogDB["lastUpdate"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

class CatalogAPI:
    
    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps({"status": "online", "message": "Catalog API is running"}).encode('utf-8')
    
    # ==================== HEALTH CHECK ====================
    @cherrypy.expose
    def health(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps({
            "status": "online",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "devices": len(catalogDB["devicesList"]),
            "services": len(catalogDB["servicesList"]),
            "users": len(catalogDB["usersList"]),
            "fireFighters": len(catalogDB["fireFightersList"]),
            "buildings": len(catalogDB["buildingList"])
        }).encode('utf-8')
    
    # ==================== DEVICES ====================
    @cherrypy.expose
    def devices(self, clientID=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if cherrypy.request.method == "GET":
            if clientID:
                for d in catalogDB["devicesList"]:
                    if d["clientID"] == clientID:
                        return json.dumps(d).encode('utf-8')
                raise cherrypy.HTTPError(404, "Device not found")
            return json.dumps(catalogDB["devicesList"]).encode('utf-8')
        
        elif cherrypy.request.method == "POST":
            data = json.loads(cherrypy.request.body.read())
            data["lastUpdate"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            catalogDB["devicesList"].append(data)
            updateTimestamp()
            return json.dumps({"status": "success", "message": f"Device {data.get('clientID')} added"}).encode('utf-8')
        
        elif cherrypy.request.method == "PUT":
            if not clientID:
                raise cherrypy.HTTPError(400, "clientID required")
            data = json.loads(cherrypy.request.body.read())
            for d in catalogDB["devicesList"]:
                if d["clientID"] == clientID:
                    d.update(data)
                    updateTimestamp()
                    return json.dumps({"status": "success", "message": f"Device {clientID} updated"}).encode('utf-8')
            raise cherrypy.HTTPError(404, "Device not found")

        elif cherrypy.request.method == "DELETE":
            if not clientID:
                raise cherrypy.HTTPError(400, "clientID required")
            for i, d in enumerate(catalogDB["devicesList"]):
                if d["clientID"] == clientID:
                    catalogDB["devicesList"].pop(i)
                    updateTimestamp()
                    return json.dumps({"status": "success", "message": f"Device {clientID} deleted"}).encode('utf-8')
            raise cherrypy.HTTPError(404, "Device not found")
    
    # ==================== USERS ====================
    @cherrypy.expose
    def users(self, userID=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if cherrypy.request.method == "GET":
            if userID:
                for u in catalogDB["usersList"]:
                    if u["userID"] == userID:
                        return json.dumps(u).encode('utf-8')
            return json.dumps(catalogDB["usersList"]).encode('utf-8')

        elif cherrypy.request.method == "POST":
            data = json.loads(cherrypy.request.body.read())
            catalogDB["usersList"].append(data)
            updateTimestamp()
            return json.dumps({"status": "success", "message": f"User {data.get('userName')} added"}).encode('utf-8')

        elif cherrypy.request.method == "PUT":
            if not userID:
                raise cherrypy.HTTPError(400, "userID required")
            data = json.loads(cherrypy.request.body.read())
            for u in catalogDB["usersList"]:
                if str(u["userID"]) == str(userID):
                    u.update(data)
                    updateTimestamp()
                    return json.dumps({"status": "success", "message": f"User {userID} updated"}).encode('utf-8')
            raise cherrypy.HTTPError(404, "User not found")

        elif cherrypy.request.method == "DELETE":
            if not userID:
                raise cherrypy.HTTPError(400, "userID required")
            for i, u in enumerate(catalogDB["usersList"]):
                if str(u["userID"]) == str(userID):
                    catalogDB["usersList"].pop(i)
                    updateTimestamp()
                    return json.dumps({"status": "success", "message": f"User {userID} deleted"}).encode('utf-8')
            raise cherrypy.HTTPError(404, "User not found")
    
    # ==================== FIREFIGHTERS ====================
    @cherrypy.expose
    def firefighters(self, fireFighterID=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if cherrypy.request.method == "GET":
            if fireFighterID:
                for f in catalogDB["fireFightersList"]:
                    if f["fireFighterID"] == fireFighterID:
                        return json.dumps(f).encode('utf-8')
            return json.dumps(catalogDB["fireFightersList"]).encode('utf-8')

        elif cherrypy.request.method == "POST":
            data = json.loads(cherrypy.request.body.read())
            catalogDB["fireFightersList"].append(data)
            updateTimestamp()
            return json.dumps({"status": "success", "message": f"FireFighter {data.get('fireFighterID')} added"}).encode('utf-8')

        elif cherrypy.request.method == "PUT":
            if not fireFighterID:
                raise cherrypy.HTTPError(400, "fireFighterID required")
            data = json.loads(cherrypy.request.body.read())
            for f in catalogDB["fireFightersList"]:
                if f["fireFighterID"] == fireFighterID:
                    f.update(data)
                    updateTimestamp()
                    return json.dumps({"status": "success", "message": f"FireFighter {fireFighterID} updated"}).encode('utf-8')
            raise cherrypy.HTTPError(404, "FireFighter not found")

        elif cherrypy.request.method == "DELETE":
            if not fireFighterID:
                raise cherrypy.HTTPError(400, "fireFighterID required")
            for i, f in enumerate(catalogDB["fireFightersList"]):
                if f["fireFighterID"] == fireFighterID:
                    catalogDB["fireFightersList"].pop(i)
                    updateTimestamp()
                    return json.dumps({"status": "success", "message": f"FireFighter {fireFighterID} deleted"}).encode('utf-8')
            raise cherrypy.HTTPError(404, "FireFighter not found")
    
    # ==================== BUILDINGS ====================
    @cherrypy.expose
    def buildings(self, buildingID=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if cherrypy.request.method == "GET":
            if buildingID:
                for b in catalogDB["buildingList"]:
                    if b["buildingID"] == buildingID:
                        return json.dumps(b).encode('utf-8')
            return json.dumps(catalogDB["buildingList"]).encode('utf-8')

        elif cherrypy.request.method == "POST":
            data = json.loads(cherrypy.request.body.read())
            catalogDB["buildingList"].append(data)
            updateTimestamp()
            return json.dumps({"status": "success", "message": f"Building {data.get('buildingID')} added"}).encode('utf-8')

        elif cherrypy.request.method == "PUT":
            if not buildingID:
                raise cherrypy.HTTPError(400, "buildingID required")
            data = json.loads(cherrypy.request.body.read())
            for b in catalogDB["buildingList"]:
                if b["buildingID"] == buildingID:
                    b.update(data)
                    updateTimestamp()
                    return json.dumps({"status": "success", "message": f"Building {buildingID} updated"}).encode('utf-8')
            raise cherrypy.HTTPError(404, "Building not found")

        elif cherrypy.request.method == "DELETE":
            if not buildingID:
                raise cherrypy.HTTPError(400, "buildingID required")
            for i, b in enumerate(catalogDB["buildingList"]):
                if b["buildingID"] == buildingID:
                    catalogDB["buildingList"].pop(i)
                    updateTimestamp()
                    return json.dumps({"status": "success", "message": f"Building {buildingID} deleted"}).encode('utf-8')
            raise cherrypy.HTTPError(404, "Building not found")
    
    # ==================== FULL CATALOG ====================
    @cherrypy.expose
    def catalog(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(catalogDB).encode('utf-8')
    
    # ==================== BROKER ====================
    @cherrypy.expose
    def broker(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(catalogDB["broker"]).encode('utf-8')
    
    # ==================== DEBUG ====================
    @cherrypy.expose
    def debug(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(catalogDB, indent=2).encode('utf-8')


if __name__ == "__main__":
    config = {
        "/": {
            "tools.sessions.on": True,
            "tools.encode.on": True,
            "tools.encode.encoding": "utf-8",
            "tools.response_headers.on": True,
            "tools.response_headers.headers": [("Content-Type", "application/json")]
        }
    }
    
    cherrypy.config.update({
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 8081
    })
    
    print("="*50)
    print("  NODE-RED TEST CATALOG API")
    print("="*50)
    print("\nEndpoints disponibles:")
    print("  GET  /health              - Health check")
    print("  GET  /catalog             - Full catalog")
    print("  GET  /broker              - Broker info")
    print("")
    print("  GET  /devices             - Liste devices")
    print("  POST /devices             - Ajouter device")
    print("  DELETE /devices?clientID= - Supprimer device")
    print("")
    print("  GET  /users               - Liste users")
    print("  POST /users               - Ajouter user")
    print("  DELETE /users?userID=     - Supprimer user")
    print("")
    print("  GET  /firefighters             - Liste firefighters")
    print("  POST /firefighters             - Ajouter firefighter")
    print("  DELETE /firefighters?fireFighterID= - Supprimer firefighter")
    print("")
    print("  GET  /buildings                - Liste buildings")
    print("  POST /buildings                - Ajouter building")
    print("  DELETE /buildings?buildingID=  - Supprimer building")
    print("="*50)
    print(f"\nServeur démarré sur http://localhost:8081")
    print("="*50 + "\n")
    
    cherrypy.quickstart(CatalogAPI(), "/", config)
