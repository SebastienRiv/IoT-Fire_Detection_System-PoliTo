from src.Services.REST.RESTServices.CatalogProviderService import CatalogProviderService
from src.libs.CatalogJSON.CatalogJSON import CatalogJSON
import threading
import json
import cherrypy
import time


class JSONCatalogProviderService(CatalogProviderService):

    def __init__(self, configFilePath: str) -> None:

        # initialize CatalogProviderService that initialize RESTService (super-class)
        super().__init__(configFilePath)

        # this thing is used to prevent 2 or more services to write the catalog at the same time
        self.lock = threading.RLock()

        self.catalogHelper = CatalogJSON(self.configLocal)
        self.catalog = dict()
        self._load()

    def _load(self) -> None:

        # the lock is used in case we want to load the catalog while is being saved
        with self.lock:
            # if the catalog exists, self.catalog = loaded Catalog, otherwise loads the template
            try:
                with open(self.catalogPath, 'r') as catalog:
                    self.catalogData = json.load(catalog)
            except FileNotFoundError:
                self.catalogData = self.catalogHelper.getTemplate()
                self._save()
            except json.JSONDecodeError:
                self.catalogData = self.catalogHelper.getTemplate()
                self._save()

    def _save(self) -> None:

        self.catalogData["lastUpdate"] = time.time()

        # stop more than 1 service to write at the same time
        with self.lock:
            # saves the new catalog (from not existing -> template)
            try:
                with open(self.catalogPath, 'w') as catalog:
                    json.dump(self.catalogData, catalog, indent=4)

            except IOError as e:
                print(f"Error saving catalog to {self.catalogPath}: {e}")

            # just adding this exeption to catch any other I might not know
            except Exception as e:
                print(f"Unexpected error saving catalog: {e}")

    def _find_item(self, list_name, id_key, target_id):
        """
        Find an item in a specific list.
        If found:
            return item, index
        Else:
            return None, None
        """
        current_list = self.catalogData.get(list_name, [])
        for index, item in enumerate(current_list):
            if item.get(id_key) == target_id:
                return item, index
        return None, None

    # REST methods

    def GET(self, *uri, **params):

        # NOTE: don't know the actual names yet
        """
        GET /getCatalog
        GET /getResourceByID?clientID=<resource_id>
        GET /getUserByID?userID=<user_id>
        GET /getBuildingByID?buildingID=<building_id>
        GET /getBuildingDevices?buildingID=<building_id>
        GET /getDeviceByMeasure?measure=<measure_name>
        GET /getServiceByID?clientID=<service_id>
        GET /getServiceThreshold?clientID=<service_id>
        GET /getFireFighterByID?fireFighterID=<firefighter_id>
        """
        #                        uri[0]
        # if len(uri) == 0 --> /
        # if len(uri) > 0 --> /<something>
        # NOTE: the check on the name of in params is done because we are keeping chaing the json
        # I want to avoid silent errors if the naming mismatches
        try:
            if len(uri) == 1:
                endpointName = uri[0]

                if endpointName == "getCatalog":
                    return json.dumps({"status": "success", "data": self.catalogData})
                
                elif endpointName == "getResourceByID":

                    # check if clientID exists in params (naming mismatch?)
                    if "clientID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'clientID' parameter is missing.")
                    
                    clientID = params["clientID"]

                    # check if ID in devicesList
                    device, _ = self._find_item("devicesList", "clientID", clientID)
                    if device:
                        return json.dumps({"status": "success", "data": device})
                    # if it doesnt find any ID matching
                    raise cherrypy.HTTPError(404, "Resource not found.")
                
                elif endpointName == "getUserByID":

                    if "userID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'userID' parameter is missing.")
                    
                    userID = params["userID"]

                    user, _ = self._find_item("usersList", "userID", userID)
                    if user:
                        return json.dumps({"status": "success", "data": user})
                    
                    raise cherrypy.HTTPError(404, "User not found.")
                
                elif endpointName == "getBuildingByID":

                    if "buildingID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'buildingID' parameter is missing.")
                    
                    buildingID = params["buildingID"]

                    building, _ = self._find_item("buildingList", "buildingID", buildingID)
                    if building:
                        return json.dumps({"status": "success", "data": building})
                    
                    raise cherrypy.HTTPError(404, "Building not found.")

                elif endpointName == "getBuildingDevices":

                    if "buildingID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'buildingID' parameter is missing.")
                    
                    buildingID = params["buildingID"]
                    building, _ = self._find_item("buildingList", "buildingID", buildingID)
                    
                    if not building:
                        raise cherrypy.HTTPError(404, "Building not found.")

                    target_client_ids = []
                    for floor in building.get("floor", []):
                        for room in floor.get("rooms", []):
                            for dev_ref in room.get("devicesList", []):
                                if "clientID" in dev_ref:
                                    target_client_ids.append(dev_ref["clientID"])

                    devicesInBuilding = []
                    for device in self.catalogData["devicesList"]:
                        if device["clientID"] in target_client_ids:
                            devicesInBuilding.append(device)
                    
                    return json.dumps({"status": "success", "data": {"buildingID": buildingID, "devices": devicesInBuilding}})

                elif endpointName == "getDeviceByMeasure":

                    if "measure" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'measure' parameter is missing.")
                    
                    target_measure = params["measure"]
                    found_devices = []

                    for device in self.catalogData["devicesList"]:
                        if target_measure in device.get("measureType", []):
                            found_devices.append(device)
                    
                    return json.dumps({"status": "success", "data": found_devices})
                
                elif endpointName == "getServiceByID":

                    if "clientID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'clientID' parameter is missing.")
                    
                    clientID = params["clientID"]

                    service, _ = self._find_item("servicesList", "clientID", clientID)
                    if service:
                        return json.dumps({"status": "success", "data": service})
                    
                    raise cherrypy.HTTPError(404, "Service not found.")

                elif endpointName == "getServiceThreshold":

                    if "clientID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'clientID' parameter is missing.")
                    
                    clientID = params["clientID"]

                    service, _ = self._find_item("servicesList", "clientID", clientID)
                    if service:
                        extra_section = service.get("extra", {})
                        if not isinstance(extra_section, dict):
                            extra_section = {}
                        if "threshold" in extra_section:
                            return json.dumps({"status": "success", "data": {"clientID": clientID, "threshold": extra_section["threshold"]}})
                        raise cherrypy.HTTPError(404, "Threshold not found.")
                    
                    raise cherrypy.HTTPError(404, "Service not found.")
                
                elif endpointName == "getFireFighterByID":

                    if "fireFighterID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'fireFighterID' parameter is missing.")
                    
                    fireFighterID = params["fireFighterID"]

                    fireFighter, _ = self._find_item("fireFightersList", "fireFighterID", fireFighterID)
                    if fireFighter:
                        return json.dumps({"status": "success", "data": fireFighter})
                    
                    raise cherrypy.HTTPError(404, "Fire fighter not found.")

                else:
                    raise cherrypy.HTTPError(400, "Bad Request: Unknown endpoint.")

        except Exception as e:
            raise cherrypy.HTTPError(500, f"Internal Server Error: {e}")

    # PUT method updates the catalog
    def PUT(self, *uri, **params):

        # NOTE: don't know the actual names yet
        """
        PUT /updateSystemConfig
        
                uri[0]         uri[1]
        PUT /updateDevice/<clientID>
        PUT /updateUser/<userID>
        PUT /updateBuilding/<buildingID>
        PUT /updateService/<clientID>
        PUT /updateFireFighter/<fireFighterID>
        Body: JSON with new catalog data
        """

        try:
            if len(uri) == 1 and uri[0] == "updateSystemConfig":
                body = cherrypy.request.body.read()
                try:
                    body = json.loads(body)
                except json.JSONDecodeError:
                    raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON.")

                if "projectOwner" in body:
                    self.catalogData["projectOwner"] = body["projectOwner"]
                if "projectName" in body:
                    self.catalogData["projectName"] = body["projectName"]
                if "broker" in body:
                    if isinstance(body["broker"], dict):
                        for k, v in body["broker"].items():
                            self.catalogData["broker"][k] = v
                    else:
                        self.catalogData["broker"] = body["broker"]

                self._save()
                return json.dumps({"status": "updated", "data": self.catalogData})

            elif len(uri) == 2:
                endpointName = uri[0]
                targetID = uri[1]
                # check if the endpoint is correct
                if endpointName == "updateDevice":

                    bodyUpdatedDevice = cherrypy.request.body.read()

                    try:
                        bodyUpdatedDevice = json.loads(bodyUpdatedDevice)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")

                    if bodyUpdatedDevice["clientID"] != targetID:
                        raise cherrypy.HTTPError(400, "DeviceID in the URI does not match the one in the body")

                    device, _ = self._find_item("devicesList", "clientID", targetID)
                    
                    if device:
                        # update the device info
                        for key, value in bodyUpdatedDevice.items():
                            if key in device:
                                device[key] = value
                        # update timestamp
                        device["lastUpdate"] = time.time()
                        
                        self._save()
                        # in this case I think it's better to return the catalog since it might need to update the page
                        return json.dumps({"status": "updated", "data": self.catalogData})
                    else:
                        raise cherrypy.HTTPError(404, "ClientID not found in the catalog.")
                
                elif endpointName == "updateUser":
                    bodyUpdatedUser = cherrypy.request.body.read()

                    try:
                        bodyUpdatedUser = json.loads(bodyUpdatedUser)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")

                    if bodyUpdatedUser["userID"] != targetID:
                        raise cherrypy.HTTPError(400, "UserID in the URI does not match the one in the body")

                    user, _ = self._find_item("usersList", "userID", targetID)
                    
                    if user:
                        # update the user info
                        for key, value in bodyUpdatedUser.items():
                            if key in user:
                                user[key] = value
                        
                        self._save()
                        return json.dumps({"status": "updated", "data": self.catalogData})
                    else:
                        raise cherrypy.HTTPError(404, "UserID not found in the catalog.")

                elif endpointName == "updateBuilding":
                    bodyUpdatedBuilding = cherrypy.request.body.read()

                    try:
                        bodyUpdatedBuilding = json.loads(bodyUpdatedBuilding)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")

                    if bodyUpdatedBuilding["buildingID"] != targetID:
                        raise cherrypy.HTTPError(400, "BuildingID in the URI does not match the one in the body")

                    building, _ = self._find_item("buildingList", "buildingID", targetID)
                    
                    if building:
                        # update the building info
                        for key, value in bodyUpdatedBuilding.items():
                            if key in building:
                                building[key] = value
                        
                        self._save()
                        return json.dumps({"status": "updated", "data": self.catalogData})
                    else:
                        raise cherrypy.HTTPError(404, "BuildingID not found in the catalog.")
                
                elif endpointName == "updateService":
                    bodyUpdatedService = cherrypy.request.body.read()

                    try:
                        bodyUpdatedService = json.loads(bodyUpdatedService)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")

                    if bodyUpdatedService["clientID"] != targetID:
                        raise cherrypy.HTTPError(400, "ClientID in the URI does not match the one in the body")

                    service, _ = self._find_item("servicesList", "clientID", targetID)
                    
                    if service:
                        # update the service info
                        for key, value in bodyUpdatedService.items():
                            if key == "extra":
                                if isinstance(service.get("extra"), dict) and isinstance(value, dict):
                                    service["extra"].update(value)
                                else:
                                    service["extra"] = value
                            elif key in service:
                                service[key] = value
                        # update timestamp
                        service["lastUpdate"] = time.time()
                        
                        self._save()
                        return json.dumps({"status": "updated", "data": self.catalogData})
                    else:
                        raise cherrypy.HTTPError(404, "ClientID not found in the catalog.")
                
                elif endpointName == "updateFireFighter":
                    bodyUpdatedFireFighter = cherrypy.request.body.read()

                    try:
                        bodyUpdatedFireFighter = json.loads(bodyUpdatedFireFighter)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")

                    if bodyUpdatedFireFighter["fireFighterID"] != targetID:
                        raise cherrypy.HTTPError(400, "FireFighterID in the URI does not match the one in the body")

                    fireFighter, _ = self._find_item("fireFightersList", "fireFighterID", targetID)
                    
                    if fireFighter:
                        # update the fire fighter info
                        for key, value in bodyUpdatedFireFighter.items():
                            if key in fireFighter:
                                fireFighter[key] = value
                        
                        self._save()
                        return json.dumps({"status": "updated", "data": self.catalogData})
                    else:
                        raise cherrypy.HTTPError(404, "FireFighterID not found in the catalog.")
                
                else:
                    raise cherrypy.HTTPError(400,"The URL should be <url>/updateDevice/<deviceID> or similar")
            else:
                raise cherrypy.HTTPError(400, "Bad Request")

        except Exception as e:
            raise cherrypy.HTTPError(500, f"Internal Server Error: {e}")
        
    def POST(self, *uri, **params):
        """
                uri[0]
        POST /addDevice
        POST /addUser
        POST /addBuilding
        POST /addService
        POST /addFireFighter
        Body: JSON with new <>(s) data
        """

        try:
            if len(uri) == 1:
                endpointName = uri[0]
                if endpointName == "addDevice":
                
                    bodyNewDevice = cherrypy.request.body.read()

                    # check if the body is valid
                    if not bodyNewDevice:
                        raise cherrypy.HTTPError(400, "Bad Request: Empty body.")
                    
                    try:
                        bodyNewDevice = json.loads(bodyNewDevice)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")
                
                    # check if the device already exists
                    newID = bodyNewDevice["clientID"]
                    existing_device, _ = self._find_item("devicesList", "clientID", newID)
                    if existing_device:
                        raise cherrypy.HTTPError(409, "ClientID given already exists.")
                        
                    # if here, device is new
                    bodyNewDevice["lastUpdate"] = time.time()
                    self.catalogData["devicesList"].append(bodyNewDevice)
                    self._save()
                    return json.dumps({"status": "created", "data": self.catalogData})
            
                elif endpointName == "addUser":

                    bodyNewUser = cherrypy.request.body.read()

                    # check if the body is valid
                    if not bodyNewUser:
                        raise cherrypy.HTTPError(400, "Bad Request: Empty body.")
                    
                    try:
                        bodyNewUser = json.loads(bodyNewUser)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")
                
                    # check if the user already exists
                    newID = bodyNewUser["userID"]
                    existing_user, _ = self._find_item("usersList", "userID", newID)
                    if existing_user:
                        raise cherrypy.HTTPError(409, "UserID given already exists.")
                        
                    # if here, user is new
                    self.catalogData["usersList"].append(bodyNewUser)
                    self._save()
                    return json.dumps({"status": "created", "data": self.catalogData})

                elif endpointName == "addBuilding":

                    bodyNewBuilding = cherrypy.request.body.read()

                    # check if the body is valid
                    if not bodyNewBuilding:
                        raise cherrypy.HTTPError(400, "Bad Request: Empty body.")
                    
                    try:
                        bodyNewBuilding = json.loads(bodyNewBuilding)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")
                
                    # check if the building already exists
                    newID = bodyNewBuilding["buildingID"]
                    existing_building, _ = self._find_item("buildingList", "buildingID", newID)
                    if existing_building:
                        raise cherrypy.HTTPError(409, "BuildingID given already exists.")
                        
                    # if here, building is new
                    self.catalogData["buildingList"].append(bodyNewBuilding)
                    self._save()
                    return json.dumps({"status": "created", "data": self.catalogData})
                
                elif endpointName == "addService":

                    bodyNewService = cherrypy.request.body.read()

                    # check if the body is valid
                    if not bodyNewService:
                        raise cherrypy.HTTPError(400, "Bad Request: Empty body.")
                    
                    try:
                        bodyNewService = json.loads(bodyNewService)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")
                
                    # check if the service already exists
                    newID = bodyNewService["clientID"]
                    existing_service, _ = self._find_item("servicesList", "clientID", newID)
                    if existing_service:
                        raise cherrypy.HTTPError(409, "ClientID given already exists.")
                        
                    # if here, service is new
                    if "extra" not in bodyNewService:
                        bodyNewService["extra"] = {}
                    bodyNewService["lastUpdate"] = time.time()
                    self.catalogData["servicesList"].append(bodyNewService)
                    self._save()
                    return json.dumps({"status": "created", "data": self.catalogData})
                
                elif endpointName == "addFireFighter":

                    bodyNewFireFighter = cherrypy.request.body.read()

                    # check if the body is valid
                    if not bodyNewFireFighter:
                        raise cherrypy.HTTPError(400, "Bad Request: Empty body.")
                    
                    try:
                        bodyNewFireFighter = json.loads(bodyNewFireFighter)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")
                
                    # check if the fire fighter already exists
                    newID = bodyNewFireFighter["fireFighterID"]
                    existing_fireFighter, _ = self._find_item("fireFightersList", "fireFighterID", newID)
                    if existing_fireFighter:
                        raise cherrypy.HTTPError(409, "Conflict: fireFighterID given already exists.")
                        
                    # if here, fire fighter is new
                    self.catalogData["fireFightersList"].append(bodyNewFireFighter)
                    self._save()
                    return json.dumps({"status": "created", "data": self.catalogData})

            # in case endpoint != addDevice
            else:
                raise cherrypy.HTTPError(400, "Bad Request: Unknown endpoint.")
        
        except Exception as e:
            raise cherrypy.HTTPError(500, f"Internal Server Error: {e}")

    def DELETE(self, *uri, **params):
        """
                uri[0]         uri[1]
        DELETE /deleteDevice/<clientID>
        DELETE /deleteUser/<userID>
        DELETE /deleteBuilding/<buildingID>
        DELETE /deleteService/<clientID>
        DELETE /deleteFireFighter/<fireFighterID>
        """
        try:
            if len(uri) == 2:

                endpointName = uri[0]
                targetID = uri[1]
                item = None
                index = None

                if endpointName == "deleteDevice":
                    item, index = self._find_item("devicesList", "clientID", targetID)
                    if item:
                        del self.catalogData["devicesList"][index]

                elif endpointName == "deleteUser":
                    item, index = self._find_item("usersList", "userID", targetID)
                    if item:
                        del self.catalogData["usersList"][index]
                
                elif endpointName == "deleteBuilding":
                    item, index = self._find_item("buildingList", "buildingID", targetID)
                    if item:
                        del self.catalogData["buildingList"][index]
                
                elif endpointName == "deleteService":
                    item, index = self._find_item("servicesList", "clientID", targetID)
                    if item:
                        del self.catalogData["servicesList"][index]
                
                elif endpointName == "deleteFireFighter":
                    item, index = self._find_item("fireFightersList", "fireFighterID", targetID)
                    if item:
                        del self.catalogData["fireFightersList"][index]

                if item:
                    self._save()
                    # returns the updated catalog
                    return json.dumps({"status": "deleted", "data": self.catalogData})
                else:
                    raise cherrypy.HTTPError(404, "ClientID not found in the catalog.")

            else:
                raise cherrypy.HTTPError(400, "Bad Request: Unknown endpoint.")
        
        except Exception as e:
            raise cherrypy.HTTPError(500, f"Internal Server Error: {e}")


    def serviceRunTime(self) -> None:
        self.serviceRunTimeStatus = True
        self.updateLoopStart()

    def killServiceRunTime(self) -> None:
        self.serviceRunTimeStatus = False
        return super().killServiceRunTime() 

if __name__ == "__main__":

    # TODO
    configFilePath = "" # HERE PUT THE YAML CONFIG FILE PATH

    service = JSONCatalogProviderService(configFilePath)

    print("Starting service")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping service")
        service.killServiceRunTime()
        print("Service stopped")

