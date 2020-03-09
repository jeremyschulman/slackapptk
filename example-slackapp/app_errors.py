from werkzeug.exceptions import Unauthorized
from flask import jsonify
from app_data import slackapp
from slack.errors import SlackApiError

from slack.web.classes.blocks import (
    SectionBlock
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
        err = dict(blocks=[SectionBlock(text=errmsg).to_dict()])
        return jsonify(err)

    errmsg = f"I'm sorry <@{rqst.user_id}>, I'm not authorized do to that."
    msg = dict(blocks=[SectionBlock(text=errmsg).to_dict()])
    return jsonify(msg)


def on_slack_apierror(exc):
    errmsg = f"Error with call to api.slack.com: {str(exc)}"
    msg = dict(blocks=[SectionBlock(text=errmsg).to_dict()])
    return jsonify(msg)


def on_general_exception(exc):
    errmsg = f"Unexpected error: {str(exc)}"
    msg = dict(blocks=[SectionBlock(text=errmsg).to_dict()])
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
