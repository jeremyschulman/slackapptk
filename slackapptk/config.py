from collections import UserDict


__all__ = ['SlackAppConfig']


class SlackAppConfig(UserDict):

    def __init__(self):
        super(SlackAppConfig, self).__init__()
        self.signing_secret = None
        self.token = None

    def from_obj(self, obj):
        self.update(obj)
        self.signing_secret = obj['signing_secret']
        self.token = obj['token']

