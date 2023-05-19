import os

from notion.interfaces import INotionAPIClient, INotionDataParser


class NotionDataParser(INotionDataParser):
    def _format_text(self, text, value_type):
        if value_type == 'text':
            return text
        elif value_type == 'bulleted_list':
            return f"•   {text}"
        else:
            return None

    def _parse_text(self, title):
        text_list = []
        for text_data in title:
            if len(text_data) == 1 or (
                    text_data[1][0] and text_data[1][0][0] == 'a'):
                text_list.append(text_data[0])
        complete_text = ''.join(text_list)
        return complete_text

    def parse(self, data):
        page = []
        for _, data_value in data.items():
            value = data_value.get('value')
            value_type = value.get('type')
            title = value.get('properties', {}).get('title', [['']])
            text = self._parse_text(title)

            if not text:
                break

            text = self._format_text(text, value_type)
            if text:
                page.append(text)
        page_string = '\n'.join(page)
        return page_string


class NotionAPIClient(INotionAPIClient):

    host = os.environ.get('NOTION_HOST')
    notion_page_id = os.environ.get('NOTION_PAGE_ID')

    def __init__(self, api_client):
        self.api_client = api_client

    def get_page_content_from_response(self, response_data: dict):
        data = response_data.get("recordMap", {}).get("block", {})
        return data

    def get_status_data(self):
        url = os.path.join(self.host, 'api/v3/loadCachedPageChunk/')
        data = {
            "page": {"id": self.notion_page_id},
            "limit": 30,
            "cursor": {"stack": []},
            "chunkNumber": 0,
            "verticalColumns": False
        }
        response = self.api_client.request(url, method='POST', data=data)
        if not response:
            response = self.api_client.request(url, method='POST', data=data)
        return self.get_page_content_from_response(response)
