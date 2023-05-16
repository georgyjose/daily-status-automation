from abc import ABC, abstractmethod, abstractproperty


class APIClient(ABC):

    @abstractmethod
    def request(self, url, method, data=None):
        pass

    @abstractmethod
    def get_auth_header(self):
        pass
