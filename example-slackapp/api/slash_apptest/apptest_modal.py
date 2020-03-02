#
# At present slackclient 2.5.0, there are no View and related widgets.  Going to build
# an example "by hand" given the information here:
#
#   https://api.slack.com/reference/surfaces/views
#

import json
from flask import session

from slack.web.classes.blocks import (
    SectionBlock, extract_json
)

from slack.web.classes.elements import (
    ButtonElement, Option,
    DatePickerElement, SelectElement,
    ExternalDataSelectElement
)

# The following are "missing" from the slackclient package, so implemented
# these using their SDK.  Hopefully these widgets will be availbale in a near
# term future release.

from slackapptk import SlackApp
from slackapptk.web.classes.blocks import (
    InputBlock
)

from slackapptk.modal import Modal, View

from slackapptk.web.classes.elements import (
    MultiSelectElement,
    PlainTextElement,
    CheckboxElement
)

from app_data import slackapp
from api.slash_apptest import slashcli


cmd = slashcli.add_command_option(
    'modal', parser_spec=dict(
        help='Run the Modal test example',
        description='Modal Test'
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
    app: SlackApp = rqst.app
    params = session[SESSION_KEY]['params']
    rqst.delete()

    event_id = cmd.prog + ".view1"

    slackapp.ic.view.on(event_id, on_main_modal_submit)

    priv_data = {
        'name': 'Jeremy',
        'state': "NC"
    }

    modal = Modal(rqst)
    view = modal.view = View(
        title='Ohai Modal!',
        callback_id=event_id,
        close='Cacel',
        submit='Next',
        private_metadata=priv_data)

    # -------------------------------------------------------------------------
    # Create a button block:
    # Each time the User clicks it a counter will be incremented by 1.
    # -------------------------------------------------------------------------

    button1 = view.add_block(SectionBlock(
        text="It's Block Kit...but _in a modal_",
        block_id=event_id + ".button1"))

    button1.accessory = ButtonElement(
        text='Click me', value='0',
        action_id=button1.block_id,
        style='danger'
    )

    params['clicks'] = 0

    @app.ic.block_action.on(button1.block_id)
    def remember_button(_onb):
        _params = session[SESSION_KEY]['params']
        _params['clicks'] += 1

    # -------------------------------------------------------------------------
    # Create a Checkboxes block:
    # When the User checks/unchecks the items, they are stored to the session.
    # -------------------------------------------------------------------------

    checkbox_options = [
        Option(label='Box 1', value='A1'),
        Option(label='Box 2', value='B2')
    ]

    params['checkboxes'] = checkbox_options[0].value

    checkbox = view.add_block(SectionBlock(
        text='Nifty checkboxes',
        block_id=event_id + ".checkbox"))

    checkbox.accessory = CheckboxElement(
            action_id=checkbox.block_id,
            options=checkbox_options,
            initial_options=[checkbox_options[0]]
        )

    @app.ic.block_action.on(checkbox.block_id)
    def remember_check(_oncb, action):
        _params = session[SESSION_KEY]['params']
        _params['checkboxes'] = action.value

    # -------------------------------------------------------------------------
    # Create an Input block:
    # Required single line of text.
    # -------------------------------------------------------------------------

    view.add_block(InputBlock(
        label='First input',
        element=PlainTextElement(
            action_id=event_id + ".text1",
            placeholder='Type in here'
        )
    ))

    # -------------------------------------------------------------------------
    # Create an Input block:
    # Optional multi-line text area, maximum 500 characters.
    # -------------------------------------------------------------------------

    host_selector = view.add_block(InputBlock(
        label='Next input',
        optional=True,
        block_id=event_id + ".ext1"))

    host_selector.element = ExternalDataSelectElement(
        placeholder='hosts ..',
        action_id=event_id + ".ext1",
    )

    @app.ic.ext_select.on(host_selector.element.action_id)
    def select_host_from_dynamic_list(_rqst):
        return {
            'options': extract_json([
                Option(label=val, value=val)
                for val in ('lx5e1234', 'lx5w1234', 'lx5e4552')
            ])
        }

    # -------------------------------------------------------------------------
    # Create an Input Datepicker block
    # -------------------------------------------------------------------------

    view.add_block(InputBlock(
        label="Pick a date",
        element=DatePickerElement(
            action_id=event_id + ".datepicker",
            placeholder='A date'
        )
    ))

    # -------------------------------------------------------------------------
    # Create an Input to select from static list, optional.
    # -------------------------------------------------------------------------

    view.add_block(InputBlock(
        label="Select one option",
        optional=True,
        element=SelectElement(
            placeholder='Select one of ...',
            action_id=event_id + ".select_1",
            options=[
                Option(label='this', value='this'),
                Option(label='that', value='that')
            ]
        )
    ))

    # -------------------------------------------------------------------------
    # Create an Input to allow the User to select multiple items
    # from a static list.
    # -------------------------------------------------------------------------

    view.add_block(InputBlock(
        label="Select many option",
        element=MultiSelectElement(
            placeholder='Select any of ...',
            action_id=event_id + ".select_N",
            options=[
                Option(label='cat', value='cat'),
                Option(label='dog', value='dog'),
                Option(label='monkey', value='monkey')
            ]
        )
    ))

    res = modal.open(callback=on_main_modal_submit)
    if not res.get('ok'):
        slackapp.log.error(json.dumps(res, indent=3))


def on_main_modal_submit(rqst, input_values):
    params = session[SESSION_KEY]['params']
    
    # The input_values is a dictionary of key=action_id and value=user-input
    # since all action_id are formulated with dots (.), just use the
    # last token as the variable name when form

    results = {
        k.rpartition('.')[-1]: v
        for k, v in input_values.items()
    }

    results.update(dict(
        clicks=params['clicks'],
        checkboxes=params['checkboxes'],
    ))

    modal = Modal(rqst, view=View(
        title='Modal Results',
        close='Back',
        submit='Done',
        callback_id=cmd.prog + '.modal.last',
        blocks=[
            SectionBlock(
                text="Input results in raw JSON"
            ),
            SectionBlock(
                text="```" + json.dumps(results, indent=3) + "```"
            )
        ]
    ))

    modal.view.clear_on_close = True
    return modal.push(callback=lambda *_: View.clear_all_response())
