import json

from typing import Optional, Dict, List, Any, Callable

from slack.web.classes import JsonObject, extract_json
from slack.web.classes.objects import PlainTextObject


class Modal(JsonObject):
    attributes = {
        'title',
        'callback_id'
    }

    def __init__(
            self,
            *,
            title: str,
            callback_id: str,
            close: Optional[str] = None,
            submit: Optional[str] = None,
            private_metadata: Optional[Dict] = None,
            blocks: Optional[List[Any]] = None
    ):
        self.title = title
        self.callback_id = callback_id
        self.close = close
        self.submit = submit
        self.private_metadata = private_metadata
        self.blocks = blocks or list()

    def add_block(self, block):
        self.blocks.append(block)
        return block

    def open(self, rqst, callback: Callable = None):

        if callback:
            rqst.app.ui.modal.on(self.callback_id, callback)

        return rqst.client.views_open(
            trigger_id=rqst.trigger_id,
            view=self.to_dict())

    def push(self, rqst, callback: Callable = None):
        if callback:
            rqst.app.ui.modal.on(self.callback_id, callback)

        return dict(response_action='push', view=self.to_dict())

    @staticmethod
    def clear_all():
        return {"response_action": "clear"}

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

        as_dict['blocks'] = extract_json(self.blocks)
        return as_dict
