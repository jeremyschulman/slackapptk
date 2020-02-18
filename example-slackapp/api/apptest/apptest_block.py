from flask import session

from slack.web.classes import (
    extract_json,
    blocks, elements
)

from app_data import slackapp

_g_slash_command = slackapp.slash_commands['/apptest']

cmd = _g_slash_command.add_command_option(
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


@_g_slash_command.cli.on(cmd.prog)
def slash_main(rqst, params):
    session_init()
    return main(rqst)


@_g_slash_command.ui.on(cmd.prog)
def ui_main(rqst):
    session_init()
    return main(rqst)


def main(rqst):
    resp = rqst.ResponseMessage()

    block_id = SESSION_KEY + '.main.button'

    @rqst.app.ui.block_action.on(block_id)
    def _on_button(onb_rqst, action):
        """ this function will be called when the User clicks on the of buttons defined """
        onb_resp = onb_rqst.ResponseMessage()
        onb_resp.send(f"At time {action.data['action_ts']}, you pressed: {action.value}")

    user_id = rqst.user_id

    resp['blocks'] = extract_json([
        blocks.SectionBlock(text='Hi There!'),
        blocks.SectionBlock(text=f'You are <@{user_id}>'),
        blocks.DividerBlock(),
        blocks.ActionsBlock(
            block_id=block_id,
            elements=[
                elements.ButtonElement(
                    text='Press for Bad',
                    style='danger',
                    action_id=f'{block_id}.bad',
                    value='bad'),
                elements.ButtonElement(
                    text='Press for Good',
                    style="primary",
                    action_id=f'{block_id}.good',
                    value='good')
            ]

        ),
        blocks.DividerBlock()
    ])

    resp.send().raise_for_status()
