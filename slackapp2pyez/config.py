import os
from pathlib import Path
from collections import UserDict

import toml

__all__ = ['SlackAppConfig']


class SlackAppConfig(UserDict):

    def __init__(self):
        super(SlackAppConfig, self).__init__()
        self.channels = None
        self.signing_secret = None
        self.token = None

    def from_obj(self, obj):
        # store the config file data into the object as dict

        self.update(obj)

        # create a specific `channels` attribute that is a dict of channel ID to
        # channel config.

        self.channels = {_chan['id']: _chan
                         for _chan in self['channels']}

        self.signing_secret = obj['app']['signing_secret']
        self.token = obj['app']['token']

        self['SLACK_CHANNEL_NAME_TO_ID'] = {
            _chan['name']: _chan['id']
            for _chan in self['channels']
        }

    def from_envar(self, envar):
        conf_file = os.environ.get(envar)
        if not conf_file:
            raise RuntimeError(f'The environment variable {envar} is not set '
                               'and as such configuration could not be '
                               'loaded.  Set this variable and make it '
                               'point to a configuration file')

        conf_file_p = Path(conf_file)
        if not conf_file_p.exists():
            raise RuntimeError(f'The environment variable {envar} is set to '
                               f'{conf_file}, but this file does not exist')

        # import the configuration from the contents of the TOML file.

        self.from_obj(toml.load(conf_file_p))
