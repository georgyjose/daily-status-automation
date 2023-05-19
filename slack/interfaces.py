from abc import ABC, abstractmethod

from slack_sdk import WebClient as SlackSDKWebClient


class ISlackRequestProcessor(ABC):
    @abstractmethod
    def get_thread_id_from_msg_history(self, msg_history: list):
        pass


class ISlackAPIClient(ABC):
    sdk: SlackSDKWebClient = None

    @abstractmethod
    def get_conversation_history(self, channel_id, timestamp):
        pass

    @abstractmethod
    def post_message(self, channel, thread, message):
        pass
