from typing import Dict
import json

from slackapptk.request.any import AnyRequest

__all__ = [
    'AnyRequest',
    'DialogRequest',
    'InteractiveMessageRequest'
]


class DialogRequest(AnyRequest):
    def __init__(
        self,
        app,
        payload: Dict
    ):
        """
        Inbound request originated from a Dialog user interaction.

        Parameters
        ----------
        app: SlackApp

        payload: Dict
            The request form 'payload' dict

        Notes
        -----
        Dialog requests are considered to be depreciated in favor of using Modals
        and Blocks.
        """
        super().__init__(
            app=app,
            rqst_type=payload['type'],
            rqst_data=payload,
            user_id=payload['user']['id']
        )
        self.state = json.loads(payload.get('state') or '{}')


class InteractiveMessageRequest(AnyRequest):
    def __init__(
        self,
        app,
        payload: Dict
    ):
        """
        Interative Message attachments are an outmoded approach using Message Attachments.
        The new approach is to use Blocks.

        Parameters
        ----------
        app
        payload: Dict

        Notes
        -----
        https://api.slack.com/docs/outmoded-messaging
        """
        super().__init__(
            app=app,
            rqst_type=payload['type'],
            rqst_data=payload,
            user_id=payload['user']['id']
        )
        self.user_name = payload['user']['name']
        self.channel = payload['channel']['id']
