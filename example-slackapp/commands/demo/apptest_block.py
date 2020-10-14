"""
/demo block

The purpose of this demo is to create a response back to the User that gives
them two buttons to click.  When the User clicks on eitehr button a message is
sent back to them indicating their choice.
"""

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Union

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from slack.web.classes import extract_json

from slack.web.classes.blocks import (
    SectionBlock,
    ActionsBlock,
    DividerBlock
)
from slack.web.classes.elements import (
    ButtonElement
)

from slack.web.classes.objects import (
    MarkdownTextObject
)

# -----------------------------------------------------------------------------
# SlackAppTK Imports
# -----------------------------------------------------------------------------

from slackapptk.request.all import (
    InteractiveMessageRequest,
    CommandRequest,
    BlockActionRequest, ActionEvent
)
from slackapptk.response import Response

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from commands.demo.cli import slash_demo, demo_cmds

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

# define the CLI command "/demo blocks"

cmd = demo_cmds.add_parser(
    'block',
    help='Run the block test example',
    description='Block test'
)


# bind the entrypoint handler for when the User enters the complete "/demo
# block" command in the Slack client.

@slash_demo.cli.on(cmd.prog)
def slash_main(rqst: CommandRequest):
    return main(rqst)


# bind the entrypoint handler for when the User selects this demo item from the
# /demo menu-selector

@slash_demo.ic.on(cmd.prog)
def ui_main(rqst: InteractiveMessageRequest):
    resp = Response(rqst)
    resp.send_response(delete_original=True)

    return main(rqst)


def main(rqst: Union[InteractiveMessageRequest, CommandRequest]) -> None:

    block_id = cmd.prog + '.main.button'

    # create a Slack message that will be used to respond to the User's
    # interaction which was the invocation of the /demo command.

    resp = Response(rqst)

    # -------------------------------------------------------------------------
    # define the button callback handler to send a response back to the
    # User telling the time when they pressed the button
    # -------------------------------------------------------------------------

    @rqst.app.ic.block_action.on(block_id)
    def on_button(btn_rqst: BlockActionRequest,
                  btn_action: ActionEvent):

        btn_resp = Response(btn_rqst)

        btn_resp.send_response(text=(
            f"At timestamp `{btn_action.data['action_ts']}`, "
            f"you pressed: *{btn_action.value.title()}*")
        )

    # -------------------------------------------------------------------------
    # create a message to send to the User that has two buttons; and when
    # they click either one, the above callback will be executed.
    # -------------------------------------------------------------------------

    user_id = rqst.user_id

    resp['blocks'] = extract_json([
        SectionBlock(text=MarkdownTextObject(text=f'Hi there <@{user_id}>!')),
        DividerBlock(),
        ActionsBlock(
            block_id=block_id,
            elements=[
                ButtonElement(
                    text='Press for Bad', style='danger',
                    action_id=f'{block_id}.bad',
                    value='bad'),
                ButtonElement(
                    text='Press for Good', style="primary",
                    action_id=f'{block_id}.good',
                    value='good')
            ]

        ),
        DividerBlock()
    ])

    resp.send()
