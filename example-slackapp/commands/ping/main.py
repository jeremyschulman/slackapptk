
from slackapptk.cli import SlashCommandCLI
from slackapptk.request.command import CommandRequest
from slackapptk.response import Response


def ping(
    slashcli: SlashCommandCLI,
    rqst: CommandRequest
) -> None:
    """
    Called with no params, default is to ping privately.
    """
    resp = Response(rqst)
    resp.send_ephemeral("*private* Pong!")
