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
        self.lock = threading.Lock()

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

    # REST methods

    def GET(self, *uri, **params):

        # NOTE: don't know the actual names yet
        """
        GET /getCatalog
        GET /getResourceByID?clientID=<resource_id>
        GET /getUserByID?userID=<user_id>
        GET /getBuildingByID?buildingID=<building_id>
        GET /getBuildingDevices?buildingID=<building_id>
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
                    return json.dumps(self.catalogData)
                
                elif endpointName == "getResourceByID":

                    # check if clientID exists in params (naming mismatch?)
                    if "clientID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'clientID' parameter is missing.")
                    
                    clientID = params["clientID"]

                    # check if ID in devicesList
                    for device in self.catalogData["devicesList"]:
                        if device["clientID"] == clientID:
                            return json.dumps(device)
                    # if it doesnt find any ID matching
                    raise cherrypy.HTTPError(404, "Resource not found.")
                
                elif endpointName == "getUserByID":

                    if "userID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'userID' parameter is missing.")
                    
                    userID = params["userID"]

                    for user in self.catalogData["usersList"]:
                        if user["userID"] == userID:
                            return json.dumps(user)
                    
                    raise cherrypy.HTTPError(404, "User not found.")
                
                elif endpointName == "getBuildingByID":

                    if "buildingID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'buildingID' parameter is missing.")
                    
                    buildingID = params["buildingID"]

                    for building in self.catalogData["buildingList"]:
                        if building["buildingID"] == buildingID:
                            return json.dumps(building)
                    
                    raise cherrypy.HTTPError(404, "Building not found.")

                elif endpointName == "getBuildingDevices":

                    if "buildingID" not in params:
                        raise cherrypy.HTTPError(400, "Bad Request: 'buildingID' parameter is missing.")
                    
                    buildingID = params["buildingID"]

                    devicesInBuilding = []
                    for device in self.catalogData["devicesList"]:
                        if device["buildingID"] == buildingID:
                            devicesInBuilding.append(device)
                    
                    return json.dumps({"buildingID": buildingID, "devices": devicesInBuilding})

                else:
                    raise cherrypy.HTTPError(400, "Bad Request: Unknown endpoint.")

        except Exception as e:
            raise cherrypy.HTTPError(500, f"Internal Server Error: {e}")

    # PUT method updates the catalog
    def PUT(self, *uri, **params):

        # NOTE: don't know the actual names yet
        """
            uri[0]         uri[1]
        PUT /updateDevice/<clientID>
        PU /updateUser/<userID>
        PUT /updateBuilding/<buildingID>
        Body: JSON with new catalog data
        """

        try:
            if len(uri) == 2:
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

                    
                    found = False

                    for device in self.catalogData["devicesList"]:
                        if device["clientID"] == targetID:
                            found = True

                            # update the device info
                            for key, value in bodyUpdatedDevice.items():
                                if key in device:
                                    device[key] = value
                            # update timestamp
                            device["lastUpdate"] = time.time()
                                    
                            break
                    
                    if found:
                        self._save()
                        # in this case I think it's better to return the catalog since it might need to update the page
                        return json.dumps({"status": "updated", "catalog": self.catalogData})

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

                    found = False

                    for user in self.catalogData["usersList"]:
                        if user["userID"] == targetID:
                            found = True

                            # update the user info
                            for key, value in bodyUpdatedUser.items():
                                if key in user:
                                    user[key] = value
                                    
                            break
                    
                    if found:
                        self._save()
                        return json.dumps({"status": "updated", "catalog": self.catalogData})

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

                    found = False

                    for building in self.catalogData["buildingList"]:
                        if building["buildingID"] == targetID:
                            found = True

                            # update the building info
                            for key, value in bodyUpdatedBuilding.items():
                                if key in building:
                                    building[key] = value
                                    
                            break
                    
                    if found:
                        self._save()
                        return json.dumps({"status": "updated", "catalog": self.catalogData})

                    else:
                        raise cherrypy.HTTPError(404, "BuildingID not found in the catalog.")
                
                else:
                    raise cherrypy.HTTPError(400,"The URL should be <url>/updateDevice/<deviceID>")
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
                    for device in self.catalogData["devicesList"]:
                        if device["clientID"] == newID:
                            raise cherrypy.HTTPError(409, "Conflict: clientID given already exists.")
                        
                    # if here, device is new
                    bodyNewDevice["lastUpdate"] = time.time()
                    self.catalogData["devicesList"].append(bodyNewDevice)
                    self._save()
                    return json.dumps({"status": "Created", "catalog": self.catalogData})
            
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
                    for user in self.catalogData["usersList"]:
                        if user["userID"] == newID:
                            raise cherrypy.HTTPError(409, "Conflict: userID given already exists.")
                        
                    # if here, user is new
                    self.catalogData["usersList"].append(bodyNewUser)
                    self._save()
                    return json.dumps({"status": "Created", "catalog": self.catalogData})

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
                    for building in self.catalogData["buildingList"]:
                        if building["buildingID"] == newID:
                            raise cherrypy.HTTPError(409, "Conflict: buildingID given already exists.")
                        
                    # if here, building is new
                    self.catalogData["buildingList"].append(bodyNewBuilding)
                    self._save()
                    return json.dumps({"status": "Created", "catalog": self.catalogData})

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
        """
        try:
            if len(uri) == 2:

                endpointName = uri[0]
                targetID = uri[1]
                found = False

                if endpointName == "deleteDevice":
                    for index, device in enumerate(self.catalogData["devicesList"]):
                        if device["clientID"] == targetID:
                            found = True
                            del self.catalogData["devicesList"][index]
                            break

                if endpointName == "deleteUser":
                    for index, user in enumerate(self.catalogData["usersList"]):
                        if user["userID"] == targetID:
                            found = True
                            del self.catalogData["usersList"][index]
                            break
                if endpointName == "deleteBuilding":
                    for index, building in enumerate(self.catalogData["buildingList"]):
                        if building["buildingID"] == targetID:
                            found = True
                            del self.catalogData["buildingList"][index]
                            break

                if found:
                    self._save()
                    # returns the updated catalog
                    return json.dumps({"status": "Deleted", "catalog": self.catalogData})
                else:
                    raise cherrypy.HTTPError(404, "ClientID not found in the catalog.")

            else:
                raise cherrypy.HTTPError(400, "Bad Request: Unknown endpoint.")
        
        except Exception as e:
            raise cherrypy.HTTPError(500, f"Internal Server Error: {e}")


    # NOTE: ARE THESE METHODS NEEDED IN THIS SERVICE?    
    # def serviceRunTime(self) -> None:
    #     pass

    # def killServiceRunTime(self) -> None:
    #     return super().killServiceRunTime() 
