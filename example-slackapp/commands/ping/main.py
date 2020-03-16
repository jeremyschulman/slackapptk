
from slackapptk.cli import SlashCommandCLI
from slackapptk.request.command import CommandRequest
from slackapptk.response import Response


# noinspection PyUnusedLocal
def ping(
    slashcli: SlashCommandCLI,
    rqst: CommandRequest
) -> None:
    """
    Called with no params, default is to ping privately.
    """
    Response(rqst).send_response(text="*private* Pong!")
