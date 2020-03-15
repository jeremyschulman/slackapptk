from slackapptk.cli import SlackAppTKParser

from app_data import slackapp

from . import main

demo_parser = SlackAppTKParser(
    prog='demo',
    description="This command showcases the use of argsparse for rich CLI constructs"
)

demo_parser.add_argument(
    '-v', '--version',
    action='version',
    version='%(prog)s 1.0'
)

demo_cmds = demo_parser.add_subparsers(
    title='demo commands'
)

slash_demo = slackapp.commands.register(
    parser=demo_parser,
    callback=main.main_demo
)

# Note: each of the demo subcommands will define additiona CLI parsers bound to
# the demo_cmds instance.  See each file for details.
