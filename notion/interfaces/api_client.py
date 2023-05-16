from abc import ABC, abstractmethod

from apis.implementations.client import NoAuthAPIClient


class INotionAPIClient(ABC, NoAuthAPIClient):
    host = None
    notion_page_id = None

    @abstractmethod
    def get_status_data(self):
        pass
