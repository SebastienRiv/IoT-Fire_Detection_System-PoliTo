import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")

from src.DevicesConnectors.Device.Devices.FireButtonAlarmDevice import FireButtonAlarmDevice
from src.DevicesConnectors.SensorsSimulation.Sensors.ButtonSensorSimulation import ButtonSensorSimulation

if __name__  == "__main__" :
    
    sensorButton = ButtonSensorSimulation(initialValue=False)
    sensorsArray = [ sensorButton ]
    
    device = FireButtonAlarmDevice("./MicroServices/FireButtonAlarmDevice/configFireButtonAlarmDevice.yaml", sensorsArray)
    
    device.setDeviceRunTimeStatus(True)
    device.deviceRunTime()