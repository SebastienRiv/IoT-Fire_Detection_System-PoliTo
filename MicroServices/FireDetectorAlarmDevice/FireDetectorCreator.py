import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")

from src.DevicesConnectors.Device.Devices.FireDetectorDevice import FireDetectorDevice
from src.DevicesConnectors.SensorsSimulation.ModelSensor.ModelSensors.TemperatureSensorSimulation import TemperatureSensorSimulation
from src.DevicesConnectors.SensorsSimulation.ModelSensor.ModelSensors.COSensorSimulation import COSensorSimulation
from src.DevicesConnectors.SensorsSimulation.ModelSensor.ModelSensors.TVOCSensorSimulation import TVOCSensorSimulation
from src.DevicesConnectors.SensorsSimulation.Sensors.SmokeSensorSimulation import SmokeSensorSimulation

if __name__ == "__main__" :
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    sensorCO = COSensorSimulation(os.path.join(base_path, "data_set/indoor_data.csv"))
    sensorTemp = TemperatureSensorSimulation(os.path.join(base_path, "data_set/OFFC_EMY.csv"))
    sensorTVOC = TVOCSensorSimulation(os.path.join(base_path, "data_set/indoor_data.csv"))
    sensorSmoke = SmokeSensorSimulation()
    
    sensorsArray = [ sensorTemp, sensorTVOC, sensorCO, sensorSmoke ]
    
    device = FireDetectorDevice(os.path.join(base_path, "configFireDetectorDevice.yaml"), sensorsArray)
    
    device.setDeviceRunTimeStatus(True)
    device.deviceRunTime()