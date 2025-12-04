from src.DevicesConnectors.SensorsSimulation.SensorsSimulation import SensorSimulation
from datetime import datetime

class ButtonSensorSimulation(SensorSimulation) :
    
    def __init__(self, initialValue:bool = False) -> None :
        super().__init__()
        self.currentValue = initialValue
        
    def getValue(self) -> dict:
        return { "n" : "Button", "u": "boolean", "v" : self.currentValue, "t" : self.lastUpdateTime }
    
    def updateValue(self, context=None) -> None :
        now = datetime.now()
        print("Press a to toggle the button state...")
        buttonState = input(">> ")
        if buttonState.lower() == 'a' :
            self.currentValue = not self.currentValue
            self.lastUpdateTime = int(now.timestamp())
        else :
            print("No change to button state.")
        