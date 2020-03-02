from flask import session

from slack.web.classes.blocks import (
    SectionBlock
)

from slackapptk import Request, CommandRequest, ViewRequest
from slackapptk.modal import Modal, View
from api.slash_apptest import slashcli


cmd = slashcli.add_command_option(
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


@slashcli.cli.on(cmd.prog)
def slash_main(rqst: CommandRequest, params):
    session_init()
    return main(rqst)


@slashcli.ui.on(cmd.prog)
def ui_main(rqst: Request):
    session_init()
    return main(rqst)


def main(rqst: Request):
    rqst.delete()

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
