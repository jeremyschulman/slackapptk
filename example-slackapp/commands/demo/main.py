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


from slack.web.classes import (
    objects, actions, attachments,
    extract_json
)

from slackapptk.cli import SlashCommandCLI
from slackapptk.request.command import CommandRequest
from slackapptk.response import Response


COLOR_GREEN = '#008000'


def main_demo(
    demo_cmd: SlashCommandCLI,
    rqst: CommandRequest
):

    event_id = demo_cmd.cmd + '.cmd'

    @rqst.app.ic.imsg.on(event_id)
    def on_command_selected(on_rqst, action):
        return demo_cmd.run(on_rqst, event=action.value)

    # Now build the the response message and send the response message.

    resp = Response(rqst)

    resp.text = (
        f"Hi <@{rqst.user_id}>, I see you'd like to run a test command.\n"
        "Let's get started."
    )

    resp['attachments'] = extract_json([
        attachments.InteractiveAttachment(
            text='First please select a *test command*:\n',
            color=COLOR_GREEN,
            callback_id=event_id,
            actions=[
                actions.ActionStaticSelector(
                    name='commands',
                    text='commands ...',
                    options=[
                        objects.Option(label=option, value=command_id)
                        for command_id, option in demo_cmd.get_command_options().items()
                    ])]
        )
    ])

    resp.send_ephemeral()
