import sys
import json
import traceback


from werkzeug.exceptions import Unauthorized
from flask import jsonify
from app_data import slackapp
from slack.errors import SlackApiError

from slack.web.classes.blocks import (
    SectionBlock
)

from slack.web.classes.objects import (
    MarkdownTextObject
)

from slackapptk.request.any import AnyRequest

__all__ = ['register_handlers']


def on_401_unauthorized(exc):
    try:
        msg = exc.args[0]
        code = exc.args[1]
        rqst: AnyRequest = exc.args[2]

    except Exception as exc:
        errmsg = "App error called with exception: {}".format(str(exc))
        slackapp.log.error(errmsg)
        err = dict(blocks=[SectionBlock(text=MarkdownTextObject(text=f"```{errmsg}```")).to_dict()])
        return jsonify(err)

    errmsg = f"I'm sorry <@{rqst.user_id}>, I'm not authorized do to that."
    msg = dict(blocks=[SectionBlock(text=MarkdownTextObject(text=f"```{errmsg}```")).to_dict()])
    return jsonify(msg)


def on_slack_apierror(exc):
    errmsg = f"Error with call to api.slack.com: {str(exc)}"
    slackapp.log.error(errmsg)
    msg = dict(blocks=[SectionBlock(text=MarkdownTextObject(text=f"```{errmsg}```")).to_dict()])
    return jsonify(msg)


def on_general_exception(exc):
    exc_info = sys.exc_info()
    tb_content = json.dumps(traceback.format_tb(exc_info[2]), indent=3)
    errmsg = f"Unexpected error: {str(exc)}:\n{tb_content}"
    slackapp.log.critical(errmsg)
    msg = dict(blocks=[SectionBlock(text=MarkdownTextObject(text=f"```{errmsg}```")).to_dict()])
    return jsonify(msg)


def register_handlers(app):
    app.register_error_handler(
        SlackApiError,
        on_slack_apierror
    )

    app.register_error_handler(
        Unauthorized,
        on_401_unauthorized
    )

    app.register_error_handler(
        Exception,
        on_general_exception
    )
