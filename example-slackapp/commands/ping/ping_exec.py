from argparse import Namespace

from slackapptk.request.command import CommandRequest
from slackapptk.response import Response

from .cli import slash_ping, ping_parser


@slash_ping.cli.on(ping_parser.prog)
def ping_exec(
    rqst: CommandRequest,
    cliargs: Namespace
):
    """
    This callback is executed when the User provides CLI arguments.

    Parameters
    ----------
    rqst: CommandRequest
        The inbound api.slack.com message enrobed for ease of use.

    cliargs: Namespace
        The User arguments stored in the Namespace object
    """
    resp = Response(rqst)

    if cliargs.mode == 'public':
        resp.send(text='*public* Pong!')
    else:
        resp.send(text='*private* Pong!',
                  private=rqst.user_id)
