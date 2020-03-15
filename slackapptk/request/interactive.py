import json
from typing import Union, Dict

from slackapptk.errors import SlackAppTKUnhandledRequestError
from slackapptk.request.action_event import BlockActionEvent, ActionEvent
from slackapptk.request.view import ViewRequest, View
from slackapptk.request.outmoded import *


__all__ = [
    'AnyRequest',
    'ActionEvent',
    'BlockActionRequest',
    'BlockActionEvent',
    'InteractiveRequest'
]


class BlockActionRequest(AnyRequest):
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

        c_type = self.surface['type']

        if c_type == 'view':
            # self.view = ViewSurface(payload)
            self.view = View.from_view(view=payload['view'])
        elif c_type == 'message':
            self.channel = self.surface['channel_id']
        else:
            app.log.error(
                f'Unknown block action container type: {c_type}'
            )
            app.log.debug(json.dumps(self.rqst_data, indent=3))


RQST_TYPES = {
    'block_actions': BlockActionRequest,
    'dialog_submission': DialogRequest,
    'interactive_message': InteractiveMessageRequest,
    'view_submission': ViewRequest,
    'view_closed': ViewRequest
}


# -----------------------------------------------------------------------------
#
#                          ANY INTERACTIVE REQUEST MESSAGE
#
# -----------------------------------------------------------------------------


def InteractiveRequest(
    app,
    payload: Dict
) -> Union[BlockActionRequest,
           DialogRequest,
           InteractiveMessageRequest,
           ViewRequest, AnyRequest]:

    rqst_type = payload['type']
    rqst_cls = RQST_TYPES.get(rqst_type)

    if not rqst_cls:
        emsg = f'Unhadled request type: {rqst_type}'
        app.log.error(emsg)
        raise SlackAppTKUnhandledRequestError(
            app=app,
            payload=payload
        )

    return rqst_cls(app=app, payload=payload)
