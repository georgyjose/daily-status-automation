from abc import ABC, abstractmethod

from apis.interfaces import IAPIClient


class INotionDataParser(ABC):
    @abstractmethod
    def parse(self, data: dict):
        pass

    @abstractmethod
    def _format_text(self, text: str, value_type: str):
        pass

    @abstractmethod
    def _parse_text(self, text: list):
        pass


class INotionAPIClient(ABC):
    host = None
    notion_page_id = None
    api_client: IAPIClient = None

    @abstractmethod
    def get_page_content_from_response(self, response):
        pass

    @abstractmethod
    def get_status_data(self):
        pass
