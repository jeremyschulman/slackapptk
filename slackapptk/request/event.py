from typing import Dict
from .any import AnyRequest

__all__ = [
    'AnyRequest',
    'EventRequest'
]


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
