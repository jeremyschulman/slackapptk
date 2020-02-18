import json

from typing import Optional, Union, Set
from slack.web.classes.blocks import Block

from slack.web.classes.elements import InteractiveElement
from slack.web.classes.objects import PlainTextObject

from .elements import PlainTextElement

__all__ = ['InputBlock']


class InputBlock(Block):
    fields_max_length = 10

    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"hint", "optional"})

    def __init__(
        self,
        *,
        label: str,
        element: Union[PlainTextElement, InteractiveElement],
        block_id: Optional[str] = None,
        hint: Optional[str] = None,
        optional: bool = None
    ):
        """
        https://api.slack.com/reference/block-kit/blocks#input
        """
        super().__init__(subtype="input", block_id=block_id)
        self.label = label
        self.element = element
        self.hint = hint
        self.optional = optional

    def to_dict(self) -> dict:
        as_dict = super().to_dict()

        as_dict['element'] = self.element.to_dict()
        pto_dfs = PlainTextObject.direct_from_string

        as_dict['label'] = pto_dfs(self.label)

        if 'hint' in as_dict:
            as_dict['hint'] = pto_dfs(self.hint)

        return as_dict
