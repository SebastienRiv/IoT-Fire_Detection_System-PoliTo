import sys
import os

# Change the working directory to the project root
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.DevicesConnectors.Device.Devices.FireDetectorDevice import FireDetectorDevice
from src.DevicesConnectors.SensorsSimulation.ModelSensor.ModelSensors.TemperatureSensorSimulation import TemperatureSensorSimulation
from src.DevicesConnectors.SensorsSimulation.ModelSensor.ModelSensors.COSensorSimulation import COSensorSimulation
from src.DevicesConnectors.SensorsSimulation.ModelSensor.ModelSensors.TVOCSensorSimulation import TVOCSensorSimulation
from src.DevicesConnectors.SensorsSimulation.Sensors.SmokeSensorSimulation import SmokeSensorSimulation

if __name__ == "__main__":
    # Use the project root to construct file paths
    data_set_path = os.path.join(os.getcwd(), "MicroServices/FireDetectorAlarmDevice/data_set")
    config_path = os.path.join(os.getcwd(), "MicroServices/FireDetectorAlarmDevice/configFireDetectorDevice.yaml")

    sensorCO = COSensorSimulation(os.path.join(data_set_path, "indoor_data.csv"))
    sensorTemp = TemperatureSensorSimulation(os.path.join(data_set_path, "OFFC_EMY.csv"))
    sensorTVOC = TVOCSensorSimulation(os.path.join(data_set_path, "indoor_data.csv"))
    sensorSmoke = SmokeSensorSimulation()

    sensorsArray = [sensorTemp, sensorTVOC, sensorCO, sensorSmoke]

    device = FireDetectorDevice(config_path, sensorsArray)

    device.setDeviceRunTimeStatus(True)
    device.deviceRunTime()