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

import json

from typing import TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from slackapp2pyez import SlackApp

from werkzeug.exceptions import Unauthorized
from flask import session
from slack import WebClient

from slackapp2pyez.response import Response

__all__ = [
    'BlockActionsRequest',
    'CommandRequest',
    'DialogRequest',
    'EventRequest',
    'InteractiveRequest',
    'OptionSelectRequest',
    'Request',
    'ViewRequest',
]


class Request(object):

    def __init__(
            self,
            app,
            request
    ):
        self.app: SlackApp = app
        self.rqst_data = request.form
        self.rqst_type = session['rqst_type']
        self.user_id = session['user_id']
        self.payload = session['payload']

        # default places to look for values in payload
        self.response_url = self.payload.get('response_url')
        self.trigger_id = self.payload.get('trigger_id')
        self.channel = self.payload.get('channel')

        self.client: Optional[WebClient] = None

    def delete(self):
        """
        This method will cause the original request message to be deleted in
        the Slack client.
        """
        Response(self).send(delete_original=True, replace_original=True)

    def finalize(self):
        # if this request originated with a channel ID value, then make sure it
        # is valid for this channel based on the app configuration.  Note that
        # Modal requests do not have channel ID values.

        if self.channel is not None and self.channel not in self.app.config.channels:
            msg = f"Unable to execute the Request in this channel: {self.channel}"
            self.app.log.error(msg)
            raise Unauthorized(description=msg)

        self.client = WebClient(token=self.app.config.token)


class CommandRequest(Request):
    def __init__(self, app, request):
        """
        No 'payload' in form_data
        """
        super().__init__(app, request)
        assert self.rqst_type == 'command'

        self.trigger_id = self.rqst_data['trigger_id']
        self.response_url = self.rqst_data['response_url']
        self.channel = self.rqst_data["channel_id"]
        self.user_name = self.rqst_data['user_name']
        self.argv = self.rqst_data['text'].split()

        self.finalize()


class DialogRequest(Request):
    def __init__(self, app, request):
        super().__init__(app, request)
        self.state = json.loads(self.payload.get('state') or '{}')
        self.finalize()


class EventRequest(Request):
    def __init__(self, app, request):
        super().__init__(app, request)
        assert self.rqst_type == 'event'

        self.event = self.rqst_data['event']
        self.user_id = self.event['user']
        self.channel = self.event['channel']
        self.text = self.event['text']
        self.ts = self.event['ts']

        self.finalize()


class OptionSelectRequest(Request):
    def __init__(self, app, request):
        super().__init__(app, request)
        assert self.rqst_type == 'block_suggestion'

        self.value = self.payload['value']
        self.action_id = self.payload['action_id']
        self.block_id = self.payload['block_id']

        self.finalize()


class ViewRequest(Request):
    def __init__(self, app, request):
        super().__init__(app, request)
        self.user_name = self.payload['user']['name']

        # view specific attributes

        self.view = self.payload['view']
        self.view_id = self.view['id']
        self.view_state_values = self.view['state']['values']
        self.view_hash = self.view['hash']
        self.private_metadata = json.loads(self.view.get('private_metadata') or '{}')

        self.finalize()


class InteractiveMessageRequest(Request):
    def __init__(self, app, request):
        super().__init__(app, request)
        self.user_name = self.payload['user']['name']
        self.channel = self.payload['channel']['id']
        self.finalize()


class BlockActionsRequest(Request):
    def __init__(self, app, request):
        super().__init__(app, request)
        self.user_name = self.payload['user']['name']
        self.trigger_id = self.payload['trigger_id']
        container = self.payload['container']
        c_type = container['type']
        if c_type == 'view':
            self.view = self.payload['view']
        elif c_type == 'message':
            self.channel = container['channel_id']
        else:
            app.log.error(
                f'Unknown block action container type: {c_type}'
            )
            app.log.debug(json.dumps(self.payload, indent=3))

        self.finalize()


class InteractiveRequest(type):

    RQST_TYPES = {
        'block_actions': BlockActionsRequest,
        'dialog_submission': DialogRequest,
        'interactive_message': InteractiveMessageRequest,
        'view_submission': ViewRequest,
        'view_closed': ViewRequest
    }

    def __new__(
        mcs,
        *args,
        **kwargs
    ) -> Optional[Union[BlockActionsRequest, DialogRequest,
                        InteractiveMessageRequest, ViewRequest,
                        Request]]:
        """
        This type class is used to introspect the received flask.Request
        instance to determine the specific type of interactive component
        request and create the corresponding SlackApp request instance.
        """
        app, request = kwargs['app'], kwargs['request']
        r_type = session['rqst_type']
        r_cls = mcs.RQST_TYPES.get(r_type)

        if not r_cls:
            app.log.error(
                f'Unhadled request type: {r_type}'
            )
            r_cls = Request

        return r_cls(app=app, request=request)
