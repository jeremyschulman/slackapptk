from pkg_resources import get_distribution
from slackapptk.cli import SlackAppTKParser

from app_data import slackapp

demo_parser = SlackAppTKParser(
    prog='demo',
    description="This command showcases the use of argsparse for rich CLI constructs"
)

demo_parser.add_argument(
    '-v', '--version',
    action='version',
    version='%(prog)s ' + get_distribution('slackapptk').version
)

demo_cmds = demo_parser.add_subparsers(
    title='demo commands'
)

slash_demo = slackapp.commands.register(demo_parser)

# Note: each of the demo subcommands will define additiona CLI parsers bound to
# the demo_cmds instance.  See each file for details.
