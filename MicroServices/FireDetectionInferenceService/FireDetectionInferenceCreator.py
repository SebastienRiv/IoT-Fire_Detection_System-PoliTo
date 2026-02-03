import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")

from src.Services.REST.RESTServices.InferenceServices.FireDetectionInferenceService import FireDetectionInferenceService

if __name__  == "__main__" :
    
    service = FireDetectionInferenceService("./MicroServices/FireDetectionInferenceService/configFireDetectionInferenceService.yaml", "./MicroServices/FireDetectionInferenceService/model/")
    
    service.setServiceRunTimeStatus(True)
    service.serviceRunTime()