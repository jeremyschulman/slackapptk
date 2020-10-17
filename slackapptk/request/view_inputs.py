#
# FILE: viewtk.py
#
#    This file contains a utility function that will extract the View Input
#    element value based on the element type.
#

__all__ = ['get_input_value']


VIEW_INPUT_TYPE_VALUE = {
    'plain_text_input': lambda e: e.get('value'),
    'datepicker': lambda e: e.get('selected_date'),

    # single select elements:
    'static_select': lambda e: e.get('selected_option', {}).get('value'),
    'external_select': lambda e: e.get('selected_option', {}).get('value'),
    'users_select': lambda e: e.get('selected_user'),
    'conversations_select': lambda e: e.get('selected_conversation'),
    'channels_select': lambda e: e.get('selected_channel'),
    'radio_buttons': lambda e: e.get('selected_option', {}).get('value'),

    # multi-select elements
    'multi_static_select': lambda e: [i['value'] for i in e.get('selected_options', {})],
    'multi_external_select': lambda e: [i['value'] for i in e.get('selected_options', {})],
    'multi_users_select': lambda e: e.get('selected_users'),
    'multi_conversations_select': lambda e: e.get('selected_conversations'),
    'multi_channels_select': lambda e: e.get('selected_channel'),
    'checkboxes': lambda e: [i['value'] for i in e.get('selected_options', {})]
}


def get_input_value(ele):
    value_type = ele['type']
    return VIEW_INPUT_TYPE_VALUE[value_type](ele)
