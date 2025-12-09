from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime
from src.libs.SensML.SensML import SensML

# NOTE: ABC = Abstract Base Class --> used to define the generic intertface that has to be inherited
class SensorSimulation(ABC):
    """Sensors simulation class provide the interface for all sensors
    """
    
    def __init__(self) -> None :
        self.sensML = SensML()
        
        self.currentValue = None
        self.lastUpdateTime = None
    
    @abstractmethod
    def getValue(self) -> dict :
        msg = self.sensML.genSensMLSensorMsg("Unknown", "Unknown", self.currentValue, self.lastUpdateTime)
        return msg
    
    @abstractmethod
    def updateValue(self, context=None) -> None :
        pass
    