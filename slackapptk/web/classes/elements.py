from typing import Optional, List, Union, Set

from slack.web.classes import (
    JsonObject,
    extract_json
)

from slack.web.classes.elements import (
    InteractiveElement,
    AbstractSelector,
    PlainTextObject,
    Option, OptionGroup,
    ConfirmObject
)

from slackapptk.web.classes.objects import (
    DescriptiveOption
)

__all__ = [
    'PlainTextElement',
    'MultiSelectElement',
    "CheckboxElement",
    'RadioButtonsElement'
]


class PlainTextElement(JsonObject):

    attributes = {
        "type",
        "action_id",
        "placeholder",
        "initial_value",
        "multiline",
        "max_length",
        "min_length",
    }

    def __init__(
        self,
        *,
        action_id: str,
        placeholder: Optional[str] = None,
        initial_value: Optional[str] = None,
        multiline: Optional[bool] = None,
        min_length: int = 0,
        max_length: Optional[int] = None,
    ):
        self.type = 'plain_text_input'
        self.action_id = action_id
        self.placeholder = placeholder
        self.min_length = min_length
        self.max_length = max_length
        self.multiline = multiline
        self.initial_value = initial_value

    def to_dict(self, *args) -> dict:
        as_dict = super().to_dict()
        as_dict['type'] = self.type
        as_dict['action_id'] = self.action_id

        pto_dfs = PlainTextObject.direct_from_string

        if self.placeholder:
            as_dict['placeholder'] = pto_dfs(self.placeholder)

        if self.initial_value:
            as_dict['initial_value'] = pto_dfs(self.initial_value)

        return as_dict


class MultiSelectElement(AbstractSelector):

    options_max_length = 100

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({
            "max_selected_items",
            "min_query_length"
        })

    def __init__(
        self,
        *,
        placeholder: str,
        action_id: str,
        options: List[Union[Option, OptionGroup]],
        initial_options: Optional[List[Union[Option, OptionGroup]]] = None,
        confirm: Optional[ConfirmObject] = None,
        max_selected_items: int = None,
        min_query_length: int = None
    ):

        super().__init__(
            placeholder=placeholder,
            action_id=action_id,
            subtype="multi_static_select",
            confirm=confirm,
        )
        self.options = options
        self.initial_options = initial_options
        self.max_selected_items = max_selected_items
        self.min_query_length = min_query_length

    def to_dict(self) -> dict:
        json = super().to_dict()

        if isinstance(self.options[0], OptionGroup):
            json["option_groups"] = extract_json(self.options, "block")
        else:
            json["options"] = extract_json(self.options, "block")

        if self.initial_options is not None:
            json["initial_options"] = extract_json(self.initial_options, "block")

        return json


class CheckboxElement(InteractiveElement):

    def __init__(
        self,
        *,
        action_id: str,
        options: List[DescriptiveOption],
        initial_options: Optional[List[Option]] = None,
        confirm: Optional[ConfirmObject] = None,
    ):
        super().__init__(action_id=action_id, subtype='checkboxes')
        self.options = options
        self.initial_options = initial_options
        self.confirm = confirm

    def to_dict(self) -> dict:
        as_dict = super().to_dict()
        as_dict['options'] = extract_json(self.options)

        if self.confirm is not None:
            as_dict["confirm"] = extract_json(self.confirm)

        if self.initial_options is not None:
            as_dict['initial_options'] = extract_json(self.initial_options)

        return as_dict


class RadioButtonsElement(InteractiveElement):
    def __init__(
        self,
        *,
        action_id: str,
        options: List[DescriptiveOption],
        initial_option: Optional[Option] = None,
        confirm: Optional[ConfirmObject] = None,
    ):
        super().__init__(action_id=action_id, subtype='radio_buttons')
        self.options = options
        self.initial_option = initial_option
        self.confirm = confirm

    def to_dict(self) -> dict:
        as_dict = super().to_dict()
        as_dict['options'] = extract_json(self.options)

        if self.confirm is not None:
            as_dict["confirm"] = extract_json(self.confirm)

        if self.initial_option is not None:
            as_dict['initial_option'] = extract_json(self.initial_option)

        return as_dict
