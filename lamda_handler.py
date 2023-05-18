import os
from apis.client import NoAuthIAPIClient
from notion.client import Notion
from slack.client import SlackClient
from slack_sdk import WebClient
USER_TOKEN = os.environ.get('USER_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
NOTION_HOST_URL = os.environ.get('NOTION_HOST_URL')


def lambda_handler(event, context):
    api_client = NoAuthIAPIClient(host=NOTION_HOST_URL)
    notion = Notion(api_client=api_client)
    status_data = notion.get_status_data()
    parse_data = notion.parse(status_data)

    sdk = WebClient(token=USER_TOKEN)
    slack_client = SlackClient(sdk=sdk)
    convo_history = slack_client.get_conversation_history(
        channel_id=CHANNEL_ID)
    thread = slack_client.get_thread_id_from_msg_history(convo_history)
    slack_client.post_message(
        channel_id=CHANNEL_ID, thread_id=thread, message=parse_data)
