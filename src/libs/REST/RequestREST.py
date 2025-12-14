import requests
import json

class RequestREST:
    def __init__(self, serverURL:str) -> None:
        self.serverURL = serverURL
        
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
        
    def POST(self, resource:str, data:dict):
        try:
            url=f"{self.serverURL}/{resource}"
            response=requests.post(url,json=data)
            if response.status_code!=200:
                print(f"POST request failed with status code {response.status_code}")
        except Exception as e :
            print(f"GET request error: {e}")

    def PUT(self, resource:str, data:dict):
        pass
    
    def DELETE(self, resource:str, params=None):
        pass