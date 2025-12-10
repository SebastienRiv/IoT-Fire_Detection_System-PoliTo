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
        """
        #                        uri[0]
        # if len(uri) == 0 --> /
        # if len(uri) > 0 --> /<something>

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
        Body: JSON with new catalog data
        """

        try:
            if len(uri) == 2:
                endpointName = uri[0]

                # check if the endpoint is correct
                if endpointName == "updateDevice":

                    clientID = uri[1]

                    bodyUpdatedDevice = cherrypy.request.body.read()

                    try:
                        bodyUpdatedDevice = json.loads(bodyUpdatedDevice)
                    except json.JSONDecodeError:
                        raise cherrypy.HTTPError(400, "Bad Request: Invalid JSON in the body.")

                    if bodyUpdatedDevice["clientID"] != clientID:
                        raise cherrypy.HTTPError(400, "DeviceID in the URI does not match the one in the body")

                    
                    found = False

                    for device in self.catalogData["devicesList"]:
                        if device["clientID"] == clientID:
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
                        return json.dumps(self.catalogData)

                    else:
                        raise cherrypy.HTTPError(404, "ClientID not found in the catalog.")
                
                else:
                    raise cherrypy.HTTPError(400,"The URL should be <url>/updateDevice/<deviceID>")
            else:
                raise cherrypy.HTTPError(400, "Bad Request")

        except Exception as e:
            raise cherrypy.HTTPError(500, f"Internal Server Error: {e}")
        
    def POST(self, *uri, **params):
        """
        POST /addDevice
        Body: JSON with new device(s) data
        """

        # TODO: continue
        pass

    def DELETE(self, *uri, **params):
        """
        DELETE /deleteDevice/<clientID>
        """

        # TODO: continue
        pass
