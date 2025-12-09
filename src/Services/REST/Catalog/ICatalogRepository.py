from abc import ABC, abstractmethod


class ICatalogRepository(ABC):

    @abstractmethod
    def getCatalog(self) -> dict:
        """Returns the catalog as dict"""
        pass

    @abstractmethod
    def updateCatalog(self, new_data: tuple[str, dict] | list[tuple[str,dict]])-> bool:
        pass

    # TODO: maybe search by only 1 id it's not fine -> give list of IDs
    # I implemented the code this way so that it can accept both single value
    #  and list of values (if you preferer, we can remove the single value)
    @abstractmethod
    def getResourceById(self, resource_id: str | list[str]) -> dict | list[dict]:
        pass

    @abstractmethod
    def removeResourceById(self, resource_id: str | list[str]) -> bool:
        pass

    @abstractmethod
    def addResource(self, new_resource: dict | list[dict]) -> bool:
        pass