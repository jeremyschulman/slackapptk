from typing import Optional


from slack.web.classes import (
    JsonObject, JsonValidator
)


class DescriptiveOption(JsonObject):

    attributes = {}  # no attributes because to_dict has unique implementations

    label_max_length = 75
    value_max_length = 75

    def __init__(
        self, *,
        label: str,
        value: Optional[str] = None,
        description: Optional[str] = None,
        mrkdwn: Optional[bool] = False
    ):
        self.label = label
        self.value = value or label
        self.description = description
        self.mrkdwn = mrkdwn

    @JsonValidator(f"label attribute cannot exceed {label_max_length} characters")
    def label_length(self):
        return len(self.label) <= self.label_max_length

    @JsonValidator(f"value attribute cannot exceed {value_max_length} characters")
    def value_length(self):
        return len(self.value) <= self.value_max_length

    def to_dict(self) -> dict:
        """
        Different parent classes must call this with a valid value from OptionTypes -
        either "dialog", "action", or "block", so that JSON is returned in the
        correct shape.
        """
        self.validate_json()
        as_dict = dict()

        as_dict['text'] = {
            'type': 'mrkdwn' if self.mrkdwn else 'plain_text',
            'text': self.label
        }

        as_dict['value'] = self.value

        if self.description is not None:
            as_dict['description'] = {
                'type': 'mrkdwn' if self.mrkdwn else 'plain_text',
                'text': self.description
            }

        return as_dict
