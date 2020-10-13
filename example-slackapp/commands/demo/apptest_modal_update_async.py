"""
/demo async-modal
"""

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from threading import Thread
from time import sleep
import argparse


# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from flask import session

from slack.web.classes.blocks import (
    SectionBlock
)
from slack.web.classes.elements import (
    ButtonElement
)

from slack.web.classes.objects import (
    PlainTextObject
)

# -----------------------------------------------------------------------------
# SlackAppTK Imports
# -----------------------------------------------------------------------------

from slackapptk.request.view import ViewRequest, AnyRequest
from slackapptk.request.command import CommandRequest
from slackapptk.modal import Modal, View
from slackapptk.response import Messenger, Response

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from commands.demo.cli import demo_cmds, slash_demo

# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------

ASYNC_SLEEP_TIME_SEC = 5
MAX_SLEEP_TIME_SEC = 20

# define the CLI parser for the command "/demo async-modal"

cmd = demo_cmds.add_parser(
    'async-modal',
    help='Run the async update modal test example',
    description='Async Update Modal'
)


class DelayArgument(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # optional value
        if not values:
            return

        delay = int(values)
        if not (1 <= delay <= MAX_SLEEP_TIME_SEC):
            parser.error(f"{self.dest} must be between 1 and {MAX_SLEEP_TIME_SEC}.")

        setattr(namespace, self.dest, delay)


cmd.add_argument(
    '--delay',
    help='first boop delay',
    metavar=f"[1..{MAX_SLEEP_TIME_SEC}]",
    action=DelayArgument,
    default=ASYNC_SLEEP_TIME_SEC
)


SESSION_KEY = cmd.prog


def get_origin_data(rqst):
    return {
        'channel': rqst.channel,
        'trigger_id': rqst.trigger_id,
        'response_url': rqst.response_url
    }


def session_init(rqst):
    # discard previous if exists

    session.pop(SESSION_KEY, None)
    user_sdata = session[SESSION_KEY] = dict()

    # save information about the originating request so that we can message
    # back to the User from the context of View launched from a background
    # thread

    user_sdata['__origin__'] = get_origin_data(rqst)

    # the two parameters used by this demo is the number of "boop" ocurrances
    # (counter) and the optional boop-delay that the User can provide via the
    # CLI.

    params = user_sdata['params'] = dict()
    params['delay'] = ASYNC_SLEEP_TIME_SEC
    params['boops'] = 1


@slash_demo.cli.on(cmd.prog)
def slash_main(rqst: CommandRequest, cliargs: argparse.Namespace):
    session_init(rqst)
    session[SESSION_KEY]['params']['delay'] = cliargs.delay

    return main(rqst)


@slash_demo.ic.on(cmd.prog)
def ui_main(rqst):
    session_init(rqst)

    # delete the originating message; just for aesthetics
    Response(rqst).send_response(delete_original=True)

    return main(rqst)


def main(rqst: AnyRequest):

    modal = Modal(
        rqst, callback=on_main_modal_submit,
        view=View(
            type="modal",
            title='First Modal View',
            callback_id=cmd.prog + ".view1",
            close='Cancel',
            submit='Start'))

    modal.view.add_block(
        SectionBlock(text=
            PlainTextObject(text='Click the Start button to begin.')
        )
    )

    res = modal.open()
    if not res.get('ok'):
        rqst.app.log.error(res)


def on_main_modal_submit(rqst):
    modal = Modal(rqst)
    view = modal.view
    view.callback_id = cmd.prog + ".view2"
    view.title = PlainTextObject(text='Awaiting Boop')

    params = session[SESSION_KEY]['params']
    delay = params['delay']

    view.blocks[0] = SectionBlock(
        text=PlainTextObject(text=f"Launching async task for {delay} sec update")
    )

    view.submit = None

    rqst.app.log.debug(modal.view.hash)

    Thread(target=delayed_update_view,
           kwargs={
               'rqst': rqst,
               'view': modal.view,
               'delay': delay
           }).start()

    return modal.update()


def delayed_update_view(rqst: ViewRequest, view: View, delay: int):

    sleep(delay)

    modal = Modal(rqst=rqst, view=view, detached=True)

    # If the User clicks on Done, then the `done_booping` handler will be
    # invoked as a result of the view close.

    modal.notify_on_close = done_booping

    view = modal.view
    view.title = PlainTextObject(text='Booped!')
    view.close = PlainTextObject(text='Done')

    view.blocks[0] = SectionBlock(
        text=PlainTextObject(text=f'First boop after {delay} seconds')
    )

    button = view.add_block(
        SectionBlock(
            text=PlainTextObject(text='Click button to boop again.'),
            block_id=cmd.prog + ".boop"
        )
    )

    button.accessory = ButtonElement(
        text='Boop',
        action_id=button.block_id,
        value='boop'
    )

    rqst.app.ic.block_action.on(
        button.block_id,
        on_boop_button
    )

    res = modal.update()
    if not res.get('ok'):
        rqst.app.log.error(
            f'failed to boop: {res}'
        )


def on_boop_button(rqst):

    params = session[SESSION_KEY]['params']

    params['boops'] += 1
    boops = params['boops']

    modal = Modal(rqst)

    view = modal.view
    view.blocks.pop(0)
    view.blocks.insert(0, SectionBlock(
        text=PlainTextObject(text=f'Boop {boops}')
    ))

    res = modal.update()
    if not res.get('ok'):
        rqst.app.log.error(f'failed to boop: {res}')


def done_booping(rqst: ViewRequest):

    user_sdata = session[SESSION_KEY]

    params = user_sdata['params']
    origin = user_sdata['__origin__']

    messenger = Messenger(
        app=rqst.app,
        response_url=origin['response_url']
    )

    messenger.send_response(text=f"Booped: {params['boops']}")
