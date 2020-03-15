import json

from typing import Optional, Dict, List, Any

from slack.web.classes import JsonObject, extract_json
from slack.web.classes.objects import PlainTextObject


class View(JsonObject):
    attributes = {
        'title',
        'callback_id',
        'external_id',
    }

    def __init__(
        self,
        *,
        title: Optional[str] = None,
        callback_id: Optional[str] = None,
        close: Optional[str] = None,
        submit: Optional[str] = None,
        private_metadata: Optional[Dict] = None,
        blocks: Optional[List[Any]] = None,
        external_id: Optional[str] = None,
        notify_on_close: Optional[bool] = False,
        clear_on_close: Optional[bool] = False
    ):
        self.title = title
        self.callback_id = callback_id
        self.close = close
        self.submit = submit
        self.private_metadata = private_metadata or {}
        self.blocks = blocks or list()

        self.external_id = external_id

        self.view_id = None
        self.view_hash = None
        self.state_values = None

        self.notify_on_close = notify_on_close
        self.clear_on_close = clear_on_close
        self.origin = None

    def add_block(self, block):
        self.blocks.append(block)
        return block

    def push_response(self):
        return {
            'response_action': 'push',
            'view': self.to_dict()
        }

    def update_response(self):
        return {
            'response_action': 'update',
            'view': self.to_dict()
        }

    @staticmethod
    def clear_all_response():
        return {
            "response_action": "clear"
        }

    @staticmethod
    def error_response(errors):
        return {
            "response_action": "errors",
            "errors": errors
        }

    def to_dict(self, *args) -> dict:
        as_dict = super().to_dict()

        pto_dfs = PlainTextObject.direct_from_string
        as_dict['type'] = 'modal'
        as_dict['title'] = pto_dfs(self.title)

        if self.close is not None:
            as_dict['close'] = pto_dfs(self.close)

        if self.submit is not None:
            as_dict['submit'] = pto_dfs(self.submit)

        if self.private_metadata is not None:
            as_dict['private_metadata'] = json.dumps(self.private_metadata)

        if self.notify_on_close is True:
            as_dict['notify_on_close'] = True

        if self.clear_on_close is True:
            as_dict['clear_on_close'] = True

        as_dict['blocks'] = extract_json(self.blocks)
        return as_dict

    @classmethod
    def from_view(cls, view):
        new_view = cls(
            title=view['title']['text'],
            callback_id=view['callback_id'],
            blocks=view['blocks'],
            external_id=view['external_id'] or None,
        )

        new_view.origin = view

        if view['close']:
            new_view.close = view['close']['text']

        if view['submit']:
            new_view.submit = view['submit']['text']

        new_view.notify_on_close = view['notify_on_close']
        new_view.view_id = view['id']
        new_view.view_hash = view['hash']

        if view['private_metadata']:
            new_view.private_metadata = json.loads(
                view['private_metadata']
            )

        new_view.state_values = view['state']['values']
        return new_view
