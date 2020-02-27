from typing import Dict

from slack.web.client import WebClient


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
        self.payload = rqst_data

        # default places to look for values in payload
        self.response_url = self.rqst_data.get('response_url')
        self.trigger_id = self.rqst_data.get('trigger_id')
        self.channel = self.rqst_data.get('channel')
        self.surface = self.rqst_data.get('container')

        self.client = WebClient(token=self.app.config.token)


class CommandRequest(AnyRequest):
    def __init__(
        self,
        app,
        form_data
    ):
        """
        Inbound message is a result of a User entering a /command.
        """
        super().__init__(
            app=app,
            rqst_type='command',
            rqst_data=form_data,
            user_id=form_data['user_id']
        )

        self.channel = self.rqst_data["channel_id"]
        self.argv = self.rqst_data['text'].split()


class EventRequest(AnyRequest):
    def __init__(
        self,
        app,
        body: Dict
    ):
        """
        The event data is from the inbound message JSON body.

        Parameters
        ----------
        app: SlackApp

        body: Dict
            The request body from JSON.

        Notes
        -----
        https://api.slack.com/types/event
        """
        super().__init__(
            app=app,
            rqst_type='event',
            rqst_data=body,
            user_id=body['event']['user']

        )

        self.event = self.rqst_data['event']
        self.event_type = self.event['type']
        self.ts = self.event['ts']
