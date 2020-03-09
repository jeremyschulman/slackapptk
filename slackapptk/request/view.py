from slackapptk.request.any import AnyRequest
from slackapptk.web.classes.view import View

__all__ = [
    'AnyRequest',
    'ViewRequest',
    'View'
]


class ViewRequest(AnyRequest):
    def __init__(
        self,
        app,
        payload
    ):
        super().__init__(
            app=app,
            rqst_type=payload['type'],
            rqst_data=payload,
            user_id=payload['user']['id']
        )
        self.view = View.from_view(view=payload['view'])
