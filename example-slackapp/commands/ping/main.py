
# -----------------------------------------------------------------------------
# SlackAppTK Imports
# -----------------------------------------------------------------------------

from slackapptk.request.command import CommandRequest
from slackapptk.response import Response

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .cli import slash_ping, ping_parser


@slash_ping.cli.on(ping_parser.prog)
def ping(rqst: CommandRequest) -> None:
    """
    Called with no params, default is to ping privately.
    """
    Response(rqst).send_response(text="*private* Pong!")
