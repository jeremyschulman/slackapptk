import json

from flask import request
from first import first
from blueprint import blueprint
from app_data import slackapp

from slackapp2pyez import CommandRequest, Response


@blueprint.route("/slack/command/ping", methods=['POST'])
def slackcmd_ping():

    rqst = CommandRequest(slackapp, request)
    resp = Response(rqst)

    if first(rqst.argv, '') == 'public':
        res = resp.send_public('public pong')
    else:
        res = resp.send_ephemeral("private pong")

    if not res.get('ok'):
        slackapp.log.error(
            "Ping failed: " + json.dumps(res, indent=3)
        )

    return ""
