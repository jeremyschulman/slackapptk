from slackapptk.cli import SlashCommandCLI
from app_data import slackapp

from . import main

demo_cmd = slackapp.slash_commands['demo'] = SlashCommandCLI(
    app=slackapp,
    cmd='demo',
    description='demo example app components',
    version='1.0',
    callback=main.main_demo
)

