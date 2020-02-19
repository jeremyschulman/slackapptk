from flask import session

from slack.web.classes import (
    extract_json, dialogs, blocks
)

from api.slash_apptest.apptest_slashcli import slashcli


cmd = slashcli.add_command_option(
    'dialog', parser_spec=dict(
        help='Run the dialog test example',
        description='Dialog Test'
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


def main(rqst):
    rqst.delete()

    resp = rqst.ResponseMessage()

    event_id = cmd.prog + ".dialog"

    rqst.app.ui.dialog.on(event_id, on_dialog_submit)

    builder = (dialogs.DialogBuilder()
               .title("My Cool Dialog")
               .callback_id(event_id)
               .state({'value': 123, 'key': "something"})
               .text_area(name="message", label="Message", hint="Enter a message", max_length=500)
               .text_field(name="signature", label="Signature", optional=True, max_length=50))

    res = resp.client.dialog_open(dialog=builder.to_dict(),
                                  trigger_id=rqst.trigger_id)


def on_dialog_submit(rqst, submit):
    resp = rqst.ResponseMessage()

    resp['blocks'] = extract_json([
        blocks.SectionBlock(text=f"""
Your selections:\n
*message*: {submit['message']}

*signature*: {submit['signature']}\n            

*state `value`*: {rqst.state['value']}
""")
    ])

    resp.send()
