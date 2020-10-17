"""
/demo modal

This file demonstrates the use of Modals and Input widgets.  This
example also uses the flask sessions infrastructure to store values
when the User interacts with Buttons and other components.
"""
# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import json
from typing import Dict

from commands.demo.cli import demo_cmds, slash_demo
from flask import session
from slack.web.classes import extract_json
from slack.web.classes.blocks import InputBlock, SectionBlock
from slack.web.classes.elements import (ButtonElement, CheckboxesElement,
                                        DatePickerElement,
                                        ExternalDataSelectElement, Option,
                                        PlainTextInputElement, SelectElement,
                                        StaticMultiSelectElement)
from slack.web.classes.objects import MarkdownTextObject, PlainTextObject
from slackapptk.app import SlackApp
from slackapptk.modal import Modal, View
from slackapptk.request.all import ActionEvent, BlockActionRequest, ViewRequest
from slackapptk.response import Response

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------






# -----------------------------------------------------------------------------
# SlackAppTK Imports
# -----------------------------------------------------------------------------




# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#
#                                 CODE BEGINS
#
# -----------------------------------------------------------------------------


# create a Argsparser for the "/demo modal" command

cmd = demo_cmds.add_parser(
    'modal',
    help='Run the Modal test example',
    description='Modal Test'
)


# The user session key will be the program name of the parser, i.e. "demo
# modal" but demonstrating this use programatically.  The User interactions
# will be stored in the sessions in 'params'.

SESSION_KEY = cmd.prog


def session_init():
    # discard previous if exists
    session.pop(SESSION_KEY, None)
    session[SESSION_KEY] = dict()
    session[SESSION_KEY]['params'] = {}


# bind the entrypoint handler when the User enters the complete "/demo modal"
# from the Slack client.

@slash_demo.cli.on(cmd.prog)
def slash_main(rqst):
    session_init()
    return main(rqst)


# bind the entrypoint handler for when the User selects the modal demo from the
# main /demo menu-select.

@slash_demo.ic.on(cmd.prog)
def ui_main(rqst):
    session_init()

    # delete the originating message; just for aesthetics
    Response(rqst).send_response(delete_original=True)

    return main(rqst)


def main(rqst):

    app: SlackApp = rqst.app
    params = session[SESSION_KEY]['params']

    # define the event ID for when the User clicks the Submit button on the
    # Modal. bind that event to the code handler that will process the data.

    event_id = cmd.prog + ".view1"
    app.ic.view.on(event_id, on_main_modal_submit)

    priv_data = {
        'name': 'Jeremy',
        'state': "NC"
    }

    # create a Modal instace, which will also defined a View when one is not
    # provided.  Tie the submit callback ID to the envent_id value

    modal = Modal(rqst)
    view = modal.view = View(
        type="modal",
        title=PlainTextObject(text="Awesome Modal"),
        callback_id=event_id,
        close=PlainTextObject(text="Cancel"),
        submit=PlainTextObject(text="Next"),
        private_metadata=str(priv_data))

    # -------------------------------------------------------------------------
    # Create a button block:
    # Each time the User clicks it a counter will be incremented by 1.
    # The button click count is stored in the session params.
    # -------------------------------------------------------------------------

    button1 = view.add_block(SectionBlock(
        text=PlainTextObject(text="It's Block Kit...but _in a modal_"),
        block_id=event_id + ".button1"))

    button1.accessory = ButtonElement(
        text='Click me', value='0',
        action_id=button1.block_id,
        style='danger'
    )

    params['clicks'] = 0

    # noinspection PyUnusedLocal
    @app.ic.block_action.on(button1.block_id)
    def remember_button(btn_rqst: BlockActionRequest):
        session[SESSION_KEY]['params']['clicks'] += 1

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
        text=PlainTextObject(text='Nifty checkboxes'),
        block_id=event_id + ".checkbox"))

    checkbox.accessory = CheckboxesElement(
            action_id=checkbox.block_id,
            options=checkbox_options,
            initial_options=[checkbox_options[0]]
        )

    @app.ic.block_action.on(checkbox.block_id)
    def remember_check(cb_rqst: BlockActionRequest, action: ActionEvent):
        session[SESSION_KEY]['params']['checkboxes'] = action.value

    # -------------------------------------------------------------------------
    # Create an Input block:
    # Required single line of text.
    # -------------------------------------------------------------------------

    view.add_block(InputBlock(
        label=PlainTextObject(text='First input'),
        element=PlainTextInputElement(
            action_id=event_id + ".text1",
            placeholder='Type in here'
        )
    ))

    # -------------------------------------------------------------------------
    # Create an Input block:
    # Optional multi-line text area, maximum 500 characters.
    # -------------------------------------------------------------------------

    host_selector = view.add_block(InputBlock(
        label=PlainTextObject(text='Next input selector ... start typing'),
        optional=True,
        block_id=event_id + ".ext1",
        element=ExternalDataSelectElement(
                    placeholder='hosts ..',
                    action_id=event_id + ".ext1",)
        ))

    @app.ic.select.on(host_selector.element.action_id)
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
        label=PlainTextObject(text="Pick a date"),
        element=DatePickerElement(
            action_id=event_id + ".datepicker",
            placeholder='A date'
        )
    ))

    # -------------------------------------------------------------------------
    # Create an Input to select from static list, optional.
    # -------------------------------------------------------------------------

    view.add_block(InputBlock(
        label=PlainTextObject(text="Select one option"),
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
        label=PlainTextObject(text="Select many option"),
        element=StaticMultiSelectElement(
            placeholder=PlainTextObject(text='Select any of ...'),
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
        app.log.error(json.dumps(res, indent=3))


def on_main_modal_submit(
    rqst: ViewRequest,
    input_values: Dict
):
    params = session[SESSION_KEY]['params']

    # The input_values is a dictionary of key=action_id and value=user-input
    # since all action_id are formulated with dots (.), just use the
    # last token as the variable name when form

    results = {
        k.rpartition('.')[-1]: v
        for k, v in input_values.items()
    }

    results.update(dict(
        clicks=params['clicks']
    ))

    modal = Modal(rqst, view=View(
        type="modal",
        title=PlainTextObject(text='Modal Results'),
        close=PlainTextObject(text='Done'),
        clear_on_close=True,
        blocks=[
            SectionBlock(
                text=PlainTextObject(text="Input results in raw JSON")
            ),
            SectionBlock(
                text=MarkdownTextObject(text="```" + json.dumps(results, indent=3) + "```")
            )
        ]
    ))

    return modal.push()
