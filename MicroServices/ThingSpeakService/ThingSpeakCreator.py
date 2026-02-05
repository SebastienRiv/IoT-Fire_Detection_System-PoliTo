import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")

from src.Services.Hybrid.RESTandMQTTServices.TimeSerieServices.ThingSpeakService import ThingspeakService

if __name__ == "__main__" :
    thingSpeakService = ThingspeakService("./MicroServices/ThingSpeakService/configThingSpeakService.yaml", "./MicroServices/ThingSpeakService/.env")
    
    thingSpeakService.setServiceRunTimeStatus(True)
    thingSpeakService.serviceRunTime()