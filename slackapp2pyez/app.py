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

import time
import hmac
import hashlib
import json

from first import first
import pyee
from slack import WebClient

from slackapp2pyez.request import Request
from slackapp2pyez.log import create_logger
from slackapp2pyez.config import SlackAppConfig
from slackapp2pyez import ui
from slackapp2pyez.cli import SlashCommandCLI


__all__ = ['SlackApp']


class SlackAppUIEventHandlers(object):
    def __init__(self, app):
        self.app = app
        self.block_action = pyee.EventEmitter()
        self.dialog = pyee.EventEmitter()
        self.imsg_attch = pyee.EventEmitter()
        self.modal = pyee.EventEmitter()


class SlackApp(object):

    def __init__(self):
        self.log = create_logger()
        self.slash_commands = dict()

        self.ui = SlackAppUIEventHandlers(app=self)

        # create callback handler for different interactive payload types.
        #   https://api.slack.com/reference/interaction-payloads
        #   https://api.slack.com/interactivity/handling#payloads

        self._ia_payload_hanlder = {

            'block_actions': self._handle_block_action,
            'message_actions': self._handle_message_action,
            'view_closed': self._handle_view_closed_action,
            'view_submission': self._handle_view_submission_action,

            # TODO: deprecate, this is outmoded style of handling attachment
            #       interactive elements
            #       https://api.slack.com/reference/messaging/attachments

            'interactive_message': self._handle_ia_msg_attachment,

            # TODO: migrate Dialogs to Modals
            #       https://api.slack.com/block-kit/dialogs-to-modals

            'dialog_submission': self._handle_dialog_submit
        }

        self.config = SlackAppConfig()

    def RequestEvent(self, request):
        return Request(app=self, request=request)

    def Client(self, channel=None, chan_id=None, as_bot=False):
        """
        Create a Slack Web Client instance based on the SlackApp configuration
        or provided parameters.  This is generally used for test and debug
        purposes, and not by the SlackApp itself.

        Parameters
        ----------
        channel
        chan_id
        as_bot

        Returns
        -------
        WebClient
            The Slack WebClient instance that is used for api.slac.com
            communicaiton purposes.
        """
        # need the channel ID to assocaite this SlackApp.  If one was provided
        # use it, or if the channle name was provided use that, or use the
        # first channel in the channels configured list.

        chan_id = (chan_id or (
            self.config['SLACK_CHANNEL_NAME_TO_ID'][channel] if channel
            else first(self.config.channels)))

        chan_cfg = self.config.channels[chan_id]
        token = chan_cfg['oauth_token' if not as_bot else 'bot_oauth_token']
        return WebClient(token=token)

    # -------------------------------------------------------------------------
    # Request handlers - per payload
    # -------------------------------------------------------------------------

    def handle_interactive_request(self, request):
        """
        This method should be called by the API route handler bound to the
        Interactive Compenents, Interactivity "Request URL" configured
        in the api.slack.com site.

        The purpose of this method is to invoke the handler bound to the
        specific type of interactive Request.  Different types of
        interactive messages are handled diffently.

        Parameters
        ----------
        request : flask.request

        Returns
        -------
        dict or empty-string
            When dict, this will be the JSON payload returned to the api.slack.com
            system; i.e. return message as a result of handling this Request.
            If there is no dict-data, then return empty-string, which is required
            by the api.slack.com for response.
        """
        rqst = Request(app=self, request=request)
        self.log.debug("PAYLOAD>> {}\n".format(json.dumps(rqst.payload, indent=3)))
        p_type = rqst.payload['type']
        return self._ia_payload_hanlder[p_type](rqst) or ""

    # -------------------------------------------------------------------------
    # PRIVATE Request handlers - per payload type
    # -------------------------------------------------------------------------

    def _handle_message_action(self, rqst):
        pass

    def _handle_view_closed_action(self, rqst):
        pass

    def _handle_view_submission_action(self, rqst):
        event = rqst.view['callback_id']
        callback = first(self.ui.modal.listeners(event))
        vsv = rqst.view_state_values

        input_types = {
            'plain_text_input': lambda e: e.get('value'),
            'static_select': lambda e: e.get('selected_option', {}).get('value'),
            'multi_static_select': lambda e: [i['value'] for i in e.get('selected_options', {})],
            'datepicker': lambda e: e.get('selected_date'),

        }

        def input_value(ele):
            return input_types[ele['type']](ele)

        input_values = {
            action_id: input_value(action_ele)
            for block_id, block_ele in vsv.items()
            for action_id, action_ele in block_ele.items()
        }

        if callback is None:
            msg = f"No handler for modal submission event: {event}"
            self.log.error(msg)
            return

        return callback(rqst, input_values)

    # -------------------------------------------------------------------------
    # PRIVATE Request handlers - per payload type
    # -------------------------------------------------------------------------

    def _handle_block_action(self, rqst):
        """
        This method is called by handle_interactive_request when the User
        generates an event from a block actions element.  As a result, the code
        associated with this block ID is invoked to ultimately process the
        action event.

        If no callback is associated, the error is logged.

        Parameters
        ----------
        rqst : Request

        Notes
        -----
        https://api.slack.com/reference/interaction-payloads/block-actions

        Returns
        -------
        None
            If no callback is bound to the block ID
        dict
            Response message to send back to api.slack.com
        """
        payload_action = first(rqst.payload['actions'])
        event = payload_action['block_id']
        action = ui.BlockActionEvent(payload_action)
        callback = first(self.ui.block_action.listeners(event))

        if callback is None:
            msg = f"No handler for block action event: {event}"
            self.log.error(msg)
            return

        return callback(rqst, action)

    def _handle_dialog_submit(self, rqst):
        event = rqst.payload['callback_id']
        submission = rqst.payload['submission']
        callback = first(self.ui.dialog.listeners(event))

        if callback is None:
            msg = f'No dialog handler for event {event}'
            self.log.error(msg)
            return ""

        return callback(rqst, submission)

    def _handle_ia_msg_attachment(self, rqst):
        """
        TODO: deprececiate the use of secondary attachmeents.

        Parameters
        ----------
        rqst

        Returns
        -------
        """
        event = rqst.payload['callback_id']
        payload_action = first(rqst.payload['actions'])
        action = ui.InteractiveMessageActionEvent(payload_action)
        callback = first(self.ui.imsg_attch.listeners(event))

        if not callback:
            msg = f"No handler for IMSG action event: {event}"
            self.log.error(msg)
            return

        return callback(rqst, action)

    def add_slash_command(self, cmd, description=None):
        sl_cmd = self.slash_commands[cmd] = SlashCommandCLI(
            app=self, cmd=cmd, description=description
        )
        return sl_cmd

    def error(self, exc):
        emsg = str(exc)
        if exc.args:
            self.log.error("SlackApp ERROR>>\n{}\n".format(emsg))

        raise exc

    def verify_request(self, request) -> bool:
        """
        This function validates the received using the process described
        https://api.slack.com/docs/verifying-requests-from-slack and
        using the code in https://github.com/slackapi/python-slack-events-api

        Parameters
        ----------
        signature: str
        request : flask.request

        Returns
        -------
        bool
            True if signature is validated
            False otherwise
        """
        timestamp = request.headers['X-Slack-Request-Timestamp']

        if abs(time.time() - int(timestamp)) > 60 * 5:
            # The request timestamp is more than five minutes from local time.
            # It could be a replay attack, so let's ignore it.
            return False

        signature = request.headers['X-Slack-Signature']

        req = str.encode('v0:' + str(timestamp) + ':') + request.get_data()

        request_hash = 'v0=' + hmac.new(
            str.encode(self.config.signing_secret),
            req, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(request_hash, signature)
