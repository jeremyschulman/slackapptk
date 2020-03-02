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

from flask import request

from slack.web.classes import (
    objects, actions, attachments,
    extract_json
)

from slackapptk import CommandRequest, Response
from slackapptk.request import action_event

from blueprint import blueprint
from app_data import slackapp
from api.slash_apptest import slashcli

SESSION_KEY = slashcli.cmd


@blueprint.route(f"/slack/command/{slashcli.cmd}", methods=['POST'])
def slackcmd_apptest():

    # clear the active command for the User if one exists, and
    # then setup the session data for use.

    rqst = CommandRequest(app=slackapp, request=request)

    # -------------------------------------------------------------------------
    # if the user provide more than just the slash command, process the
    # CLI text and "jump directly to" the right code that handles the
    # specific command & options.
    # -------------------------------------------------------------------------

    if len(rqst.argv):
        return slashcli.run(rqst)

    # -------------------------------------------------------------------------
    # if the User did not provide a specific test option, then we need to send
    # a response message back that allows them to select one of the test
    # command options.  Once they select the option we need to use that
    # selection value to execute the specific test command code.
    # -------------------------------------------------------------------------

    # the `event_id` is a global unique value that will be use to route the
    # User selection to the callback function.  We define and register the
    # callback function before we send the response message to the User.

    event_id = SESSION_KEY + '.cmd'

    @rqst.app.ic.imsg_attch.on(event_id)
    def on_command_selected(on_rqst, action):
        return slashcli.run(on_rqst, event=action.value)

    # Now build the the response message and send the response message.

    resp = Response(rqst)

    resp.text = (
        f"Hi <@{rqst.user_id}>, I see you'd like to run a test command.\n"
        "Let's get started."
    )

    resp['attachments'] = extract_json([
        attachments.InteractiveAttachment(
            text='First please select a *test command*:\n',
            color=action_event.COLOR_GREEN,
            callback_id=event_id,
            actions=[
                actions.ActionStaticSelector(
                    name='commands',
                    text='commands ...',
                    options=[
                        objects.Option(label=option, value=command_id)
                        for command_id, option in slashcli.get_command_options().items()
                    ])]
        )
    ])

    res = resp.send_ephemeral()

    if not res.get('ok'):
        slackapp.error()

    return ""
