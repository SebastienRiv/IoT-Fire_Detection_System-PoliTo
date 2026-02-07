from src.Services.REST.RESTService import RESTService
import cherrypy
from abc import abstractmethod, ABC

class InferenceService(RESTService, ABC):
    
    def __init__(self, configFilePath:str, modelPath:str="None") -> None :
        super().__init__(configFilePath)
        
        self.modelPath = modelPath
    
    def GET(self, *uri, **params):
        return cherrypy.HTTPError(405, "GET not allowed.")
    
    @abstractmethod
    def POST(self, *uri, **params):
        return super().POST(*uri, **params)
    
    def PUT(self, *uri, **params):
        raise cherrypy.HTTPError(405, "PUT method not allowed.")
    
    def DELETE(self, *uri, **params):
        raise cherrypy.HTTPError(405, "DELETE method not allowed.")
    
    @abstractmethod
    def infer(self, inputData) :
        pass
    
    @abstractmethod
    def serviceRunTime(self) -> None :
        pass
    
    def getModelPath(self) -> str:
        return self.modelPath
    
    @abstractmethod
    def killServiceRunTime(self) -> None:
        super().killServiceRunTime()