# import json
from flask import request
from blueprint import blueprint
from app_data import slackapp

from slackapptk.exceptions import SlackAppError


@blueprint.route('/slack/request', methods=["POST"])
def on_slack_request():
    try:
        return slackapp.handle_interactive_request(request)

        # if isinstance(resp, dict):
        #     slackapp.log.debug("RESPONSE: {}".format(
        #         json.dumps(resp, indent=3)
        #     ))
        #
        # return resp

    except SlackAppError as exc:
        return {
            'error': exc.args[0]
        }, 400


@blueprint.route('/slack/select', methods=["POST"])
def on_slack_select():
    return slackapp.handle_select_request(request)
