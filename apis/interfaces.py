from abc import ABC, abstractmethod


class IAPIClient(ABC):

    @abstractmethod
    def request(self, url, method, data=None):
        pass

    @abstractmethod
    def get_auth_header(self):
        pass
