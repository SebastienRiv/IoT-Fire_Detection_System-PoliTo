import requests
import json
import time

# Configuration du test
THINGSPEAK_SERVICE_URL = "http://localhost:8083"

def testReadData():
    """Test GET /readData - Récupère les données depuis Thingspeak"""
    print("\n" + "="*50)
    print("TEST: GET /readData")
    print("="*50)
    
    # Test pour chaque field (1=Smoke, 2=TVOC, 3=Temperature, 4=CO2)
    fields = {1: "Smoke", 2: "TVOC", 3: "Temperature", 4: "CO2"}
    
    for fieldNumber, fieldName in fields.items():
        url = f"{THINGSPEAK_SERVICE_URL}/readData"
        params = {
            "fieldNumber": fieldNumber,
            "size": 10  # Récupère les 10 dernières valeurs
        }
        
        print(f"\n[{fieldName}] GET {url}?fieldNumber={fieldNumber}&size=10")
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Status: {response.status_code}")
            
            if "feeds" in data:
                feeds = data["feeds"]
                print(f"  ✓ Nombre de valeurs: {len(feeds)}")
                
                if len(feeds) > 0:
                    lastFeed = feeds[-1]
                    fieldKey = f"field{fieldNumber}"
                    lastValue = lastFeed.get(fieldKey, "N/A")
                    lastTime = lastFeed.get("created_at", "N/A")
                    print(f"  ✓ Dernière valeur: {lastValue} ({lastTime})")
            else:
                print(f"  ! Réponse inattendue: {data}")
        else:
            print(f"  ✗ Erreur: {response.status_code}")
            print(f"    {response.text}")

def testDirectThingspeak():
    """Test direct vers Thingspeak pour vérifier la connectivité"""
    print("\n" + "="*50)
    print("TEST: Connexion directe Thingspeak")
    print("="*50)
    
    channelId = "3249207"  # Depuis ton config
    url = f"https://api.thingspeak.com/channels/{channelId}/feeds.json?results=2"
    
    print(f"\nGET {url}")
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ Connexion OK")
        print(f"  ✓ Channel: {data.get('channel', {}).get('name', 'N/A')}")
        print(f"  ✓ Feeds: {len(data.get('feeds', []))}")
    else:
        print(f"  ✗ Erreur: {response.status_code}")

def testServiceHealth():
    """Vérifie si le service ThingSpeak est accessible"""
    print("\n" + "="*50)
    print("TEST: Service Health Check")
    print("="*50)
    
    try:
        response = requests.get(THINGSPEAK_SERVICE_URL, timeout=5)
        print(f"  ✓ Service accessible sur {THINGSPEAK_SERVICE_URL}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Service non accessible sur {THINGSPEAK_SERVICE_URL}")
        print(f"    → Lance d'abord: python MicroServices/ThingSpeakService/ThingSpeakCreator.py")
        return False
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        return False

def simulateMQTTMessage():
    """Simule ce que ferait un message MQTT (pour debug)"""
    print("\n" + "="*50)
    print("INFO: Format message MQTT attendu (SenML)")
    print("="*50)
    
    sampleMessage = {
        "bn": "FireDetector_001",
        "e": [
            {"n": "Smoke", "v": 0.15, "u": "ppm"},
            {"n": "TVOC", "v": 250, "u": "ppb"},
            {"n": "Temperature", "v": 24.5, "u": "Cel"},
            {"n": "CO2", "v": 450, "u": "ppm"}
        ]
    }
    
    print(f"\nMessage SenML attendu:")
    print(json.dumps(sampleMessage, indent=2))
    print(f"\nCe message sera publié sur le topic MQTT configuré")
    print(f"et uploadé vers Thingspeak automatiquement.")

if __name__ == "__main__":
    print("\n" + "#"*50)
    print("  TEST THINGSPEAK SERVICE")
    print("#"*50)
    
    # Test 1: Connexion directe à Thingspeak
    testDirectThingspeak()
    
    # Test 2: Vérifier si le service local est up
    serviceUp = testServiceHealth()
    
    if serviceUp:
        # Test 3: Tester l'endpoint readData
        testReadData()
    
    # Info: Format message MQTT
    simulateMQTTMessage()
    
    print("\n" + "="*50)
    print("TESTS TERMINÉS")
    print("="*50 + "\n")
