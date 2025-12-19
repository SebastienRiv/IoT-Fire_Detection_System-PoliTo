from src.Services.REST.RESTServices.InferenceService import InferenceService

class FireDetectionInferenceService(InferenceService):
    
    def __init__(self, configFilePath:str, dataPath:str) -> None :
        super().__init__(configFilePath, dataPath)
        
    def GET(self, *uri, **params):
        pass
    
    def POST(self, *uri, **params):
        pass
    
    def trainModel(self) :
        pass
    
    def infer(self, inputData) :
        pass 
    
    def serviceRunTime(self) -> None :
        pass
    
    def killServiceRunTime(self) -> None:
        super().killServiceRunTime()