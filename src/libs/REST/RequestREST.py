import requests
import json

class RequestREST:
    def __init__(self, severURL:str) -> None:
        self.serverURL = severURL
        
    def GET(self, resource:str, params=None) -> dict:
        try : 
            url = f"{self.serverURL}/{resource}"
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"GET request failed with status code {response.status_code}")
                return {}
            response.raise_for_status()
            return response.json()
        except Exception as e :
            print(f"GET request error: {e}")
            return {}
        
    def POST(self, resource:str, data:dict, params=None) -> dict:
        pass

    def PUT(self, resource:str, data:dict, params=None) -> dict: 
        try :
            url = f"{self.serverURL}/{resource}"
            response = requests.put(url, params=params, json=data)
            if response.status_code != 200:
                print(f"PUT request failed with status code {response.status_code}")
                return {}
            response.raise_for_status()
            return response.json()
        except Exception as e :
            print(f"PUT request error: {e}")
            return {}
    
    def DELETE(self, resource:str, params=None):
        pass