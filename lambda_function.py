import logging
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from abc import ABC, abstractmethod
from datetime import timedelta, datetime
import requests


class DataFetcher(ABC):
    """
    Abstract class for data fetching
    """
    @abstractmethod
    def fetch_data(self):
        """
        Method for fetching data
        """
        pass


class DataParser(ABC):
    """
    Abstract class for parsing data 
    """
    @abstractmethod
    def parse_response(self, data):
        """
        Method for parsing data
        """
        pass


class NotionClient(DataFetcher, DataParser, ABC):
    """
    Notion abstract class
    """
    pass

class NotionDataClient(NotionClient):
    """
    Implementation of NotionData
    """
    def __init__(self, notion_page_id, notion_url):
        self.notion_page_id = notion_page_id
        self.notion_url = notion_url

    def fetch_data(self):
        response = requests.post(
            self.notion_url,
            json={
                "page": {"id": self.notion_page_id},
                "limit": 30,
                "cursor": {"stack": []},
                "chunkNumber": 0,
                "verticalColumns": False
            }
        )
        response_data = response.json()
        data = response_data.get("recordMap", {}).get("block", {})
        return data

    def parse_text(self, title):
        """
        Method for parsing text
        """
        text_list = []
        for text_data in title:
            if len(text_data) == 1:
                text_list.append(text_data[0])
            elif text_data[1][0] and text_data[1][0][0] == 'a':
                text_list.append(text_data[0])
        complete_text = ''.join(text_list)
        return complete_text

    def format_text(self, text, value_type):
        """
        Method for formatting text
        """
        if value_type == 'text':
            return text
        elif value_type == 'bulleted_list':
            return f"•   {text}"
        elif value_type == 'page':
            return None

    def parse_response(self, data):
        """
        Parse response method
        """
        page = []
        for _, data_value in data.items():
            value = data_value.get('value')
            value_type = value.get('type')
            title = value.get('properties', {}).get('title', [['']])
            text = self.parse_text(title)

            if not text:
                break

            text = self.format_text(text, value_type)
            if text:
                page.append(text)
        page.append("Note: This is an automated message 😋")
        page_string = '\n'.join(page)
        return page_string


class StatusPoster(ABC):
    """
    Abstract class for posting status
    """
    @abstractmethod
    def post_status(self, text, thread_id):
        """
        Post status method
        """
        pass


class StatusReader(ABC):
    @abstractmethod
    def get_status_thread_id(self):
        pass


class SlackClient(StatusPoster, StatusReader, ABC):
    """
    Abstract class for slack client
    """
    @abstractmethod
    def __init__(self, token):
        self.token = token
        self.channel_id = None
        self.daily_status_filter_text = None
        self.daily_status_filter_pod_name = None


class SlackStatusClient(SlackClient):
    """
    Implementation of SlackClient
    """
    def __init__(self, token):
        super().__init__(token)
        self.slack_client = WebClient(token=token)

    def post_status(self, text, thread_id):
        try:
            result = self.slack_client.chat_postMessage(
                channel=self.channel_id,
                text=text,
                thread_ts=thread_id
            )
            logging.getLogger(__name__).info(result)

        except SlackApiError as error:
            logging.getLogger(__name__).error(f"Error posting message: {error}")

    def get_status_thread_id(self):
        older_time = (datetime.now() - timedelta(hours=12)).timestamp()
        try:
            result = self.slack_client.conversations_history(channel=self.channel_id, oldest=older_time)
            conversation_history = result["messages"]
            for conversation_data in conversation_history:
                text = conversation_data.get('text')
                if self.daily_status_filter_text in text and self.daily_status_filter_pod_name in text:
                    return conversation_data.get('ts')

        except SlackApiError as error:
            logging.getLogger(__name__).error(f"Error getting message: {error}")

        return None


class NotionStatusPoster:
    """
    Notion status poster class
    """
    def __init__(self, notion_client: NotionClient, slack_client: SlackClient):
        self.logger = logging.getLogger(__name__)
        self.notion_client = notion_client
        self.slack_client = slack_client

    def post_daily_status_to_slack(self):
        """
        Method for posting status
        """
        notion_data = self.notion_client.fetch_data()

        page = self.notion_client.parse_response(notion_data)
        thread_id = self.slack_client.get_status_thread_id()

        if thread_id and page != "Note: This is an automated message 😋":
            self.slack_client.post_status(page, thread_id)
            self.logger.info(f"Successfully posted")
        elif page == "Note: This is an automated message 😋":
            self.logger.info(f"Not posting status")
        else:
            self.logger.error(f"Couldn't get thread id: {thread_id}")

    def post_daily_status(self):
        self.post_daily_status_to_slack()

def lambda_handler(event, context):
    """
    Lambda function
    """
    logging.basicConfig(level=logging.INFO)
    notion_page_id = os.environ.get("NOTION_PAGE_ID")
    notion_url = os.environ.get("NOTION_URL")
    notion_data_fetcher_parser = NotionDataClient(notion_page_id, notion_url)
    slack_client = SlackStatusClient(os.environ.get("USER_TOKEN"))
    slack_client.channel_id = os.environ.get("CHANNEL_ID")
    slack_client.daily_status_filter_text = "Good morning! Don’t forget to post your update in thread."
    slack_client.daily_status_filter_pod_name = "learningpod"

    notion_status_poster = NotionStatusPoster(notion_data_fetcher_parser, slack_client)
    notion_status_poster.post_daily_status()


if __name__ == '__main__':
    lambda_handler(None, None)