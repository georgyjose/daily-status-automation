import requests
import logging
import os

from abc import ABC, abstractmethod

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import timedelta, datetime

logger = logging.getLogger(__name__)

CHANNEL_ID = os.environ.get("CHANNEL_ID")
USER_TOKEN = os.environ.get("USER_TOKEN")
NOTION_PAGE_ID = os.environ.get("NOTION_PAGE_ID")

DAILY_STATUS_FILTER_TEXT = "Good morning! Don't forget to post your update in thread."
DAILY_STATUS_FILTER_POD_NAME = "learningpod"
AUTOMATED_MESSAGE = "Note: This is an automated message :yum:"


"""This is a test commit"""

class Notion(ABC):
    @abstractmethod
    def parse_response(self, notion_url):
        pass

    @abstractmethod
    def parse_response(self, data):
        pass

    


class NotionParser(Notion):
    def __init__(self, page_id):
        self.page_id = page_id

    def request_data(self, notion_url):
        response = requests.post(
            notion_url, 
            json={
                    "page": {"id": self.page_id},
                    "limit": 30,
                    "cursor":{"stack": []},
                    "chunkNumber":0 ,
                    "verticalColumns": False}
        )
        response_data= response.json()
        return response_data.get("recordMap", {}).get("block", {})

    def parse_text(self, title):
        text_list = []
        for text_data in title:
            if len(text_data) == 1:
                text_list.append(text_data[0])
            elif text_data[1][0] and text_data[1][0][0] == 'a':
                text_list.append(text_data[0])
        return ''.join(text_list)

    def format_text(self, text, value_type):
        if value_type == 'text':
            return text
        elif value_type == 'bulleted_list':
            return f"•   {text}"
        elif value_type == 'page':
            return None

    def parse_response(self, data):
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
        page.append(AUTOMATED_MESSAGE)
        return '\n'.join(page)


class SlackMessaging(ABC):
    @abstractmethod
    def post_message(self, message, channel_id, thread_id=None):
        pass

    @abstractmethod
    def get_status_thread_id(self):
        pass


class SlackClient(SlackMessaging):
    def __init__(self, , user_token):
        self.client = WebClient(token=user_token)

    def post_message(self, message, channel_id, thread_id=None):
        try:
            result = self.client.chat_postMessage(
                channel=self.channel_id,
                text=text,
                thread_ts=thread_id
            )
            logger.info(result)

        except SlackApiError as e:
            logger.error(f"Error posting message: {e}")

    def get_status_thread_id(self):
        try:
            older_time = (datetime.now()-timedelta(hours=12)).timestamp()
            result = self.client.conversations_history(channel=self.channel_id, oldest=older_time)
            conversation_history = result["messages"]
            for conversation_data in conversation_history:
                text = conversation_data.get('text')
                if DAILY_STATUS_FILTER_TEXT in text and DAILY_STATUS_FILTER_POD_NAME in text:
                    return conversation_data.get('ts')

        except SlackApiError as e:
            logger.error(f"Error getting message: {e}")


def lambda_handler(event, context):
    notion_parser = NotionParser(NOTION_PAGE_ID)
    slack_client = SlackClient(USER_TOKEN)
    notion_url = "https://energetic-tuberose-21a.notion.site/api/v3/loadCachedPageChunk" 
    channel_id = CHANNEL_ID
    # Due to some unknown reason Notion gives correct data only in the second api call.
    data = notion_parser.request_data(notion_url)
    data = notion_parser.request_data(notion_url)

    page = notion_parser.parse_response(data)
    thread_id = slack_client.get_status_thread_id()

    if thread_id and page != AUTOMATED_MESSAGE:
        slack_client.post_message(page, channel_id, thread_id)
        logger.info(f"Successfully posted")
    elif page == AUTOMATED_MESSAGE:
        logger.info(f"Not posting status")
    else:
        logger.error(f"Couldn't get thread id: {thread_id}")

    return { 
        'message' : "Success",
        'status_code': 200
    }

if __name__ == '__main__':
    lambda_handler(None, None)
