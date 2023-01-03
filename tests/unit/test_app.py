import unittest
from unittest.mock import patch, MagicMock
import os

from requests import HTTPError

# Mock the environment variables needed for Slack notifications
os.environ["SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/services/1234567890/1234567890/1234567890"

from slack_notifications import app


class TestLambdaHandler(unittest.TestCase):
    @patch("slack_notifications.app.requests.post")
    def test_lambda_handler(self, mock_post):
        # Setup the mock response from Slack
        mock_post.return_value.status_code = 200
        mock_post.return_value.reason = "OK"

        # Set up the test event
        event = {
            "Records": [
                {
                    "account": "123456789012",
                    "region": "eu-east-1",
                    "detail": {
                        "sourceIPAddress": "123.123.123.123",
                        "eventName": "ConsoleLogin",
                        "eventTime": "2020-01-01T00:00:00Z",
                        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
                        "additionalEventData": {"MFAUsed": "Yes"},
                    },
                }
            ]
        }

        # Call the lambda handler
        result = app.lambda_handler(event, None)

        # Check the result
        self.assertEqual(result, "Success")

    @patch("slack_notifications.app.requests.post")
    def test_lambda_handler_error(self, mock_post):
        # Set up the mock response from Slack
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.reason = "Bad Request"
        mock_response.raise_for_status.side_effect = HTTPError("400 Bad Request")
        mock_post.return_value = mock_response

        # Set up the test event
        event = {
            "Records": [
                {
                    "account": "123456789012",
                    "region": "us-east-1",
                    "detail": {
                        "sourceIPAddress": "123.123.123.123",
                        "eventName": "consoleLogin",
                        "eventTime": "2022-01-01T00:00:00Z",
                        "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
                        "additionalEventData": {"MFAUsed": "Yes"},
                    },
                }
            ]
        }

        # Call the lambda handler
        result = app.lambda_handler(event, None)

        # Check the result
        self.assertEqual(result, "Error")

    def test_lambda_handler_missing_records(self):
        # Set up the test event
        event = {}

        # Call the lambda handler
        result = app.lambda_handler(event, None)

        # Check the result
        self.assertEqual(result, "Error")


if __name__ == "__main__":
    unittest.main()
