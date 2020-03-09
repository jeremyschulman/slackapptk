from .any import AnyRequest

__all__ = [
    'AnyRequest',
    'CommandRequest'
]


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
