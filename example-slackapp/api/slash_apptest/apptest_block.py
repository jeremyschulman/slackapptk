from flask import session

from slack.web.classes import extract_json

from slack.web.classes.blocks import (
    SectionBlock,
    ActionsBlock,
    DividerBlock
)
from slack.web.classes.elements import (
    ButtonElement
)

from api.slash_apptest import slashcli
from slackapptk import Response, Request

cmd = slashcli.add_command_option(
    'block', parser_spec=dict(
        help='Run the block test example',
        description='Block test'
    )
)

SESSION_KEY = cmd.prog


def session_init():
    # discard previous if exists
    session.pop(SESSION_KEY, None)
    session[SESSION_KEY] = dict()
    session[SESSION_KEY]['params'] = {}


@slashcli.cli.on(cmd.prog)
def slash_main(rqst, params):
    session_init()
    return main(rqst)


@slashcli.ui.on(cmd.prog)
def ui_main(rqst):
    session_init()
    return main(rqst)


def main(rqst: Request):
    resp = Response(rqst)

    block_id = SESSION_KEY + '.main.button'

    @rqst.app.ic.block_action.on(block_id)
    def _on_button(_rqst, action):
        """ this function will be called when the User clicks on the of buttons defined """
        _resp = Response(_rqst)
        _resp.send(f"At time {action.data['action_ts']}, you pressed: {action.value}")

    user_id = rqst.user_id

    resp['blocks'] = extract_json([
        SectionBlock(text='Hi There!'),
        SectionBlock(text=f'You are <@{user_id}>'),
        DividerBlock(),
        ActionsBlock(
            block_id=block_id,
            elements=[
                ButtonElement(
                    text='Press for Bad',
                    style='danger',
                    action_id=f'{block_id}.bad',
                    value='bad'),
                ButtonElement(
                    text='Press for Good',
                    style="primary",
                    action_id=f'{block_id}.good',
                    value='good')
            ]

        ),
        DividerBlock()
    ])

    res = resp.send()
    if not res.ok:
        rqst.app.log.error(res.text)
