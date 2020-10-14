"""
/demo update-modal

This demonstration will show the use of Modal View "update" by taking
the User through three modal views.
"""

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from slack.web.classes.blocks import (
    SectionBlock
)

from slack.web.classes.objects import (
    PlainTextObject, MarkdownTextObject
)

# -----------------------------------------------------------------------------
# SlackAppTK Imports
# -----------------------------------------------------------------------------

from slackapptk.response import Response

from slackapptk.request.any import AnyRequest

from slackapptk.request.view import ViewRequest

from slackapptk.request.command import CommandRequest

from slackapptk.modal import Modal, View

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from commands.demo.cli import demo_cmds, slash_demo

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

# create an Argsparser for the "/demo update-modal" command.

cmd = demo_cmds.add_parser(
    'update-modal',
    help='Run the update modal test example',
    description='Update Modal'
)


# bind the entrypoint handler for when the User enters the complete "/demo
# update-modal" command in the Slack client.

@slash_demo.cli.on(cmd.prog)
def slash_main(rqst: CommandRequest):
    return main(rqst)


# bind the entrypoint handler for when the User selects this demo item from the
# /demo menu-selector

@slash_demo.ic.on(cmd.prog)
def ui_main(rqst: AnyRequest):

    # delete the originating message; just for aesthetics
    Response(rqst).send_response(delete_original=True)

    return main(rqst)


def main(rqst: AnyRequest):

    # create a Modal and view, setting the callback so that when the User
    # clicks the "Next" button the code in on_main_modal_submit will be used as
    # the handler.

    Modal(
        rqst, callback=on_main_modal_submit,
        view=View(
            type="modal",
            title='First Modal View',
            callback_id=cmd.prog + ".view1",
            close='Cancel',
            submit='Next',
            blocks=[SectionBlock(text=MarkdownTextObject(text="This is the *first* modal view."))]
        )
    ).open()


def on_main_modal_submit(rqst: ViewRequest):

    # define the modal and view based on the received view request from
    # api.slack.com as a result of this instance, the code can then "update"
    # the view by returning the update payload as a resposse message.

    modal = Modal(rqst)

    view = modal.view
    view.title = PlainTextObject(text=('Second Modal View'))

    view.callback_id = cmd.prog + ".view2"
    modal.callback = on_view2_submit

    view.add_block(SectionBlock(text=MarkdownTextObject(text="This is the *second* modal view.")))

    return modal.update()


def on_view2_submit(rqst: ViewRequest):

    # same technique as on_main_modal_submit; in this case disable the submit
    # button only allow the User to click the "Done" (close) button.

    modal = Modal(rqst)

    view = modal.view
    view.title = PlainTextObject(text='Final Modal View')
    view.close = PlainTextObject(text='Done')
    view.submit = None

    view.add_block(SectionBlock(text=MarkdownTextObject(text='Final bit.')))

    return modal.update()
