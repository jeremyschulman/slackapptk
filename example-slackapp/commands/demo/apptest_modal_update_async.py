from threading import Thread
from time import sleep
from argparse import Namespace

from flask import session

from slack.web.classes.blocks import (
    SectionBlock
)
from slack.web.classes.elements import (
    ButtonElement
)

from slackapptk.request.view import ViewRequest, AnyRequest
from slackapptk.response import Response
from slackapptk.request.command import CommandRequest

from slackapptk.modal import Modal, View
from commands.demo.cli import demo_cmd


cmd = demo_cmd.add_subcommand(
    'async-modal', parser_spec=dict(
        help='Run the async update modal test example',
        description='Async Update Modal'
    )
)

SESSION_KEY = cmd.prog


def session_init():
    # discard previous if exists
    session.pop(SESSION_KEY, None)
    session[SESSION_KEY] = dict()
    params = session[SESSION_KEY]['params'] = {}
    params['boops'] = 0


@demo_cmd.cli.on(cmd.prog)
def slash_main(
    rqst: CommandRequest,
    params: Namespace
):
    session_init()
    return main(rqst)


@demo_cmd.ic.on(cmd.prog)
def ui_main(rqst):
    session_init()
    return main(rqst)


def main(rqst: AnyRequest):
    Response(rqst).send(delete_original=True)

    modal = Modal(
        rqst,
        view=View(
            title='First Modal View',
            callback_id=cmd.prog + ".view1",
            close='Cacel',
            submit='Start'),
        callback=on_main_modal_submit)

    modal.view.add_block(
        SectionBlock(
            text='Click the Start button to begin.'
        )
    )

    res = modal.open()

    if not res.get('ok'):
        rqst.app.log.error(res)


def on_main_modal_submit(rqst):
    modal = Modal(rqst)
    view = modal.view
    view.callback_id = cmd.prog + ".view2"
    view.title = 'Awaiting Boop'
    view.blocks[0] = SectionBlock(
        text="Launching async task for 5 sec update"
    )

    view.submit = None

    rqst.app.log.debug(modal.view.view_hash)

    Thread(target=delayed_update_view,
           kwargs={
               'rqst': rqst,
               'view': modal.view
           }).start()

    return modal.update()


def delayed_update_view(*_vargs, rqst: ViewRequest, view: View):
    sleep(5)

    modal = Modal(rqst=rqst, view=view, detached=True)
    modal.view.title = 'Booped!'
    modal.view.close = 'Done'

    view.blocks[0] = SectionBlock(
        text='First boop after 5 seconds'
    )

    button = view.add_block(
        SectionBlock(
            text='Click button to boop again.',
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
        text=f'Boop {boops}'
    ))

    modal.notify_on_close = done_booping

    res = modal.update()
    if not res.get('ok'):
        rqst.app.log.error(
            f'failed to boop: {res}'
        )


def done_booping(rqst: ViewRequest):
    params = session[SESSION_KEY]['params']
    print(f"Booped: {params['boops']}")
