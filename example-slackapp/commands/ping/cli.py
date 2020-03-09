from app_data import slackapp
from slackapptk.cli import SlashCommandCLI

from . import main

ping_cmd = slackapp.slash_commands['ping'] = SlashCommandCLI(
    app=slackapp,
    version='1.0',
    cmd='ping',
    description='Simple ping test',
    callback=main.ping
)

ping_cmd.parser.add_argument(
    'mode', default='private',
    choices=['public', 'private']
)
