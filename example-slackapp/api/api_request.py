
from flask import request
from blueprint import blueprint
from app_data import slackapp


@blueprint.route('/slack/request', methods=["POST"])
def on_slack_request():
    return slackapp.handle_interactive_request(request.form)

