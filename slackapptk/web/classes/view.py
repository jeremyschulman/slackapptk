import json

from slack.web.classes.objects import PlainTextObject
from slack.web.classes.views import View as SlackView


class View(SlackView):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('type', 'modal')

        super(View, self).__init__(*args, **kwargs)

        if 'blocks' in kwargs:
            self.blocks = kwargs.get('blocks')
        else:
            self.blocks = list()

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
        if isinstance(self.private_metadata, dict):
            self.private_metadata = json.dumps(self.private_metadata)

        return super().to_dict()

    @classmethod
    def from_view(cls, view):
        new_view = cls(
            type=view['type'],
            title=PlainTextObject(text=view['title']['text']),
            callback_id=view['callback_id'],
            blocks=view['blocks'],
            external_id=view['external_id'] or None,
            clear_on_close=view['clear_on_close'] or None
        )

        if view['close']:
            new_view.close = PlainTextObject(text=view['close']['text'])

        if view['submit']:
            new_view.submit = PlainTextObject(text=view['submit']['text'])

        new_view.notify_on_close = view['notify_on_close']
        new_view.view_id = view['id']

        if view['private_metadata']:
            try:
                new_view.private_metadata = json.loads(view['private_metadata'])
            except json.JSONDecodeError:
                new_view.private_metadata = view['private_metadata']

        new_view.state_values = view['state']['values']
        new_view.view_hash = view['hash']
        return new_view

    def add_block(self, block):
        self.blocks.append(block)
        return block
