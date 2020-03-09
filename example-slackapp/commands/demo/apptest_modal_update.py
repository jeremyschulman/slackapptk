from flask import session
from argparse import Namespace

from slack.web.classes.blocks import (
    SectionBlock
)

from slackapptk.response import Response
from slackapptk.request.any import AnyRequest
from slackapptk.request.view import ViewRequest
from slackapptk.request.command import CommandRequest

from slackapptk.modal import Modal, View
from commands.demo.cli import demo_cmd


cmd = demo_cmd.add_subcommand(
    'update-modal', parser_spec=dict(
        help='Run the update modal test example',
        description='Update Modal'
    )
)

SESSION_KEY = cmd.prog


def session_init():
    # discard previous if exists
    session.pop(SESSION_KEY, None)
    session[SESSION_KEY] = dict()
    session[SESSION_KEY]['params'] = {}


@demo_cmd.cli.on(cmd.prog)
def slash_main(
    rqst: CommandRequest,
    params: Namespace
):
    session_init()
    return main(rqst)


@demo_cmd.ic.on(cmd.prog)
def ui_main(rqst: AnyRequest):
    session_init()
    return main(rqst)


def main(rqst: AnyRequest):
    Response(rqst).send(delete_original=True)

    modal = Modal(rqst)

    modal.view = View(title='First Modal View',
                      callback_id=cmd.prog + ".view1",
                      close='Cacel',
                      submit='Next')

    res = modal.open(callback=on_main_modal_submit)
    if not res.get('ok'):
        rqst.app.log.error(res)


def on_main_modal_submit(rqst: ViewRequest):
    modal = Modal(rqst)
    modal.view.callback_id = cmd.prog + ".view2"
    modal.view.add_block(SectionBlock(text="New bits."))
    return modal.update(callback=on_view2_submit)


def on_view2_submit(rqst: ViewRequest):
    modal = Modal(rqst)
    view = modal.view
    view.submit = None
    view.blocks.pop()
    view.add_block(SectionBlock(text='Next new bit.'))

    return modal.update()
