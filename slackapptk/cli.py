from typing import Optional, Callable, List

from argparse import ArgumentParser, Action, SUPPRESS

from first import first
from flask import abort
import pyee

from slackapptk.response import Response
from slackapptk.errors import SlackAppTKError


class SlackArgsParserError(Exception):
    def __init__(self, parser, message):
        self.parser = parser
        self.message = message


class SlackArpsParserShowHelp(Exception):
    def __init__(self, parser, message):
        self.parser = parser
        self.message = message


class SlackArpsParserShowVersion(Exception):
    def __init__(self, parser, message):
        self.parser = parser
        self.message = message


class SlackArgsParser(ArgumentParser):
    def __init__(self, *vargs, **kwargs):
        super().__init__(*vargs, **kwargs)
        self.help = None

    def print_help(self, file=None):
        raise SlackArpsParserShowHelp(
            parser=self,
            message=self.format_help()
        )

    def error(self, message):
        raise SlackArgsParserError(
            parser=self,
            message=message
        )


class _SlackAppVersionAction(Action):
    def __init__(
            self,
            option_strings,
            version=None,
            dest=SUPPRESS,
            default=SUPPRESS,
            help="show program's version number and exit"
    ):
        super(_SlackAppVersionAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        formatter = parser._get_formatter()
        formatter.add_text(self.version)

        raise SlackArpsParserShowVersion(
            parser=parser,
            message=formatter.format_help()
        )


class SlashCommandCLI(object):

    def __init__(
        self,
        app,                    #: SlackApp,
        version: str,
        cmd: str,
        description: str,
        callback: Optional[Callable] = None,
    ):
        """
        Provides a CLI argsparse like interface for Slack slash commands,
        using the `argsparse` standard mechanism.

        Parameters
        ----------
        cmd : str
            The slash command, for example "/boop".

        description : str
            A short descriptiion of the command that can be used
            as help-text.

        callback : Callable
            The slash command cli callback function that will be invoked when
            the User does not provide any CLI arguments (other than --help).
            This callback function is expected to return a Slack API result to
            guide the User through the command.
        """
        self.app = app
        self.parser = SlackArgsParser(
            description=description
        )
        self.parser.version = version

        self.parser.add_argument(
            '--version',
            action=_SlackAppVersionAction,
            version='%(prog)s ' + version
        )

        self.parser.prog = cmd
        self.parsers: List[SlackArgsParser] = []
        self.sub_cmds = None

        self.ic = pyee.EventEmitter()
        self.cli = pyee.EventEmitter()
        self.callback = callback

    @property
    def cmd(self):
        return self.parser.prog

    def add_subcommand(self, cmd_name, parser_spec, arg_list=None, parent=None):

        if not any((parent, self.sub_cmds)):
            self.sub_cmds = self.parser.add_subparsers(parser_class=SlackArgsParser)

        attach_to = parent or self.sub_cmds

        if not attach_to:
            raise SlackAppTKError(
                f'Unable to attach subcommand {cmd_name} to {self.cmd}.  '
                'This command was created with no_subcommands'
            )

        # the add_parser command consumes the 'help' option in a way that I
        # don't entirely understand how to get it back.  So I am adding the
        # attribute back here.

        new_p = attach_to.add_parser(cmd_name, **parser_spec)
        new_p.help = parser_spec.get('help')

        if arg_list:
            for param, param_spec in arg_list:
                new_p.add_argument(param, **param_spec)

        new_p.set_defaults(cmd=cmd_name)
        if not parent:
            self.parsers.append(new_p)

        return new_p

    def add_subparser(self, name, help, description, parent=None, **kwargs):
        new_p = self.add_subcommand(
            cmd_name=name, parent=parent,
            parser_spec=dict(help=help, description=description)
        )
        new_p.set_defaults(parser=new_p)
        return new_p.add_subparsers(**kwargs)

    def get_command_options(self):
        return {
            p.prog: p.help
            for p in self.parsers
        }

    def get_command_help(self):
        return self.parser.format_help()

    @staticmethod
    def send_help_on_error(rqst, msg, helptext):
        resp = Response(rqst)

        atts = resp['attachments'] = list()
        atts.append(dict(
            color="#FF0000",    # red
            pretext=f'Hi <@{rqst.user_id}>, I could not run your command',
            text=f"```{rqst.rqst_data['command']} {rqst.rqst_data['text']}```"),
        )
        atts.append(dict(
            text=f"```{msg}```"
        ))
        atts.append(dict(
            pretext='Command help',
            text=f"```{helptext}```"
        ))

        resp.send().raise_for_status()

    @staticmethod
    def get_help_cmd_str(rqst):
        cmd = rqst.rqst_data['command']
        txt = rqst.rqst_data['text']

        if '--help' in txt:
            txt = txt.rpartition(' ')[0]

        return '%s %s' % (cmd, txt)

    @staticmethod
    def send_help(rqst, helptext):
        resp = Response(rqst)
        cmd_str = SlashCommandCLI.get_help_cmd_str(rqst)
        resp.send(
            f'Hi <@{rqst.user_id}>, here is help on the `{cmd_str}` command:\n\n'
            f"```{helptext}```"
        ).raise_for_status()

    @staticmethod
    def send_version(rqst, versiontext):
        resp = Response(rqst)
        resp.send(versiontext).raise_for_status()

    def run(self, rqst, event=None):

        # ---------------------------------------------------------------------
        # if `event` was provided, then this invocation is a result of
        # a User event interaction, for example selecting a drop-down option
        # ---------------------------------------------------------------------

        if event:
            handler = first(self.ic.listeners(event))
            if handler is None:
                rqst.app.log.critical(f"No handler for command option '{event}'")
                return

            return handler(rqst)

        # ---------------------------------------------------------------------
        # if `event` was not provided, then the User invoked the slash command
        # CLI with text options.
        # ---------------------------------------------------------------------

        try:
            args = self.parser.parse_args(rqst.argv)

        except SlackArpsParserShowVersion as exc:
            SlashCommandCLI.send_version(rqst, exc.message)
            return

        except SlackArpsParserShowHelp as exc:
            SlashCommandCLI.send_help(rqst, exc.message)
            return

        except SlackArgsParserError as exc:
            self.app.log.warning(exc.message)
            SlashCommandCLI.send_help_on_error(rqst, msg=exc.message,
                                               helptext=exc.parser.format_help())
            return

        # TODO: remove the use of params since we're passing args
        #       to the handler.

        params = vars(args)
        parser = params.pop('parser', None) or self.parser
        cmd = params.pop('cmd', None)

        event = ' '.join(filter(None, (parser.prog, cmd)))
        handler = first(self.cli.listeners(event))

        if handler is None:
            emsg = f"No handler for /cmd event '{event}'"
            self.app.log.critical(emsg)
            abort(501, emsg)
            return

        return handler(rqst, args)
