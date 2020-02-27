import json
from slackapp2pyez.request.basic import AnyRequest


class ViewSurface(object):
    def __init__(self, payload):
        self.data = view = payload['view']
        self.id = view['id']
        self.state_values = view['state']['values']
        self.hash = view['hash']
        self.private_metadata = json.loads(view.get('private_metadata') or '{}')


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
        self.view = ViewSurface(payload)

