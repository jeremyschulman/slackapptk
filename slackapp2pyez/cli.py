
from argparse import ArgumentParser

from first import first
from flask import abort
import pyee

from slackapp2pyez import ui


class SlackArgsParserError(Exception):
    def __init__(self, parser, message):
        self.parser = parser
        self.message = message


class SlackArpsParserShowHelp(Exception):
    def __init__(self, parser, message):
        self.parser = parser
        self.message = message


class SlackArgsParser(ArgumentParser):
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


class SlashCommandCLI(object):

    def __init__(self, app, cmd: str, description: str):
        self.app = app
        self.parser = SlackArgsParser(description=description)
        self.parser.prog = cmd
        self.parsers = []
        self.sub_cmds = self.parser.add_subparsers()
        self.ui = pyee.EventEmitter()
        self.cli = pyee.EventEmitter()

    @property
    def cmd(self):
        return self.parser.prog

    def add_command_option(self, cmd_name, parser_spec, arg_list=None, parent=None):
        attach_to = parent or self.sub_cmds
        new_p = attach_to.add_parser(cmd_name, **parser_spec)
        new_p.set_defaults(cmd=cmd_name)

        if arg_list:
            for param, param_spec in arg_list:
                new_p.add_argument(param, **param_spec)

        self.parsers.append(new_p)
        return new_p

    def get_command_options(self):
        return {
            p.prog: p.description
            for p in self.parsers
        }

    def get_command_help(self):
        return self.parser.format_help()

    @staticmethod
    def send_help_on_error(rqst, msg, helptext):
        resp = rqst.ResponseMessage()

        atts = resp['attachments'] = list()
        atts.append(dict(
            color=ui.COLOR_RED,
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
        resp = rqst.ResponseMessage()
        cmd_str = SlashCommandCLI.get_help_cmd_str(rqst)
        resp.send(
            f'Hi <@{rqst.user_id}>, here is help on the `{cmd_str}` command:\n\n'
            f"```{helptext}```"
        ).raise_for_status()

    def run(self, rqst, event=None):

        # ---------------------------------------------------------------------
        # if `event` was provided, then this invocation is a result of
        # a User event interaction, for example selecting a drop-down option
        # ---------------------------------------------------------------------

        if event:
            handler = first(self.ui.listeners(event))
            if handler is None:
                rqst.app.log.critical(f"No handler for command option '{event}'")
                return ""

            return handler(rqst) or ""

        # ---------------------------------------------------------------------
        # if `event` was not provided, then the User invoked the slash command
        # CLI with text options.
        # ---------------------------------------------------------------------

        try:
            args = self.parser.parse_args(rqst.argv)

        except SlackArpsParserShowHelp as exc:
            SlashCommandCLI.send_help(rqst, exc.message)
            return ""

        except SlackArgsParserError as exc:
            self.app.log.warning(exc.message)
            SlashCommandCLI.send_help_on_error(rqst, msg=exc.message,
                                               helptext=exc.parser.format_help())
            return ""

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

        return handler(rqst, params) or ""
