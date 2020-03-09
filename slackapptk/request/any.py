from typing import Dict
from slack.web.client import WebClient

__all__ = ['AnyRequest']


class AnyRequest(object):

    def __init__(
        self,
        app,
        rqst_type: str,
        rqst_data: Dict,
        user_id: str
    ):
        """
        An instance that represents any one of the many inbound requests from api.slack.com

        Parameters
        ----------
        app: SlackApp
        rqst_type: str
            The request type, as originated from the request message

        rqst_data: Dict
            The data portion of the request message.  For some message types
            this is the request form payload, and for other message types there
            is a single 'payload' within the form that contains the actual
            request data.

        user_id: str
            The Slack User-ID value originating the request.  This value is
            stored in different places depending on the message type.
        """
        self.app = app
        self.rqst_data = rqst_data
        self.rqst_type = rqst_type
        self.user_id = user_id

        # default places to look for values in payload
        self.response_url = self.rqst_data.get('response_url')
        self.trigger_id = self.rqst_data.get('trigger_id')
        self.channel = self.rqst_data.get('channel')
        self.surface = self.rqst_data.get('container')

        self.client = WebClient(token=self.app.config.token)
