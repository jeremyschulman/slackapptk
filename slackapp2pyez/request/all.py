#  Copyright 2019 Jeremy Schulman, nwkautomaniac@gmail.com
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# https://api.slack.com/reference/interaction-payloads/views#view_submission


from typing import Dict


from slackapp2pyez.exceptions import SlackAppUnhandledRequestError
from slackapp2pyez.request.basic import *
from slackapp2pyez.request.view import *
from slackapp2pyez.request.outmoded import *
from slackapp2pyez.request.action_event import *


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
            self.view = ViewSurface(payload)
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
        raise SlackAppUnhandledRequestError(
            app=app,
            payload=payload
        )

    return rqst_cls(app=app, payload=payload)
