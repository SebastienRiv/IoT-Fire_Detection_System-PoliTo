from src.Services.REST.RESTService import RESTService
import cherrypy
from abc import abstractmethod, ABC

class InferenceService(RESTService, ABC):
    
    def __init__(self, configFilePath:str, dataPath:str, modelPath:str=None) -> None :
        super().__init__(configFilePath)
        
        self.dataPath = dataPath
        self.modelPath = modelPath
        self.model = None
        
        if modelPath is not None :
            self.loadModel(modelPath)
        else : 
            self.trainModel()
    
    @abstractmethod
    def GET(self, *uri, **params):
        return super().GET(*uri, **params)
    
    @abstractmethod
    def POST(self, *uri, **params):
        return super().POST(*uri, **params)
    
    def PUT(self, *uri, **params):
        raise cherrypy.HTTPError(405, "PUT method not allowed.")
    
    def DELETE(self, *uri, **params):
        raise cherrypy.HTTPError(405, "DELETE method not allowed.")
    
        
    @abstractmethod
    def trainModel(self) :
        pass
    
    @abstractmethod
    def infer(self, inputData) :
        pass
    
    def loadModel(self, modelPath:str) :
        with open(modelPath, 'rb') as f:
            model = f.read() 
        self.model = model
        
        #### To implemente properly model loading depending on model type ####
        pass
    
    def getModel(self) :
        return self.model
    
    def getDataPath(self) :
        return self.dataPath
    
    @abstractmethod
    def serviceRunTime(self) -> None :
        pass
    
    @abstractmethod
    def killServiceRunTime(self) -> None:
        super().killServiceRunTime()