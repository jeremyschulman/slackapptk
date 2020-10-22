from typing import NamedTuple, Union, List

from slackapptk.errors import SlackAppTKError

__all__ = [
    'ActionEvent',
    'BlockActionEvent',
    'InteractiveMessageActionEvent'
]


class ActionEvent(NamedTuple):
    data: dict
    id: str
    value: Union[str, List[str]]
    type: str


def BlockActionEvent(data) -> ActionEvent:
    a_type = data['type']
    a_id = data['action_id']

    if a_type == 'button':
        return ActionEvent(
            type=a_type, data=data, id=a_id,
            value=data.get('value') or a_id
        )

    elif a_type in ['static_select', 'external_select', 'radio_buttons']:
        a_val = data['selected_option']['value']
        return ActionEvent(
            type=a_type, data=data, id=a_id,
            value=a_val
        )

    elif a_type in ['checkboxes', 'multi_static_select']:
        return ActionEvent(
            type=a_type, data=data, id=a_id,
            value=[
                each['value']
                for each in data['selected_options']
            ]
        )

    elif a_type in ['channels_select', 'users_select', 'conversations_select']:
        if a_type == 'channels_select':
            a_val = data['selected_channel']
        elif a_type == 'users_select':
            a_val = data['selected_user']
        elif a_type == 'conversations_select':
            a_val = data['selected_conversation']

        return ActionEvent(
            type=a_type, data=data, id=a_id,
            value=a_val
        )

    elif a_type in ['plain_text_input']:
        a_val = data['value']

        return ActionEvent(
            type=a_type, data=data, id=a_id,
            value=a_val
        )

    raise SlackAppTKError(
        f"Unhangled BlockActionEvent type: {a_type}"
    )


def InteractiveMessageActionEvent(action) -> ActionEvent:
    """
    These types of events originate from the secondary attachments found in the
    interactive message.  Generally speaking this mode of UI is being
    depreciated in favor of using blocks for "All the Things".
    """

    a_type = action['type']
    a_name = action['name']

    if a_type == 'button':
        return ActionEvent(
            data=action, type=a_type, id=a_name,
            value=action['value']
        )

    elif a_type == 'select':
        return ActionEvent(
            data=action, type=a_type, id=a_name,
            value=action['selected_options'][0]['value'])

    raise SlackAppTKError(
        f'Unhandled InteractiveMessageActionEvent type: {a_type}'
    )
