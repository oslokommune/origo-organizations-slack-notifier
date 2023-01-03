# Lambda Slack Notifications
# Author: Karl Mathias Moberg (@kmoberg)
# Date: 2023-01-01
# Version: 1.0.0


import logging
import os

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]


def lambda_handler(event, context):
    # Parse the SNS message
    logger.info("Starting lambda_handler")
    logger.info("Event: {}".format(event))

    try:
        event_bridge_message = event["Records"][0]
    except KeyError:
        logger.error("Event does not contain Records")
        event_bridge_message = event
        return "Error"

    logger.info("Event Bridge Message: {}".format(event_bridge_message))

    message_json = event_bridge_message

    # Extract the relevant information from the message
    account = message_json["account"]
    region = message_json["region"]
    event_detail = message_json["detail"]
    source_ip = event_detail["sourceIPAddress"]
    event_name = event_detail["eventName"]
    event_time = event_detail["eventTime"]
    user_agent = event_detail["userAgent"]
    mfa_used = event_detail["additionalEventData"]["MFAUsed"]
    use_emoji = True

    # Build the Slack message
    slack_message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⚠️  AWS Root User Login",
                    "emoji": use_emoji,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "A login to an Origo AWS account using a root user was detected. Details:",
                },
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"*Account ID:* {account}"}],
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"*Region:* {region}"}],
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"*Source IP:* {source_ip}"}],
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"*Event Name:* {event_name}"}],
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"*Event Time:* {event_time}"}],
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"*User Agent:* {user_agent}"}],
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"*MFA Used:* {mfa_used}"}],
            },
        ]
    }

    # Send the message to Slack
    try:
        request = requests.post(SLACK_WEBHOOK_URL, json=slack_message)
        request.raise_for_status()
    except requests.exceptions.RequestException:
        logging.error(f"Error sending message to Slack")
        return "Error"
    except Exception as err:
        logging.exception(f"Unexpected error: {err}")
        return "Error"

    return "Success"



