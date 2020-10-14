"""
This file contains a demonstration of using the slackclient DialogBuilder
widget to create a (outmoded) Dialog that allows the User to enter some basic
text fields and then returns a message with the contents of their input.
"""
# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import json

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from slack.web.classes import (
    dialogs, blocks
)

from slack.web.classes.objects import (
    MarkdownTextObject
)

# -----------------------------------------------------------------------------
# SlackAppTK Imports
# -----------------------------------------------------------------------------

from slackapptk.response import Response

from slackapptk.request.all import (
    AnyRequest,
    InteractiveMessageRequest,
    CommandRequest,
    DialogRequest
)

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .cli import slash_demo, demo_cmds

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

# create an argsparser for the '/demo dialog' command

cmd = demo_cmds.add_parser(
    'dialog',
    help='Run the dialog test example',
    description='Dialog Test'
)


# bind a callback for when the User enters the complete "/demo dialog" in the
# Slack client.

@slash_demo.cli.on(cmd.prog)
def slash_main(rqst: CommandRequest):
    return main(rqst)


# bind a callback for when the User selects this demo from the /demo message
# containing the menu-selector.

@slash_demo.ic.on(cmd.prog)
def ui_main(rqst: InteractiveMessageRequest):

    # delete the originating message; just for aesthetics
    Response(rqst).send_response(delete_original=True)

    return main(rqst)


def main(rqst: AnyRequest):

    # define the event trigger ID that will be used to associate the dialog
    # submit button with the callback handler on the event to process the
    # User's inputs.

    event_id = cmd.prog + ".dialog"

    rqst.app.ic.dialog.on(event_id, on_dialog_submit)

    # create the dialog wiedget using slackclient

    builder = (dialogs.DialogBuilder()
               .title("My Cool Dialog")
               .callback_id(event_id)
               .state({'value': 123, 'key': "something"})
               .text_area(name="message", label="Message", hint="Enter a message", max_length=500)
               .text_field(name="signature", label="Signature", optional=True, max_length=50))

    # send the dialog to the User for processsing, the `dialog_open` is a
    # method of the slackclient instance

    resp = Response(rqst)
    res = resp.client.dialog_open(dialog=builder.to_dict(),
                                  trigger_id=rqst.trigger_id)

    if not res.get('ok'):
        rqst.app.log.error(json.dumps(res))


def on_dialog_submit(rqst: DialogRequest, submit):
    # when the User clicks submit from the dialog, this function is called and
    # a response message is send to the User showing their inputs; as well as a
    # state variable that was hardcoded.

    resp = Response(rqst)

    resp['blocks'] = [
        blocks.SectionBlock(text=MarkdownTextObject(text=f"""
Your selections:\n
*message*: {submit['message']}
*signature*: {submit['signature']}\n
*state* `value`: {rqst.state['value']} (hardcoded in demo)
""")).to_dict()
    ]

    res = resp.send_response()
    # if res.status != 200:
    #     rqst.app.log.error(json.dumps(res))
    #
