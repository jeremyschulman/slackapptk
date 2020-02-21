from flask import request
from blueprint import blueprint
from app_data import slackapp

from slackapp2pyez.exceptions import SlackAppError


@blueprint.route('/slack/request', methods=["POST"])
def on_slack_request():
    try:
        return slackapp.handle_interactive_request(request)

    except SlackAppError as exc:
        return {
            'error': exc.args[0]
        }, 400


@blueprint.route('/slack/select', methods=["POST"])
def on_slack_select():
    return slackapp.handle_select_request(request)

