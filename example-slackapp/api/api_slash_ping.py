import json

from flask import request
from blueprint import blueprint
from app_data import slackapp


@blueprint.route("/slack/command/ping", methods=['POST'])
def slackcmd_ping():
    rqst = slackapp.RequestEvent(request.form)
    resp = rqst.ResponseMessage()
    res = resp.send_ephemeral("pong")

    if not res.get('ok'):
        slackapp.log.error(
            "Ping failed: " + json.dumps(res, indent=3)
        )

    return ""
