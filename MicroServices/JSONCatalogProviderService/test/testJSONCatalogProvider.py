import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8084"  # Ajustez le port selon votre config

def print_response(response, test_name):
    """Affiche le résultat d'un test de manière formatée"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_get_catalog():
    """Test GET /getCatalog"""
    response = requests.get(f"{BASE_URL}/getCatalog")
    print_response(response, "GET Catalog")
    return response.status_code == 200

def test_add_device():
    """Test POST /addDevice"""
    new_device = {
        "clientID": "test_device_001",
        "deviceName": "Test Fire Detector",
        "measureType": ["temperature", "smoke"],
        "availableResources": ["/temperature", "/smoke"],
        "servicesDetails": [
            {
                "serviceType": "MQTT",
                "serviceIP": "localhost",
                "topic": ["test/sensors/temperature", "test/sensors/smoke"]
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/addDevice",
        data=json.dumps(new_device),
        headers={'Content-Type': 'application/json'}
    )
    print_response(response, "POST Add Device")
    return response.status_code in [200, 201]

def test_get_device_by_id():
    """Test GET /getResourceByID"""
    response = requests.get(
        f"{BASE_URL}/getResourceByID",
        params={"clientID": "test_device_001"}
    )
    print_response(response, "GET Device by ID")
    return response.status_code == 200

def test_update_device():
    """Test PUT /updateDevice/<clientID>"""
    updated_device = {
        "clientID": "test_device_001",
        "deviceName": "Updated Test Fire Detector",
        "measureType": ["temperature", "smoke", "CO"],
        "availableResources": ["/temperature", "/smoke", "/CO"],
        "servicesDetails": [
            {
                "serviceType": "MQTT",
                "serviceIP": "localhost",
                "topic": ["test/sensors/temperature", "test/sensors/smoke", "test/sensors/CO"]
            }
        ]
    }
    
    response = requests.put(
        f"{BASE_URL}/updateDevice/test_device_001",
        data=json.dumps(updated_device),
        headers={'Content-Type': 'application/json'}
    )
    print_response(response, "PUT Update Device")
    return response.status_code == 200

def test_get_device_by_measure():
    """Test GET /getDeviceByMeasure"""
    response = requests.get(
        f"{BASE_URL}/getDeviceByMeasure",
        params={"measure": "temperature"}
    )
    print_response(response, "GET Device by Measure")
    return response.status_code == 200

def test_add_service():
    """Test POST /addService"""
    new_service = {
        "serviceID": "test_service_001",
        "serviceName": "Test Inference Service",
        "serviceType": "REST",
        "serviceIP": "localhost",
        "servicePort": 8082,
        "extra": {
            "threshold": 0.75
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/addService",
        data=json.dumps(new_service),
        headers={'Content-Type': 'application/json'}
    )
    print_response(response, "POST Add Service")
    return response.status_code in [200, 201]

def test_get_service_by_id():
    """Test GET /getServiceByID"""
    response = requests.get(
        f"{BASE_URL}/getServiceByID",
        params={"serviceID": "test_service_001"}
    )
    print_response(response, "GET Service by ID")
    return response.status_code == 200

def test_get_service_threshold():
    """Test GET /getServiceThreshold"""
    response = requests.get(
        f"{BASE_URL}/getServiceThreshold",
        params={"serviceID": "test_service_001"}
    )
    print_response(response, "GET Service Threshold")
    return response.status_code == 200

def test_add_user():
    """Test POST /addUser"""
    new_user = {
        "userID": "test_user_001",
        "name": "Test User",
        "surname": "Tester",
        "email": "test@example.com"
    }
    
    response = requests.post(
        f"{BASE_URL}/addUser",
        data=json.dumps(new_user),
        headers={'Content-Type': 'application/json'}
    )
    print_response(response, "POST Add User")
    return response.status_code in [200, 201]

def test_delete_device():
    """Test DELETE /deleteDevice/<clientID>"""
    response = requests.delete(f"{BASE_URL}/deleteDevice/test_device_001")
    print_response(response, "DELETE Device")
    return response.status_code == 200

def test_delete_service():
    """Test DELETE /deleteService/<serviceID>"""
    response = requests.delete(f"{BASE_URL}/deleteService/test_service_001")
    print_response(response, "DELETE Service")
    return response.status_code == 200

def test_delete_user():
    """Test DELETE /deleteUser/<userID>"""
    response = requests.delete(f"{BASE_URL}/deleteUser/test_user_001")
    print_response(response, "DELETE User")
    return response.status_code == 200

def run_all_tests():
    """Lance tous les tests dans l'ordre"""
    print("\n" + "="*60)
    print("DÉBUT DES TESTS DU SERVICE CATALOG")
    print("="*60)
    
    tests = [
        ("Get Catalog", test_get_catalog),
        ("Add Device", test_add_device),
        ("Get Device by ID", test_get_device_by_id),
        ("Update Device", test_update_device),
        ("Get Device by Measure", test_get_device_by_measure),
        ("Add Service", test_add_service),
        ("Get Service by ID", test_get_service_by_id),
        ("Get Service Threshold", test_get_service_threshold),
        ("Add User", test_add_user),
        ("Delete Device", test_delete_device),
        ("Delete Service", test_delete_service),
        ("Delete User", test_delete_user),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "✅ PASS" if success else "❌ FAIL"))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}\n")
            results.append((test_name, f"❌ ERROR: {str(e)}"))
        
        time.sleep(0.5)  # Pause entre les tests
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    for test_name, result in results:
        print(f"{test_name:.<40} {result}")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("⏳ Attente de 2 secondes pour que le service démarre...")
    time.sleep(2)
    
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {str(e)}")