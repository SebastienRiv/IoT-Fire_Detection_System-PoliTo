from src.DevicesConnectors.SensorsSimulation.ModelSensor.ModelSensorSimulation import ModelSensorSimulation

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime

class TemperatureSensorSimulation(ModelSensorSimulation):
    
    def __init__(self, dataSetFilePath: str, initialValue: float = 20.0) -> None:
        super().__init__(dataSetFilePath)
        
        self.currentValue = initialValue
        self.dataMinTime = None
        
        # Original data statistics for rescaling
        self.origMin = None
        self.origMax = None
        
        # Model output statistics for rescaling
        self.modelMin = None
        self.modelMax = None
        
        self.trainModel()

    def getValue(self) -> dict:        
        msg = self.sensML.genSensMLSensorMsg("Temperature", "°C", self.currentValue, self.lastUpdateTime)
        return msg

    def trainModel(self) -> None:
        data = pd.read_csv(self.dataSetFilePath)
        data['Time'] = pd.to_datetime(data['Time'])
        data['Seconds'] = (data['Time'] - data['Time'].min()).dt.total_seconds()
        self.dataMinTime = pd.to_datetime(data['Time']).min().tz_localize(None)

        temperatureValue = data['Temp'].values.astype(float)
        timeValue = data['Seconds'].values.astype(float).reshape(-1, 1)
        
        # Store original data statistics for rescaling
        self.origMin = float(temperatureValue.min())
        self.origMax = float(temperatureValue.max())

        periodeAnnual = 365 * 24 * 3600
        periodeDaily = 24 * 3600
        omegaAnnual = 2 * np.pi / periodeAnnual
        omegaDaily = 2 * np.pi / periodeDaily

        XsinAnnual = np.sin(omegaAnnual * timeValue)
        XcosAnnual = np.cos(omegaAnnual * timeValue)
        XsinDaily = np.sin(omegaDaily * timeValue)
        XcosDaily = np.cos(omegaDaily * timeValue)

        np.random.seed(42)
        noise = np.random.normal(0, 0.5, size=timeValue.shape)

        X = np.hstack((XsinAnnual, XcosAnnual, XsinDaily, XcosDaily, noise))
        y = temperatureValue + noise.flatten()

        self.model = LinearRegression()
        self.model.fit(X, y)
        
        # Compute model output statistics for rescaling
        predictions = self.model.predict(X)
        self.modelMin = float(predictions.min())
        self.modelMax = float(predictions.max())

    def updateValue(self, context=None) -> None:
        now = datetime.now()
        if self.dataMinTime is None:
            raise ValueError("Model not trained: dataMinTime not defined.")
        secondsNow = (now - self.dataMinTime).total_seconds()

        periodeAnnual = 365 * 24 * 3600
        periodeDaily = 24 * 3600
        omegaAnnual = 2 * np.pi / periodeAnnual
        omegaDaily = 2 * np.pi / periodeDaily

        XsinAnnual = np.sin(omegaAnnual * secondsNow)
        XcosAnnual = np.cos(omegaAnnual * secondsNow)
        XsinDaily = np.sin(omegaDaily * secondsNow)
        XcosDaily = np.cos(omegaDaily * secondsNow)

        noise = np.random.normal(0, 0.5)
        XNow = np.array([[XsinAnnual, XcosAnnual, XsinDaily, XcosDaily, noise]])

        if self.model is None:
            raise ValueError("Model not trained.")
        
        # Get raw model prediction
        rawValue = self.model.predict(XNow)[0]
        
        # Rescale to match original data amplitude
        if self.modelMax != self.modelMin:
            normalizedValue = (rawValue - self.modelMin) / (self.modelMax - self.modelMin)
            self.currentValue = normalizedValue * (self.origMax - self.origMin) + self.origMin
        else:
            self.currentValue = rawValue
            
        self.lastUpdateTime = int(now.timestamp())