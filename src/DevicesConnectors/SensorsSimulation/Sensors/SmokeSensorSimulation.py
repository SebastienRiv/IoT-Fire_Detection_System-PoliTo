from src.DevicesConnectors.SensorsSimulation.SensorsSimulation import SensorSimulation
import random
from datetime import datetime

class SmokeSensorSimulation(SensorSimulation) : 
    
    def __init__(self, normalValue=(0, 0.10), eventValue=(1.00, 1.50)) -> None:
        super().__init__()
        self.normalValue = normalValue
        self.eventValue = eventValue
    
    def getValue(self) -> dict:
        return { "n" : "Smoke", "u": "%/ft", "v" : self.currentValue, "t" : self.lastUpdateTime }
    
    def updateValue(self, context=None) -> None:
        now = datetime.now()
        if context and context.get("globalEvent", False):
            self.currentValue = random.uniform(self.eventValue[0], self.eventValue[1]) # Simulate smoke level between eventValue range
        else:
            self.currentValue = random.uniform(self.normalValue[0], self.normalValue[1]) # Simulate smoke level between normalValue range
        self.lastUpdateTime = int(now.timestamp())