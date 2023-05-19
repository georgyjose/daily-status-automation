import os
from datetime import datetime, timedelta

from slack.interfaces import ISlackRequestProcessor, ISlackAPIClient
DAILY_STATUS_FILTER_TEXT = \
    "Good morning! Don’t forget to post your update in thread."
DAILY_STATUS_FILTER_POD_NAME = os.environ.get('DAILY_STATUS_FILTER_POD_NAME')


class SlackRequestProcessor(ISlackRequestProcessor):
    def get_thread_id_from_msg_history(self, msg_history: list):
        for conversation_data in msg_history:
            text = conversation_data.get('text')
            if DAILY_STATUS_FILTER_TEXT in text and \
                    DAILY_STATUS_FILTER_POD_NAME in text:
                return conversation_data.get('ts')
        return None


class SlackAPIClient(ISlackAPIClient):

    def __init__(self, sdk):
        self.sdk = sdk

    def get_conversation_history(self, channel_id, timestamp=None):
        if not timestamp:
            timestamp = str(
                (datetime.now() - timedelta(hours=12)).timestamp()
            )
        try:
            convo_history = self.sdk.conversations_history(
                channel=channel_id,
                oldest=timestamp
            )
            result = convo_history['messages']
        except Exception as e:
            print(e)
            result = None
        return result

    def post_message(self, channel_id, thread_id, message):
        try:
            result = self.sdk.chat_postMessage(
                channel=channel_id,
                text=message,
                thread_ts=thread_id
            )
        except Exception as e:
            print(e)
            result = None
        return result
