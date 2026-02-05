import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")

from src.Services.REST.RESTServices.CatalogProviderServices.JSONCatalogProviderService import JSONCatalogProviderService

if __name__ == "__main__":
    
    service = JSONCatalogProviderService("./MicroServices/JSONCatalogProviderService/configJSONCatalogProviderService.yaml")
    
    service.setServiceRunTimeStatus(True)
    service.serviceRunTime()