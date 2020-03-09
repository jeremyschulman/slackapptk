import json
from typing import Optional, Dict
from argparse import Namespace

from flask import session

from slack.web.classes import extract_json

from slack.web.classes.blocks import (
    SectionBlock
)

from slack.web.classes.elements import (
    ExternalDataSelectElement,
    Option
)


from slackapptk.response import Response
from slackapptk.request.command import CommandRequest, AnyRequest


from commands.demo.cli import demo_cmd


cmd = demo_cmd.add_subcommand(
    'select', parser_spec=dict(
        help='Run the select from external source test example',
        description='Ext.Select Test'
    ),
    arg_list=[
        ('--host', dict(
            help='switch hostname'
        ))
    ]
)

SESSION_KEY = cmd.prog


def session_init():
    session.pop(SESSION_KEY, None)
    session[SESSION_KEY] = dict()


@demo_cmd.cli.on(cmd.prog)
def slash_main(
    rqst: CommandRequest,
    params: Namespace
):
    session_init()
    cmd_p = session[SESSION_KEY]['params'] = {}
    cmd_p['host'] = params.host
    return main(rqst)


@demo_cmd.ic.on(cmd.prog)
def ui_main(rqst):
    session_init()
    cmd_p = session[SESSION_KEY]['params'] = {}
    cmd_p['host'] = ''
    return main(rqst)


def main(rqst: AnyRequest) -> Optional[Dict]:
    cmd_p = session[SESSION_KEY]['params']

    # If the User provided the host value on the CLI, then send back their
    # selection in an ephemeral message; and they are done with this test
    # work-flow.

    if cmd_p['host']:
        resp = Response(rqst)
        resp.send_ephemeral(
            f"You selected host {cmd_p['host']}"
        )
        return

    event_id = SESSION_KEY + ".select"

    # -------------------------------------------------------------------------
    # Create a response that uses an External Selector
    # Use a callback function to populate the dynamtic data; so while it is a
    # static list of dynamic data, the protocol for originating the data is
    # dynamic ;-).  Once the User selects an item, send their selection back as
    # an ephemeral message.
    # -------------------------------------------------------------------------

    host_selector = SectionBlock(
        text='Enter a hostname, provide at least 3 letters',
        block_id=event_id,
        accessory=ExternalDataSelectElement(
            placeholder='host ...',
            action_id=event_id,
            min_query_length=3
        )
    )

    app = rqst.app

    @app.ic.select.on(host_selector.accessory.action_id)
    def select_host_from_dynamic_list(_rqst):
        return {
            'options': extract_json([
                Option(label=val, value=val)
                for val in ('lx5e1234', 'lx5w1234', 'lx5e4552')
            ])
        }

    @app.ic.block_action.on(host_selector.accessory.action_id)
    def host_selected(_rqst, action):
        _resp = Response(_rqst)
        _resp.send_ephemeral(
            f"You selected host of value: {action.value}"
        )

    # -------------------------------------------------------------------------

    resp = Response(rqst)

    resp['blocks'] = extract_json([
        host_selector
    ])

    res = resp.send()
    if not res.ok:
        app.log.error(json.dumps(res, indent=3))

    return
