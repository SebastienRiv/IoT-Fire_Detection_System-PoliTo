import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime

class SensorSimulation :
    """Sensors simulation class provide the interface for all sensors
    """
    
    def __init__(self) -> None :
        self.currentValue = None
        self.lastUpdateTime = None
    
    def getValue(self) -> dict :
        return { "n" : "Unknown", "u": "Unknown", "v" : self.currentValue, "t" : self.lastUpdateTime } 
    
    def updateValue(self, context=None) -> None :
        pass
    