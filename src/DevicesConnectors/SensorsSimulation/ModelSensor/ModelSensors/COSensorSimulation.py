from src.DevicesConnectors.SensorsSimulation.ModelSensor.ModelSensorSimulation import ModelSensorSimulation

import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from datetime import datetime

class COSensorSimulation(ModelSensorSimulation) :
    
    def __init__(self, DataSetFilePath:str, initialValue:float = 0.0) -> None :
        super().__init__(DataSetFilePath)
        
        self.currentValue = initialValue
        self.dataMinTime = None
        
        # Original data statistics for rescaling
        self.origMin = None
        self.origMax = None
        
        self.trainModel()
        
    def getValue(self) -> dict:
        msg = self.sensML.genSensMLSensorMsg("CO", "ppm", self.currentValue, self.lastUpdateTime)
        return msg
    
    def trainModel(self) -> None :
        data = pd.read_csv(self.dataSetFilePath)
        data['created_at'] = pd.to_datetime(data['created_at'])
        data['Seconds'] = (data['created_at'] - data['created_at'].min()).dt.total_seconds()
        
        self.dataMinTime = pd.to_datetime(data['created_at']).min().tz_localize(None)
        
        # Normalize seconds to one day (modulo 24h)
        secondsInDay = data['Seconds'] % (24 * 3600)
        coValue = data['field1'].values.astype(float)
        
        # Store original data statistics for rescaling
        self.origMin = float(coValue.min())
        self.origMax = float(coValue.max())
        
        # Sort by time of day
        sorted_indices = np.argsort(secondsInDay)
        secondsInDay = secondsInDay[sorted_indices]
        coValue = coValue[sorted_indices]
        
        # Create spline (k=3 for cubic, s for smoothing)
        self.model = UnivariateSpline(secondsInDay, coValue, k=3, s=10)
        
    def updateValue(self, context=None) -> None :
        now = datetime.now()
        secondsInDay = (now.hour * 3600 + now.minute * 60 + now.second)
        
        rawValue = float(self.model(secondsInDay))
        rawValue += np.random.normal(0, 0.5)
        
        # Clip to original data range
        self.currentValue = np.clip(rawValue, self.origMin, self.origMax)
        self.lastUpdateTime = int(now.timestamp())