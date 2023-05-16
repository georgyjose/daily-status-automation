import os
import os.path
from notion.interfaces.api_client import INotionAPIClient


class NotionAPIClient(INotionAPIClient):

    def __init__(self):
        self.host = 'https://energetic-tuberose-21a.notion.site'
        self.notion_page_id = os.environ.get("NOTION_PAGE_ID")

    def get_status_data(self):
        url = os.path.join(self.host, 'api/v3/loadCachedPageChunk')
        data = {
            "page": {"id": self.notion_page_id},
            "limit": 30,
            "cursor": {"stack": []},
            "chunkNumber": 0,
            "verticalColumns": False
        }
        return self.request(url, method='GET', data=data)
