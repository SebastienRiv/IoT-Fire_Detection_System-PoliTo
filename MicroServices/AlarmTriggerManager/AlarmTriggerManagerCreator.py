import AlarmTriggerManager
if __name__=="__main__":
    AlarmTriggerManager=AlarmTriggerManager("./MicroServices/AlarmTriggerManager/configAlarmTriggerManager.yaml")
    AlarmTriggerManager.setRunTimeStatus(True)
    AlarmTriggerManager.RunTime()