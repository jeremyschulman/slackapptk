#
# At present slackclient 2.5.0, there are no View and related widgets.  Going to build
# an example "by hand" given the information here:
#
#   https://api.slack.com/reference/surfaces/views
#

import json
from flask import session

from slack.web.classes import (
    extract_json,
    blocks, elements,
    objects
)

from slackapp2pyez.web.classes.blocks import InputBlock
from slackapp2pyez.web.classes.elements import (
    MultiSelectElement,
    PlainTextElement,
    CheckboxElement
)

from app_data import slackapp

_g_slash_command = slackapp.slash_commands['/apptest']

cmd = _g_slash_command.add_command_option(
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


@_g_slash_command.cli.on(cmd.prog)
def slash_main(rqst, params):
    session_init()
    return main(rqst)


@_g_slash_command.ui.on(cmd.prog)
def ui_main(rqst):
    session_init()
    return main(rqst)


def main(rqst):
    params = session[SESSION_KEY]['params']

    rqst.delete()

    event_id = cmd.prog + ".modal"

    action_ids = params['action_ids'] = {}
    action_ids['text1'] = event_id + ".input1"
    action_ids['text2'] = event_id + ".input2"
    action_ids['datepick'] = event_id + ".datepick"
    action_ids['button1'] = event_id + ".button1"
    action_ids['checkbox'] = event_id + ".checkbox"
    action_ids['select1'] = event_id + ".select1"
    action_ids['selectN'] = event_id + ".selectN"

    slackapp.ui.modal.on(event_id, on_main_modal_submit)

    priv_data = {
        'name': 'Jeremy',
        'state': "NC"
    }

    resp = rqst.ResponseMessage()

    pto_dfs = objects.PlainTextObject.direct_from_string

    resp['type'] = 'modal'
    resp['title'] = pto_dfs('Ohai Modal!')
    resp['close'] = pto_dfs('Cancel')
    resp['submit'] = pto_dfs('Next')
    resp['callback_id'] = event_id
    resp['private_metadata'] = json.dumps(priv_data)

    checkbox_options = [
        elements.Option(label='Box 1', value='A1'),
        elements.Option(label='Box 2', value='B2')
    ]

    params['clicks'] = 0
    params['checkboxes'] = checkbox_options[0].value

    @slackapp.ui.block_action.on(action_ids['button1'])
    def remember_button(_onb, action):
        _params = session[SESSION_KEY]['params']
        _params['clicks'] += 1

    @slackapp.ui.block_action.on(action_ids['checkbox'])
    def remember_check(_oncb, action):
        _params = session[SESSION_KEY]['params']
        _params['checkboxes'] = action.value

    resp['blocks'] = extract_json([
        blocks.SectionBlock(
            text="It's Block Kit...but _in a modal_",
            accessory=elements.ButtonElement(
                text='Click me', value='0',
                action_id=action_ids['button1'],
                style='danger'
            )
        ),
        blocks.SectionBlock(
            text='Nifty checkboxes',
            accessory=CheckboxElement(
                action_id=action_ids['checkbox'],
                options=checkbox_options,
                initial_options=[checkbox_options[0]]
            )
        ),
        InputBlock(
            label='First input',
            element=PlainTextElement(
                action_id=action_ids['text1'],
                placeholder='Type in here'
            )
        ),
        InputBlock(
            label='Next input',
            optional=True,
            element=PlainTextElement(
                action_id=action_ids['text2'],
                multiline=True,
                max_length=500
            )
        ),
        InputBlock(
            label="Pick a date",
            element=elements.DatePickerElement(
                action_id=action_ids['datepick'],
                placeholder='A date'
            )
        ),
        InputBlock(
            label="Select one option",
            optional=True,
            element=elements.SelectElement(
                placeholder='Select one of ...',
                action_id=action_ids['select1'],
                options=[
                    elements.Option(label='this', value='this'),
                    elements.Option(label='that', value='that')
                ]
            )
        ),
        InputBlock(
            label="Select many option",
            element=MultiSelectElement(
                placeholder='Select any of ...',
                action_id=action_ids['selectN'],
                options=[
                    elements.Option(label='cat', value='cat'),
                    elements.Option(label='dog', value='dog'),
                    elements.Option(label='monkey', value='monkey')
                ]
            )
        )

    ])

    res = resp.client.views_open(trigger_id=rqst.trigger_id,
                                 view=dict(resp))

    if not res.get('ok'):
        slackapp.log.error(json.dumps(res, indent=3))


def on_main_modal_submit(rqst, input_values):
    params = session[SESSION_KEY]['params']
    action_ids = params['action_ids']

    results = dict(
        text1=input_values[action_ids['text1']],
        text2=input_values[action_ids['text2']],
        datepick=input_values[action_ids['datepick']],
        clicks=params['clicks'],
        checkboxes=params['checkboxes'],
        select1=input_values[action_ids['select1']],
        selectn=input_values[action_ids['selectN']]
    )

    resp = rqst.ResponseMessage()

    pto_dfs = objects.PlainTextObject.direct_from_string

    event_id = cmd.prog + '.modal.last'

    resp['type'] = 'modal'
    resp['title'] = pto_dfs('Modal Results')
    resp['close'] = pto_dfs('Back')
    resp['submit'] = pto_dfs('Done')
    resp['callback_id'] = event_id

    resp['blocks'] = extract_json([
        blocks.SectionBlock(
            text="Input results in raw JSON"
        ),
        blocks.SectionBlock(
            text="```" + json.dumps(results, indent=3) + "```"
        )
    ])

    slackapp.ui.modal.on(event_id, on_review_modal)

    return dict(response_action='push', view=dict(resp))


def on_review_modal(rqst, input_value):
    return {"response_action": "clear"}
