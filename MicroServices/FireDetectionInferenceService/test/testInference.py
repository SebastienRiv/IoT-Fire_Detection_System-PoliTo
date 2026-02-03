import sys
sys.path.append("c:/Users/sebas/Desktop/Travail/E5/Programming for IoT applications/Project/github/IoT-Fire_Detection_System-PoliTo")

import joblib
import numpy as np
import pandas as pd
import os

# Chemin vers les fichiers du modèle
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "..", "model")

# Charger les fichiers
print("Loading model files...")
model = joblib.load(f"{MODEL_PATH}/modele_incendie.pkl")
scaler = joblib.load(f"{MODEL_PATH}/scaler_incendie.pkl")
weights = joblib.load(f"{MODEL_PATH}/weights.pkl")
baselineStats = joblib.load(f"{MODEL_PATH}/baseline_stats.pkl")
calibration = joblib.load(f"{MODEL_PATH}/score_calibration.pkl")
print("Model loaded successfully!\n")

def infer(smoke, co, tvoc, temp):
    """Test inference function"""
    deviations = {
        'smoke': (smoke - baselineStats['smoke']['mean']) / baselineStats['smoke']['std'],
        'co': (co - baselineStats['co']['mean']) / baselineStats['co']['std'],
        'tvoc': (tvoc - baselineStats['tvoc']['mean']) / baselineStats['tvoc']['std'],
        'temperature': (temp - baselineStats['temperature']['mean']) / baselineStats['temperature']['std']
    }
    
    weightedInput = np.array([[
        smoke * weights['smoke'],
        co * weights['co'],
        tvoc * weights['tvoc'],
        temp * weights['temperature']
    ]])
    inputDf = pd.DataFrame(weightedInput, columns=['smoke', 'co', 'tvoc', 'temperature'])
    inputScaled = scaler.transform(inputDf)
    
    anomalyScore = model.decision_function(inputScaled)[0]
    relativeScore = (anomalyScore - calibration['threshold']) / calibration['std']
    fireProb = 1 / (1 + np.exp(relativeScore * 1.5))
    
    highDevCount = sum(1 for d in deviations.values() if d > 3)
    if highDevCount >= 1:
        fireProb = min(0.99, fireProb + 0.2 * highDevCount)
    
    weightedDev = sum(max(0, d) * weights[s] for s, d in deviations.items())
    if weightedDev > 10:
        fireProb = min(0.99, fireProb + weightedDev / 100)
    
    fireProb = float(np.clip(fireProb, 0.01, 0.99))
    
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
        'is_fire': fireProb > 0.5
    }


# ============================================
# TESTS
# ============================================

print("=" * 50)
print("TEST 1: Normal values (should be NORMAL)")
print("=" * 50)
result = infer(smoke=0.02, co=187, tvoc=38, temp=14)
print(f"  Probability: {result['fire_probability']:.1%}")
print(f"  Alert: {result['alert_level']}")
print(f"  Is Fire: {result['is_fire']}")
assert result['alert_level'] == 'NORMAL', "FAILED: Should be NORMAL"
print("  -> PASSED\n")


print("=" * 50)
print("TEST 2: Smoke elevated (+3 std)")
print("=" * 50)
smokeHigh = baselineStats['smoke']['mean'] + 3 * baselineStats['smoke']['std']
result = infer(smoke=smokeHigh, co=187, tvoc=38, temp=14)
print(f"  Smoke value: {smokeHigh:.3f}")
print(f"  Probability: {result['fire_probability']:.1%}")
print(f"  Alert: {result['alert_level']}")
print(f"  Is Fire: {result['is_fire']}")
assert result['fire_probability'] > 0.3, "FAILED: Probability should be elevated"
print("  -> PASSED\n")


print("=" * 50)
print("TEST 3: Multiple sensors elevated (+4 std) - FIRE")
print("=" * 50)
smokeHigh = baselineStats['smoke']['mean'] + 4 * baselineStats['smoke']['std']
coHigh = baselineStats['co']['mean'] + 4 * baselineStats['co']['std']
tvocHigh = baselineStats['tvoc']['mean'] + 4 * baselineStats['tvoc']['std']
tempHigh = baselineStats['temperature']['mean'] + 4 * baselineStats['temperature']['std']
result = infer(smoke=smokeHigh, co=coHigh, tvoc=tvocHigh, temp=tempHigh)
print(f"  Probability: {result['fire_probability']:.1%}")
print(f"  Alert: {result['alert_level']}")
print(f"  Is Fire: {result['is_fire']}")
assert result['is_fire'] == True, "FAILED: Should detect fire"
assert result['alert_level'] in ['DANGER', 'CRITICAL'], "FAILED: Should be DANGER or CRITICAL"
print("  -> PASSED\n")


print("=" * 50)
print("TEST 4: Critical fire scenario (+6 std on all)")
print("=" * 50)
smokeHigh = baselineStats['smoke']['mean'] + 6 * baselineStats['smoke']['std']
coHigh = baselineStats['co']['mean'] + 6 * baselineStats['co']['std']
tvocHigh = baselineStats['tvoc']['mean'] + 6 * baselineStats['tvoc']['std']
tempHigh = baselineStats['temperature']['mean'] + 6 * baselineStats['temperature']['std']
result = infer(smoke=smokeHigh, co=coHigh, tvoc=tvocHigh, temp=tempHigh)
print(f"  Probability: {result['fire_probability']:.1%}")
print(f"  Alert: {result['alert_level']}")
print(f"  Is Fire: {result['is_fire']}")
assert result['alert_level'] == 'CRITICAL', "FAILED: Should be CRITICAL"
print("  -> PASSED\n")


print("=" * 50)
print("TEST 5: Only temperature high (not enough for fire)")
print("=" * 50)
tempHigh = baselineStats['temperature']['mean'] + 3 * baselineStats['temperature']['std']
result = infer(smoke=0.02, co=187, tvoc=38, temp=tempHigh)
print(f"  Temperature: {tempHigh:.1f}")
print(f"  Probability: {result['fire_probability']:.1%}")
print(f"  Alert: {result['alert_level']}")
print("  -> INFO (single sensor might not trigger fire)\n")


print("=" * 50)
print("ALL TESTS PASSED!")
print("=" * 50)
