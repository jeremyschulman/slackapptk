from .any import AnyRequest

__all__ = [
    'AnyRequest',
    'OptionSelectRequest'
]


class OptionSelectRequest(AnyRequest):
    def __init__(
        self,
        app,
        payload
    ):
        """
        Slack will originate an external option select message when a User
        interacts with an external menu-select widget.

        Parameters
        ----------
        app: SlackApp
        payload: Dict
        """
        super().__init__(
            app=app,
            rqst_data=payload,
            rqst_type=payload['type'],
            user_id=payload['user']['id']
        )

        self.value = self.rqst_data['value']
        self.action_id = self.rqst_data['action_id']
        self.block_id = self.rqst_data['block_id']
