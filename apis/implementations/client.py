import json

import requests

from apis.interfaces.client import APIClient


class NoAuthAPIClient(APIClient):
    host = None

    def get_auth_header(self):
        return None

    def request(self, url: str, method: str,
                data: dict = None, timeout: int = 5):
        try:
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

