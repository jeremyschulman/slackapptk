from typing import NamedTuple, Union, List


COLOR_GREEN = "#008000"
COLOR_ORANGE = '#FFA500'
COLOR_RED = '#FF0000'
COLOR_BLUE = '#0000FF'


class ActionEvent(NamedTuple):
    data: dict
    id: str
    value: Union[str, List[str]]
    type: str


class BlockActionEvent(ActionEvent):

    def __new__(cls, *args, **kwargs):
        data = args[0]
        a_type = data['type']

        if a_type == 'button':
            a_id = data['action_id']

            return ActionEvent(
                type=a_type, data=data,
                id=a_id,
                value=data.get('value') or a_id
            )

        elif a_type == 'static_select':
            a_val = data['selected_option']['value']
            return ActionEvent(
                type=a_type, data=data,
                id=a_val, value=a_val
            )

        elif a_type == 'checkboxes':
            return ActionEvent(
                type=a_type, data=data,
                id=data['action_id'],
                value=[
                    each['value']
                    for each in data['selected_options']
                ]
            )

        raise RuntimeError(
            f"Unhangled {cls.__name__} type: {a_type}"
        )


class InteractiveMessageActionEvent(ActionEvent):
    def __new__(cls, *args, **kwargs):
        action = args[0]

        a_type = action['type']
        a_name = action['name']

        if a_type == 'button':
            return ActionEvent(
                data=action, type=a_type, id=a_name,
                value=action['value'])

        elif a_type == 'select':
            return ActionEvent(
                data=action, type=a_type, id=a_name,
                value=action['selected_options'][0]['value'])

        raise RuntimeError(
            f'Unhandled {cls.__name__} type: {a_type}'
        )
