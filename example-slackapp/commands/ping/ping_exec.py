from argparse import Namespace
from slackapptk.request.command import CommandRequest
from slackapptk.response import Response

from .cli import ping_cmd


@ping_cmd.cli.on(ping_cmd.cmd)
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
        resp.send_public('*public* Pong!')
    else:
        resp.send_ephemeral('*private* Pong!')
