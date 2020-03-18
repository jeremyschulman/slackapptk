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
"""
This file contains the /demo main hander which is invoked when the User
executes the /demo command without any other options.  As a result they will be
presented with a Message containing a menu-selection of demo commands.  When
they make a selection from that drop-down, the specific sub-command demo code
is executed.
"""

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from slack.web.classes import (
    objects, actions, attachments,
    extract_json
)

# -----------------------------------------------------------------------------
# SlackAppTK Imports
# -----------------------------------------------------------------------------

from slackapptk.request.command import CommandRequest
from slackapptk.response import Response

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .cli import demo_parser, slash_demo

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


COLOR_GREEN = '#008000'


@slash_demo.cli.on(demo_parser.prog)
def main_demo(rqst: CommandRequest):

    # The callback_id will be based on the parser prog name, which is "demo" in
    # this case; but showing the use programatically.  This value will be used
    # to bind to the Slack message options and the callback which will be used
    # to run the command associated with the User's selection.

    callback_id = demo_parser.prog

    # create a Slack message that will be used to respond to the User's
    # interaction which was the invocation of the /demo command.

    resp = Response(rqst)

    resp['text'] = (
        f"Hi <@{rqst.user_id}>, I see you'd like to run a test command.\n"
        "Let's get started."
    )

    # The message will contain an attachment with a static menu selector
    # (drop-down) of the demo commands available.  These choices are based on
    # the CLI sub parser items; which are made available through a `choices`
    # property of the SlackAppTKParser instance.

    demo_choices = demo_parser.choices

    # Using those command choices, create a list of Option widgets whose label
    # comes from the CLI command help string and the value is the CLI program
    # name.  The CLI sub command program name value will be used when the User
    # makes a dropdown choice.

    demo_options = [objects.Option(label=parser.help, value=parser.prog)
                    for prog, parser in demo_choices.items()]

    # Create the message attachment interactive message that contains the
    # statick menu selector.  Notice that the callback_id value is set to to
    # the value that is the toplevel /demo program name.

    resp['attachments'] = extract_json([
        attachments.InteractiveAttachment(
            text='First please select a *test command*:\n',
            color=COLOR_GREEN,
            callback_id=callback_id,
            actions=[
                actions.ActionStaticSelector(
                    name='commands',
                    text='commands ...',
                    options=demo_options)]
        )
    ])

    # bind the callback_id so that when the User makes a selection from the
    # drop-down, the option value (which is the sub command program name) is
    # used by the slash_demo instance to route the request to the correct
    # sub-command handler.

    @rqst.app.ic.imsg.on(callback_id)
    def on_command_selected(on_rqst, action):
        return slash_demo.run(on_rqst, event=action.value)

    # Now send the message to the User for interaction
    resp.send()
