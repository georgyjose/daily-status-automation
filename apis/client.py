import json
import requests

from apis.interfaces import IAPIClient


class NoAuthIAPIClient(IAPIClient):
    def __init__(self, host):
        self.host = host

    def get_auth_header(self):
        return None

    def request(self, url: str, method: str,
                data: dict = None, timeout: int = 5):
        try:
            print(f'sending {method} request to {url} using data {data}')
            response = requests.request(method=method,
                                        url=url,
                                        json=data,
                                        headers=None,
                                        timeout=timeout)

            if response:
                json_response = json.loads(response.text)
                return json_response
            else:
                return {}
        except requests.exceptions.Timeout:
            return {}

