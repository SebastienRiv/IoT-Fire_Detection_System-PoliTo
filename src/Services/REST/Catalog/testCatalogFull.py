import requests
import json
import time
import sys

# CONFIGURATION
BASE_URL = "http://localhost:8080" # Ensure this matches your config.yaml port
HEADERS = {'Content-Type': 'application/json'}

# TEST DATA
TEST_BUILDING = {
    "buildingID": "b_test_01",
    "userID": "u_test_owner",
    "devicesList": [{"clientID": "d_test_01"}] # Reference only
}

TEST_USER = {
    "userID": "u_test_01",
    "userName": "FireChief_Test",
    "chatID": "999888777",
    "building": [{"buildingID": "b_test_01"}]
}

TEST_DEVICE = {
    "clientID": "d_test_01",
    "deviceName": "Sensor_Main_Hall",
    "buildingID": "b_test_01", # Crucial for linking!
    "measureType": ["temperature", "smoke"],
    "availableServices": ["mqtt"],
    "MQTT": {"topicPub": "test/topic"},
    "REST": {"serverHost": "127.0.0.1"}
}

def print_pass(message):
    print(f"✅ PASS: {message}")

def print_fail(message, details=""):
    print(f"❌ FAIL: {message}")
    if details: print(f"   Details: {details}")
    sys.exit(1)

def run_test():
    print("="*50)
    print("STARTING FULL CATALOG SERVICE TEST")
    print("="*50)

    # ---------------------------------------------------------
    # 1. CREATE (POST)
    # ---------------------------------------------------------
    print("\n--- PHASE 1: CREATION (POST) ---")
    
    # 1.1 Add Building
    try:
        res = requests.post(f"{BASE_URL}/addBuilding", headers=HEADERS, data=json.dumps(TEST_BUILDING))
        if res.status_code == 200: print_pass("Building created.")
        else: print_fail("Creating Building", res.text)
    except Exception as e: print_fail("Connection Error", str(e))

    # 1.2 Add User
    res = requests.post(f"{BASE_URL}/addUser", headers=HEADERS, data=json.dumps(TEST_USER))
    if res.status_code == 200: print_pass("User created.")
    else: print_fail("Creating User", res.text)

    # 1.3 Add Device
    res = requests.post(f"{BASE_URL}/addDevice", headers=HEADERS, data=json.dumps(TEST_DEVICE))
    if res.status_code == 200: print_pass("Device created.")
    else: print_fail("Creating Device", res.text)


    # ---------------------------------------------------------
    # 2. READ (GET)
    # ---------------------------------------------------------
    print("\n--- PHASE 2: RETRIEVAL (GET) ---")

    # 2.1 Get Building
    res = requests.get(f"{BASE_URL}/getBuildingByID?buildingID={TEST_BUILDING['buildingID']}")
    if res.status_code == 200 and res.json()['buildingID'] == TEST_BUILDING['buildingID']:
        print_pass("Retrieved Building successfully.")
    else: print_fail("Get Building", res.text)

    # 2.2 Get User
    res = requests.get(f"{BASE_URL}/getUserByID?userID={TEST_USER['userID']}")
    if res.status_code == 200 and res.json()['userName'] == TEST_USER['userName']:
        print_pass("Retrieved User successfully.")
    else: print_fail("Get User", res.text)

    # 2.3 Get Device
    res = requests.get(f"{BASE_URL}/getResourceByID?clientID={TEST_DEVICE['clientID']}")
    if res.status_code == 200 and res.json()['deviceName'] == TEST_DEVICE['deviceName']:
        print_pass("Retrieved Device successfully.")
    else: print_fail("Get Device", res.text)

    # 2.4 Get Building Devices (COMPLEX LOGIC CHECK)
    # This verifies that querying a building returns the devices linked to it via buildingID
    print("   [Testing Link Logic]...")
    res = requests.get(f"{BASE_URL}/getBuildingDevices?buildingID={TEST_BUILDING['buildingID']}")
    data = res.json()
    
    if res.status_code == 200 and len(data['devices']) > 0:
        if data['devices'][0]['clientID'] == TEST_DEVICE['clientID']:
            print_pass("Linked Devices retrieved successfully (Complex Logic Verified).")
        else:
            print_fail("Device list mismatch", f"Expected {TEST_DEVICE['clientID']}, got {data['devices']}")
    else:
        print_fail("Get Building Devices failed", res.text)


    # ---------------------------------------------------------
    # 3. UPDATE (PUT)
    # ---------------------------------------------------------
    print("\n--- PHASE 3: UPDATE (PUT) ---")

    # 3.1 Update Device
    update_payload = {"deviceName": "Sensor_Main_Hall_UPDATED"}
    res = requests.put(f"{BASE_URL}/updateDevice/{TEST_DEVICE['clientID']}", headers=HEADERS, data=json.dumps(update_payload))
    if res.status_code == 200:
        # Verify update
        check = requests.get(f"{BASE_URL}/getResourceByID?clientID={TEST_DEVICE['clientID']}")
        if check.json()['deviceName'] == "Sensor_Main_Hall_UPDATED":
            print_pass("Device updated successfully.")
        else:
            print_fail("Device update not persisted")
    else:
        print_fail("Update Device failed", res.text)


    # ---------------------------------------------------------
    # 4. DELETE (DELETE)
    # ---------------------------------------------------------
    print("\n--- PHASE 4: DELETION (DELETE) ---")

    # 4.1 Delete Device
    res = requests.delete(f"{BASE_URL}/deleteDevice/{TEST_DEVICE['clientID']}")
    if res.status_code == 200: print_pass("Device deleted.")
    else: print_fail("Delete Device", res.text)

    # 4.2 Delete User
    res = requests.delete(f"{BASE_URL}/deleteUser/{TEST_USER['userID']}")
    if res.status_code == 200: print_pass("User deleted.")
    else: print_fail("Delete User", res.text)

    # 4.3 Delete Building
    res = requests.delete(f"{BASE_URL}/deleteBuilding/{TEST_BUILDING['buildingID']}")
    if res.status_code == 200: print_pass("Building deleted.")
    else: print_fail("Delete Building", res.text)

    # ---------------------------------------------------------
    # 5. VERIFICATION
    # ---------------------------------------------------------
    print("\n--- PHASE 5: FINAL VERIFICATION ---")
    
    # Ensure they are really gone (Should return 404)
    res = requests.get(f"{BASE_URL}/getResourceByID?clientID={TEST_DEVICE['clientID']}")
    if res.status_code == 404: print_pass("Verified Device is gone (404).")
    else: print_fail("Device still exists!", res.text)

    print("\n" + "="*50)
    print("✅✅✅ ALL TESTS PASSED SUCCESSFULLY! ✅✅✅")
    print("="*50)

if __name__ == "__main__":
    # Wait a moment for service to ensure it's up if ran immediately
    time.sleep(1)
    try:
        run_test()
    except requests.exceptions.ConnectionError:
        print("\n⛔ CRITICAL ERROR: Could not connect to the Service.")
        print(f"Make sure JSONCatalogProviderService.py is running on {BASE_URL}")