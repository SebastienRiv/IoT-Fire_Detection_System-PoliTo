from src.Services.REST.RESTServices.InferenceService import InferenceService
from src.libs.REST.RequestREST import RequestREST

import joblib
import numpy as np
import pandas as pd
import time
import threading
import cherrypy
import json

class FireDetectionInferenceService(InferenceService):
    
    def __init__(self, configFilePath: str, modelPath: str) -> None:
        super().__init__(configFilePath, modelPath) 

        self.timeSeriesURL = self.configCatalog.get.extra.get("TimeSeriesURL", self.configLocal.get("TimeSeriesURL", "None"))

        self.requestRESTTimeSeries = RequestREST(self.timeSeriesURL)
        
        # Load model files
        self.model = joblib.load(f"{self.modelPath}/modele_incendie.pkl")
        self.scaler = joblib.load(f"{self.modelPath}/scaler_incendie.pkl")
        self.weights = joblib.load(f"{self.modelPath}/weights.pkl")
        self.baselineStats = joblib.load(f"{self.modelPath}/baseline_stats.pkl")
        self.calibration = joblib.load(f"{self.modelPath}/score_calibration.pkl")
        
        # Historical data for smoothing
        self.normData = {
            'smoke': [],
            'co': [],
            'tvoc': [],
            'temperature': []
        }
        self.normLock = threading.Lock()
        self.runtimeThread = None
        
    def getTimeSeriesURL(self) -> str: 
        return self.timeSeriesURL
    
    def POST(self, *uri, **params):
        if len(uri) > 0 and uri[0] == "fireDetection":
            bodyJson = json.loads(cherrypy.request.body.read())
            result = self.infer(bodyJson)
            return json.dumps(result)
        else:
            raise cherrypy.HTTPError(404, "Unknown POST request")
    
    def getNormData(self) -> dict:
        resource = "readData"
        normSize = self.configLocal.get("NormSize", 100)
        params = {"size": normSize}
        
        rep = self.requestRESTTimeSeries.GET(resource, params)
        return rep
    
    def updateNormData(self) -> None:
        response = self.getNormData()

        # Check if response contains the expected 'sensors' dictionary
        if not response or 'sensors' not in response:
            print("[FireDetectionInference] No valid sensor data received.")
            return

        sensors_data = response['sensors']

        with self.normLock:
            # directly replace internal buffers with the fetched lists
            # using .get() to handle potential capitalization differences (e.g. 'Smoke' vs 'smoke')
            self.normData['smoke'] = sensors_data.get('smoke', sensors_data.get('Smoke', []))
            self.normData['co'] = sensors_data.get('co', sensors_data.get('CO', []))
            self.normData['tvoc'] = sensors_data.get('tvoc', sensors_data.get('TVOC', []))
            self.normData['temperature'] = sensors_data.get('temperature', sensors_data.get('Temperature', []))

        # Log update status
        sample_count = len(self.normData['smoke'])
        if sample_count > 0:
            print(f"[FireDetectionInference] Normalization buffer updated with {sample_count} samples.")
        else:
            print("[FireDetectionInference] Warning: Received empty sensor buffers.")
    
    def getSmoothedValues(self, smoke, co, tvoc, temp) -> tuple:
        with self.normLock:
            hasHistory = len(self.normData['smoke']) >= 10
            
            if not hasHistory:
                return smoke, co, tvoc, temp
            
            smokeHist = self.normData['smoke'] + [smoke]
            coHist = self.normData['co'] + [co]
            tvocHist = self.normData['tvoc'] + [tvoc]
            tempHist = self.normData['temperature'] + [temp]
        
        normSize = self.configLocal.get("NormSize", 100)
        smokeSmooth = np.mean(smokeHist[-normSize:])
        coSmooth = np.mean(coHist[-normSize:])
        tvocSmooth = np.mean(tvocHist[-normSize:])
        tempSmooth = np.mean(tempHist[-normSize:])
        
        return smokeSmooth, coSmooth, tvocSmooth, tempSmooth
    
    def infer(self, inputData: dict) -> dict:
        smoke = float(inputData.get('smoke', 0))
        co = float(inputData.get('co', 0))
        tvoc = float(inputData.get('tvoc', 0))
        temp = float(inputData.get('temperature', 0))
        
        smokeS, coS, tvocS, tempS = self.getSmoothedValues(smoke, co, tvoc, temp)
        
        # Compute deviations
        deviations = {
            'smoke': (smokeS - self.baselineStats['smoke']['mean']) / self.baselineStats['smoke']['std'],
            'co': (coS - self.baselineStats['co']['mean']) / self.baselineStats['co']['std'],
            'tvoc': (tvocS - self.baselineStats['tvoc']['mean']) / self.baselineStats['tvoc']['std'],
            'temperature': (tempS - self.baselineStats['temperature']['mean']) / self.baselineStats['temperature']['std']
        }
        
        # Weighted input
        weightedInput = np.array([[
            smokeS * self.weights['smoke'],
            coS * self.weights['co'],
            tvocS * self.weights['tvoc'],
            tempS * self.weights['temperature']
        ]])
        inputDf = pd.DataFrame(weightedInput, columns=['smoke', 'co', 'tvoc', 'temperature'])
        inputScaled = self.scaler.transform(inputDf)
        
        # Anomaly score to probability
        anomalyScore = self.model.decision_function(inputScaled)[0]
        relativeScore = (anomalyScore - self.calibration['threshold']) / self.calibration['std']
        fireProb = 1 / (1 + np.exp(relativeScore * 1.5))
        
        # Boost for high deviations
        highDevCount = sum(1 for d in deviations.values() if d > 3)
        if highDevCount >= 1:
            fireProb = min(0.99, fireProb + 0.2 * highDevCount)
        
        weightedDev = sum(max(0, d) * self.weights[s] for s, d in deviations.items())
        if weightedDev > 10:
            fireProb = min(0.99, fireProb + weightedDev / 100)
        
        fireProb = float(np.clip(fireProb, 0.01, 0.99))
        
        # Alert level
        if fireProb < 0.20:
            alert = 'NORMAL'
        elif fireProb < 0.40:
            alert = 'WARNING'
        elif fireProb < 0.70:
            alert = 'DANGER'
        else:
            alert = 'CRITICAL'
        
        return {
            'fire_probability': fireProb,
            'alert_level': alert,
            'is_fire': fireProb > 0.5,
            'anomaly_score': float(anomalyScore)
        }
    
    def serviceRunTime(self) -> None:
        self.updateNormData()

        self.serviceRunTimeStatus = True
        self.updateLoopStart()
        
        updateInterval = self.configLocal.get("NormTimeUpdate", 5)
        while True:
            time.sleep(updateInterval)
            self.updateNormData()
    
    def killServiceRunTime(self) -> None:
        super().killServiceRunTime()