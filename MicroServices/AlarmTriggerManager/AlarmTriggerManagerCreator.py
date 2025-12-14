from AlarmTriggerManager import AlarmTriggerManager
if __name__=="__main__":
    alarmTriggerManager=AlarmTriggerManager("configAlarmTriggerManager.yaml")
    alarmTriggerManager.setRunTimeStatus(True)
    alarmTriggerManager.RunTime()