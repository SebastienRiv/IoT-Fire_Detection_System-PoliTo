from abc import ABC, abstractmethod
from src.DevicesConnectors.SensorsSimulation.SensorsSimulation import SensorSimulation

class ModelSensorSimulation(SensorSimulation, ABC) :
    """Model sensor simulation class provide the interface for all sensors with ML model
    """
    
    def __init__(self, dataSetFilePath:str) -> None :
        super().__init__()
        
        self.dataSetFilePath = dataSetFilePath
        self.model = None
        
    def getModel(self) :
        return self.model
    
    def getDatasetFilePath(self) -> str :
        return self.dataSetFilePath
    
    def setDatasetFilePath(self, new_dataSetFilePath:str) -> None :
        self.dataSetFilePath = new_dataSetFilePath
    
    @abstractmethod
    def trainModel(self) -> None :
        pass