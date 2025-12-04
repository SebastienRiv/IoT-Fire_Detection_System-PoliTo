from src.DevicesConnectors.SensorsSimulation.ModelSensorSimulation import ModelSensorSimulation

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime

class TVOCSensorSimulation(ModelSensorSimulation) :
    
    def __init__(self, DataSetFilePath:str, initialValue:float = 0.0) -> None :
        super().__init__(DataSetFilePath)
        
        self.currentValue = initialValue
        self.dataMinTime = None
        self.trainModel()
        
    def getValue(self) -> dict:
        return { "n" : "TVOC", "u": "ppb", "v" : self.currentValue, "t" : self.lastUpdateTime }
    
    def trainModel(self) -> None :
        data = pd.read_csv(self.dataSetFilePath)

        data['created_at'] = pd.to_datetime(data['created_at'])
        data['Seconds'] = (data['created_at'] - data['created_at'].min()).dt.total_seconds()
        
        self.dataMinTime = pd.to_datetime(data['created_at']).min().tz_localize(None)
        
        tvocValue = data['field6'].values.astype(float)
        timeValue = data['Seconds'].values.astype(float).reshape(-1, 1)

        periodeDay = 24 * 3600
        omegaDay = 2 * np.pi / periodeDay

        XsinDay = np.sin(omegaDay * timeValue)
        XcosDay = np.cos(omegaDay * timeValue)
        

        np.random.seed(42)
        noise = np.random.normal(0, 1, size=timeValue.shape)

        X = np.hstack((XsinDay, XcosDay, noise))
        
        self.model = LinearRegression()
        self.model.fit(X, tvocValue + noise.flatten())
        
    def updateValue(self, context=None) -> None :
        now = datetime.now()
        if self.dataMinTime is None:
            raise ValueError("Le modèle n'est pas entraîné : dataMinTime non défini.")
        secondsNow = (now - self.dataMinTime).total_seconds()

        periode_jour = 24 * 3600
        omega_jour = 2 * np.pi / periode_jour

        Xsin_jour = np.sin(omega_jour * secondsNow)
        Xcos_jour = np.cos(omega_jour * secondsNow)

        # Bruit pour la prédiction instantanée
        bruit = np.random.normal(0, 1)
        XNow = np.array([[Xsin_jour, Xcos_jour, bruit]])

        # Prédire TVOC
        if self.model is None:
            raise ValueError("Le modèle n'est pas entraîné.")
        self.currentValue = self.model.predict(XNow)[0]
        self.lastUpdateTime = int(now.timestamp())