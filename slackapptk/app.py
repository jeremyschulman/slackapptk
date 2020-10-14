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

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from logging import getLogger
from typing import Optional, Dict, List
from inspect import signature

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from first import first
import pyee

from slack.web.classes import extract_json
from slack.web.classes import objects as swc_objs

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from slackapptk.errors import SlackAppTKError
from slackapptk.config import SlackAppConfig
from slackapptk.request import view_inputs
from slackapptk.cli import SlashCommandCLI

from slackapptk.request.all import (
    CommandRequest,
    InteractiveRequest,
    BlockActionRequest,
    DialogRequest,
    InteractiveMessageRequest,
    OptionSelectRequest,
    ViewRequest
)

from slackapptk.request.action_event import (
    ActionEvent, BlockActionEvent,
    InteractiveMessageActionEvent
)


__all__ = [
    'SlackApp',
    'SlashCommandCLI'
]


class SlackAppInteractiveHandlers(object):
    def __init__(self):
        self.block_action = pyee.EventEmitter()
        self.dialog = pyee.EventEmitter()
        self.select = pyee.EventEmitter()
        self.imsg = pyee.EventEmitter()
        self.view = pyee.EventEmitter()
        self.view_closed = pyee.EventEmitter()


class SlackAppCommands(object):
    def __init__(self, app):
        self.app = app
        self._registry = dict()

    def register(self, parser):
        cmd = self._registry[parser.prog] = SlashCommandCLI(parser=parser)
        return cmd

    def run(
        self, *,
        name: str,
        rqst: CommandRequest
    ):
        """
        This method is called to process the inbound Slack slash command
        request as invoked by the User.  The calling context is (generally)
        the API route handler.

        Parameters
        ----------
        name : str
            The name of the slash command, as previously registered
            by the slack app

        rqst : CommandRequest
            The inbound API request enrobed as a SlackApp command request
            instance.

        Returns
        -------
        Optional[Dict]
            The results of the code handler that ultimately processes the
            request; which is slash command specific.
        """
        slashcli = self._registry.get(name)
        if not slashcli:
            emsg = f"Unknown slash command name: {name}"
            self.app.log.error(emsg)
            raise SlackAppTKError(emsg, name, rqst)

        return slashcli.run(rqst)


class SlackApp(object):

    def __init__(self):
        self.log = getLogger(__name__)
        self.slash_commands: Dict[str, SlashCommandCLI] = dict()
        self.commands = SlackAppCommands(self)
        self.ic = SlackAppInteractiveHandlers()

        # create callback handler for different interactive payload types.
        #   https://api.slack.com/reference/interaction-payloads
        #   https://api.slack.com/interactivity/handling#payloads

        self._ic_handlers = {

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

    # -------------------------------------------------------------------------
    # HANDLER: slash commands that use the SlashCLI mechanism
    # -------------------------------------------------------------------------

    def handle_slash_command(
        self, *,
        name: str,
        rqst: CommandRequest
    ):
        """
        This method is called to process the inbound Slack slash command
        request as invoked by the User.  The calling context is (generally)
        the API route handler.

        Parameters
        ----------
        name : str
            The name of the slash command, as previously registered
            by the slack app

        rqst : CommandRequest
            The inbound API request enrobed as a SlackApp command request
            instance.

        Returns
        -------
        Optional[Dict]
            The results of the code handler that ultimately processes the
            request; which is slash command specific.
        """
        return self.commands.run(name=name, rqst=rqst)

    # -------------------------------------------------------------------------
    # Request handlers - per payload
    # -------------------------------------------------------------------------

    def handle_interactive_request(
        self,
        rqst: InteractiveRequest
    ) -> Optional[Dict]:
        """
        This method should be called by the API route handler bound to the
        Interactive Compenents, Interactivity "Request URL" configured
        in the api.slack.com site.

        The purpose of this method is to invoke the handler bound to the
        specific type of interactive Request.  Different types of
        interactive messages are handled diffently.

        Parameters
        ----------
        rqst : InteractiveRequest
            The original API request data enrobed in a SlackApp Request instance.

        Returns
        -------
        Optional[Dict]
            When dict, this will be the JSON payload returned to the api.slack.com
            system; i.e. return message as a result of handling this Request.
            If there is no dict-data, then return empty-string, which is required
            by the api.slack.com for response.

        """
        p_type = rqst.rqst_data['type']
        return self._ic_handlers[p_type](rqst)      # noqa

    def handle_select_request(
        self,
        rqst: OptionSelectRequest
    ):
        """

        Parameters
        ----------
        rqst

        Returns
        -------

        Notes
        -----
            https://api.slack.com/reference/block-kit/composition-objects#option_group
        """
        event = rqst.block_id

        callback = first(self.ic.select.listeners(event))
        if not callback:
            msg = f"No handler for ext selector event: {event}"
            self.log.error(msg)
            return

        cal_sig = signature(callback)
        if len(cal_sig.parameters) == 1:
            return callback(rqst)

        action = ActionEvent(
            type=rqst.rqst_type,
            id=rqst.action_id,
            value=rqst.value,
            data={}
        )

        # invoke the callback to retrieve the list of Option or OptionGroup
        # items.  Ensure that the callback did return what we expect, and then
        # return the requird Dict back to api.slack.com

        res_list = callback(rqst, action)
        if not res_list:
            emsg = f'Missing return from select {action.value}, callback: {event}'
            self.log.info(emsg)
            return {'options': []}

        if not isinstance(res_list, List):
            emsg = (f'Unexpected return, not list, from select {action.value}, callback: {event}.  '
                    f'Got {type(res_list)} instead')
            self.log.error(emsg)
            raise SlackAppTKError(emsg, rqst, res_list)

        first_res = first(res_list)
        if isinstance(first_res, swc_objs.Option):
            res_type = 'options'
        elif isinstance(first_res, swc_objs.OptionGroup):
            res_type = 'option_groups'
        else:
            emsg = f'Unknown return type from select callback: {type(first_res)}'
            self.log.error(emsg)
            raise SlackAppTKError(emsg, rqst, res_list)

        return {res_type: extract_json(res_list)}

    # -------------------------------------------------------------------------
    # PRIVATE Request handlers - per payload type
    # -------------------------------------------------------------------------

    def _handle_message_action(self, rqst):
        pass

    def _handle_view_action(
        self,
        rqst: ViewRequest,
        ic_view: pyee.EventEmitter
    ):
        event = rqst.view.callback_id
        callback = first(ic_view.listeners(event))

        if callback is None:
            msg = f"No handler for view event: {event}"
            self.log.error(msg)
            return

        # get the signature of the callback to determine if the callback
        # expects any input results.  If not, then invoke the callback now with
        # the received event.

        cal_sig = signature(callback)
        if len(cal_sig.parameters) == 1:
            return callback(rqst)

        # At this point the caller is expecting input value results, so we need
        # to extract them from the view state values.

        vsv = rqst.view.state_values

        input_values = {
            action_id: view_inputs.get_input_value(action_ele)
            for block_id, block_ele in vsv.items()
            for action_id, action_ele in block_ele.items()
        }

        return callback(rqst, input_values)

    def _handle_view_submission_action(
        self,
        rqst: ViewRequest
    ):
        return self._handle_view_action(rqst, self.ic.view)

    def _handle_view_closed_action(
        self,
        rqst: ViewRequest
    ):
        return self._handle_view_action(rqst, self.ic.view_closed)

    # -------------------------------------------------------------------------
    # PRIVATE request handlers - per payload type
    # -------------------------------------------------------------------------

    def _handle_block_action(
        self,
        rqst: BlockActionRequest
    ):
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
        payload_action = first(rqst.rqst_data['actions'])
        event = payload_action['block_id']
        callback = first(self.ic.block_action.listeners(event))

        if callback is None:
            msg = f"No handler for block action event: {event}"
            self.log.error(msg)
            return

        # check the signature of the callback.  If the callback is not
        # expecting the action value, then invoke the callback now.

        sig_cal = signature(callback)
        if len(sig_cal.parameters) == 1:
            return callback(rqst)

        # the callback is expecting the action payload, so obtain that now and
        # then invoke the callback

        action = BlockActionEvent(payload_action)
        return callback(rqst, action)

    def _handle_dialog_submit(
        self,
        rqst: DialogRequest
    ):
        event = rqst.rqst_data['callback_id']
        submission = rqst.rqst_data['submission']
        callback = first(self.ic.dialog.listeners(event))

        if callback is None:
            msg = f'No dialog handler for event {event}'
            self.log.error(msg)
            return ""

        return callback(rqst, submission)

    def _handle_ia_msg_attachment(
        self,
        rqst: InteractiveMessageRequest
    ):
        """
        TODO: deprececiate the use of secondary attachmeents.

        Parameters
        ----------
        rqst

        Returns
        -------
        """
        event = rqst.rqst_data['callback_id']
        payload_action = first(rqst.rqst_data['actions'])
        action = InteractiveMessageActionEvent(payload_action)
        callback = first(self.ic.imsg.listeners(event))

        if not callback:
            msg = f"No handler for IMSG action event: {event}"
            self.log.error(msg)
            return

        return callback(rqst, action)
