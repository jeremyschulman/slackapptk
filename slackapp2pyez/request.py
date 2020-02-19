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

from first import first
from flask import session
from slack import WebClient

from slackapp2pyez.response import Response
from slackapp2pyez.exceptions import SlackAppError

__all__ = ['Request']


class Request(object):

    def __init__(self, app, request):

        self.app = app
        self.rqst_data = request.form
        self.rqst_type = session['rqst_type']
        self.user_id = session['user_id']

        if self.rqst_type == 'command':
            self.channel = self.rqst_data["channel_id"]
            self.user_name = self.rqst_data['user_name']
            self.response_url = self.rqst_data['response_url']
            self.trigger_id = self.rqst_data['trigger_id']
            self.argv = self.rqst_data['text'].split()

        elif self.rqst_type == 'event':
            self.event = self.rqst_data['event']
            self.user_id = self.event['user']
            self.channel = self.event['channel']
            self.text = self.event['text']
            self.ts = self.event['ts']

        elif session['payload']:
            self.payload = session['payload']
            self.trigger_id = self.payload.get('trigger_id')
            self.user_name = self.payload['user']['name']

            if 'channel' in self.payload:
                self.channel = self.payload['channel']['id']
                self.response_url = self.payload['response_url']
                self.state = json.loads(self.payload.get('state') or '{}')

            if 'view' in self.payload:
                self.view = self.payload['view']
                self.view_id = self.view['id']
                self.view_state_values = self.view['state']['values']
                self.view_hash = self.view['hash']
                self.private_metadata = json.loads(self.view.get('private_metadata') or '{}')

        else:
            app.log.error(
                f'Unhadled request type: {self.rqst_type}'
            )
            return

        # if this request originated with a channel ID value, then make sure it
        # is valid for this channel based on the app configuration.  Note that
        # Modal requests do not have channel ID values.

        if hasattr(self, 'channel') and self.channel not in app.config.channels:
            msg = f"Unable to execute the Request in this channel: {self.channel}"
            app.log.error(msg)
            raise SlackAppError(msg, 401, self)

        self.client = WebClient(token=self.app.config['bot']['token'])

    def ResponseMessage(self):
        """
        Return a Slack Response instance based on the current Slack Request
        """

        return Response(rqst=self)

    def delete(self):
        """
        This method will cause the original request message to be deleted in
        the Slack client.
        """
        self.ResponseMessage().send(delete_original=True, replace_original=True)
