from slackapptk.cli import SlackAppTKParser

from app_data import slackapp

from . import main

ping_parser = SlackAppTKParser(
    prog='ping',
    description='Simple ping test'
)

ping_parser.add_argument(
    'mode',
    default='private',
    choices=['public', 'private']
)

slash_ping = slackapp.commands.register(
    parser=ping_parser,
    callback=main.ping
)
