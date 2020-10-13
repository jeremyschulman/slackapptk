"""
This file contains the SlackAppTK components for creating rich CLI command
parsing utilizing the Python standard argparse module.
"""

# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

from typing import Optional, Dict, Text, NoReturn

from inspect import stack, signature
from argparse import ArgumentParser, SUPPRESS, Namespace
import logging

# noinspection PyProtectedMember
from argparse import _VersionAction, _HelpAction, _SubParsersAction

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from first import first
import pyee

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from slackapptk.response import Response
from slackapptk.request.any import AnyRequest
from slackapptk.errors import SlackAppTKError

# -----------------------------------------------------------------------------
#
#                                CODE BEGINS
#
# -----------------------------------------------------------------------------

log = logging.getLogger(__name__)

NS_ATTR_CMD = "__tk_cmd__"
NS_ATTR_RESP = "__tk_resp__"


class SlackAppTKParserExit(Exception):
    """
    This exception is used to break the code execution path, required for help
    processing; the argparse presumes the Help processing calls parser.exit(),
    which would exit the program; that is call sys.exit().
    """
    pass


class SlackAppTKParser(ArgumentParser):
    def __init__(
        self,
        *vargs,
        **kwargs
    ):
        # need to disable adding help initially since if we do not, then the
        # standard argparse _HelpAction would be used during the initialization
        # of the help action, and we need to override this action class.

        super().__init__(*vargs, add_help=False, **kwargs)

        # The following set_defaults is used to "pass" the prog name so that
        # any subsequent add_subparsers also get this value, and by doing so
        # the ultimate command destination attribute stored in the resulting
        # Namspace will have the complete command name rather than just the
        # find sub-parser command.  This is needed so that the resulting
        # command can be used as the event ID to lookup the callback function
        # associated with the CLI command.

        prog = kwargs['prog']
        self.set_defaults(**{NS_ATTR_CMD: prog})

        # override the default 'help' and 'version' actions so that this parser
        # class can send the content via Slack messaging rather than to console
        # output.

        self.register('action', 'help', _TkHelpAction)
        self.register('action', 'version', _TkVersionAction)

        # now add the help argument using the new help action class. The
        # arguments here mirror those used by the arparse package.

        self.add_argument(
            # -h
            self.prefix_chars + 'h',
            # --help
            self.prefix_chars * 2 + 'help',
            action='help', default=SUPPRESS,
            help='show this help message and exit')

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #
    #                     ArgumentParser Overrides
    #
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def add_subparsers(self, *vargs, **kwargs):
        return super().add_subparsers(
            *vargs,
            dest=NS_ATTR_CMD,
            **kwargs)

    def error(self, message: Text) -> NoReturn:
        rqst = self.get_origin_rqst()

        self.send_help_on_error(
            rqst=rqst,
            errmsg=message,
            helptext=self.format_help())

        raise SlackAppTKParserExit()

    def exit(self, status: int = ..., message: Optional[Text] = ...):
        if message:
            log.error(f'parser exit: {message}')

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #
    #                     ArgumentParser Extensions
    #
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # noinspection PyProtectedMember
    @property
    def choices(self) -> Optional[Dict]:
        """
        This property returns the subparser choices; i.e. the "sub commands"
        assiged to this parser.

        Returns
        -------
        dict
            key=<command-name>
            value=<SlackAppTKParser>

        Notes
        -----
        The returned dictionary is "enriched" with the subcommand original help
        value as the help argument to add_parser was consumed internally by
        argparse and stored into an internal structure.
        """
        try:

            sub_par_acts: _SubParsersAction = self._subparsers._group_actions[0]
            assert isinstance(sub_par_acts, _SubParsersAction)
            choices = sub_par_acts.choices

            # enrich the parser with the help attribute
            for sub_act in sub_par_acts._get_subactions():
                setattr(choices[sub_act.dest], 'help', sub_act.help)

            return choices

        except (AssertionError, AttributeError, IndexError):
            return None

    @staticmethod
    def get_origin_rqst():
        for st in stack():
            ns = st.frame.f_locals.get('namespace')
            if hasattr(ns, NS_ATTR_RESP):
                return getattr(ns, NS_ATTR_RESP)

        return None

    def send_help(self, rqst: AnyRequest) -> None:
        resp = Response(rqst)

        cmd = rqst.rqst_data['command']
        txt = rqst.rqst_data['text']

        if '--help' in txt:
            txt = txt.rpartition(' ')[0]

        cmd_str = '%s %s' % (cmd, txt)

        helptext = self.format_help()

        resp.send_response(text=(
            f'Hi <@{rqst.user_id}>, here is help on the `{cmd_str}` command:\n\n'
            f"```{helptext}```")
        )

    @staticmethod
    def send_version(rqst, versiontext) -> None:
        Response(rqst).send_response(text=versiontext)

    @staticmethod
    def send_help_on_error(rqst, errmsg, helptext):
        resp = Response(rqst)

        atts = resp['attachments'] = list()
        atts.append(dict(
            color="#FF0000",    # red
            pretext=f'Hi <@{rqst.user_id}>, I could not run your command',
            text=f"```{rqst.rqst_data['command']} {rqst.rqst_data['text']}```"),
        )
        atts.append(dict(
            text=f"```{errmsg}```"
        ))
        atts.append(dict(
            pretext='Command help',
            text=f"```{helptext}```"
        ))

        resp.send()


class SlashCommandCLI(object):

    def __init__(self, parser: SlackAppTKParser):
        self.name = parser.prog
        self.parser = parser
        self.ic = pyee.EventEmitter()
        self.cli = pyee.EventEmitter()

    def run(self, rqst, event=None):

        # ---------------------------------------------------------------------
        # event provided by Caller means that the User invoked a Slack
        # interactive component (like a button), and the expectation of the IC
        # is to invoke the underlying code associated with processing that
        # command.  For example, the User has the option of entering "/command
        # status" or clicking a button that invokes the handler to execute the
        # code responsible for the "/command status" function; this case is the
        # latter.
        # ---------------------------------------------------------------------

        if event:
            handler = first(self.ic.listeners(event))

            if handler is None:
                rqst.app.log.critical(f"No handler for command option '{event}'")
                return

            return handler(rqst)

        # ---------------------------------------------------------------------
        # Here the User entered a "/command" and this code will parse the input
        # to locate the handler responsible for executing the command.  During
        # this processing, if the User invoked either "--help" or "--version",
        # the appropriate output will be sent back to the User, and this
        # function would need to return immediately.  For this reason the
        # SlackAppTKParseExit exception is used to "exit" the argparse command
        # processor.
        #
        # Provide a namespace with the origin slack request so that it can be
        # used to message back to the User. The rqst parameter is a
        # CommandRequest which contas the argv list[str]. parse the User
        # provided CLI args; trap on the exit exexception to mimic the behavior
        # of argsparse exiting the CLI processor.
        # ---------------------------------------------------------------------

        ns = Namespace()
        setattr(ns, NS_ATTR_RESP, rqst)

        try:
            ns_args = self.parser.parse_args(rqst.argv, namespace=ns)

        except SlackAppTKParserExit:
            return ''

        # the ns_args will have the cmd event _OR_ the User entered only up to
        # a sub parser name which will be used to identify the event.

        event = getattr(ns_args, NS_ATTR_CMD) or ' '.join([self.parser.prog] + rqst.argv)
        handler = first(self.cli.listeners(event))

        if handler is None:
            cmd_str = ' '.join(rqst.argv)
            raise SlackAppTKError(
                f"{cmd_str}: no handler for event '{event}'"
            )

        # detect if the callback wants the namespace parameters or not and
        # invoke the handler accordingly.

        sig_cal = signature(handler)
        if len(sig_cal.parameters) == 1:
            return handler(rqst)

        return handler(rqst, ns_args)


# -----------------------------------------------------------------------------
#
#                         Customized Argparse Actions
#
# -----------------------------------------------------------------------------

class _TkHelpAction(_HelpAction):
    """ overrides the standard help action to support Slack messaging """

    def __call__(self, parser: SlackAppTKParser, namespace, values, option_string=None):
        rqst = parser.get_origin_rqst()
        parser.send_help(rqst)
        raise SlackAppTKParserExit()


class _TkVersionAction(_VersionAction):
    """ overrides the standard version action to support Slack messaging """

    def __call__(self, parser: SlackAppTKParser, namespace, values, option_string=None):
        rqst = parser.get_origin_rqst()
        version = self.version or ''

        # noinspection PyProtectedMember
        formatter = parser._get_formatter()
        formatter.add_text(version)

        parser.send_version(rqst, formatter.format_help())
        raise SlackAppTKParserExit()
