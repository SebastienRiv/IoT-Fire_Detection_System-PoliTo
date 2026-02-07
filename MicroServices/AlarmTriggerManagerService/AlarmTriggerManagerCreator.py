import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")

from src.Services.MQTT.MQTTServices.AlarmTriggerManager import AlarmTriggerManager

if __name__=="__main__":
    service = AlarmTriggerManager("./MicroServices/AlarmTriggerManagerService/configAlarmTriggerManagerService.yaml")

    service.setServiceRunTimeStatus(True)
    service.serviceRunTime()