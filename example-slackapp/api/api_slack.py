
from flask import request
from app_data import blueprint, slackapp
from slack.errors import SlackApiError

from slackapptk.request.command import CommandRequest
from slackapptk.request.interactive import InteractiveRequest
from slackapptk.request.select import OptionSelectRequest


@blueprint.route('/slack/request', methods=["POST"])
def on_slack_request():
    payload = request.slack_rqst_data

    rqst = InteractiveRequest(
        app=slackapp,
        payload=payload
    )

    res = slackapp.handle_interactive_request(rqst)
    return res or "", 200


@blueprint.route('/slack/select', methods=["POST"])
def on_slack_select():

    rqst = OptionSelectRequest(
        app=slackapp,
        payload=request.slack_rqst_data
    )

    res = slackapp.handle_select_request(rqst)
    return res or "", 200


@blueprint.route(f"/slack/command/<name>", methods=['POST'])
def slackcmd_apptest(name):

    rqst = CommandRequest(app=slackapp,
                          form_data=request.form)

    channel = rqst.channel

    # If the bot is not able to respond in the originating channel for any
    # reason; could be a private DM, or a channel for which the bot is not a
    # member, then change the responding channel to the User DM so that it
    # shows up as a private DM from the bot.

    try:
        res = rqst.client.conversations_info(channel=channel)
        ch_info = res.get('channel')
        if ch_info.get('is_member', True) is False:
            rqst.channel = rqst.user_id

    except SlackApiError as api_err:
        if api_err.response.data['error'] == 'channel_not_found':
            rqst.channel = rqst.user_id

    res = slackapp.handle_slash_command(name=name, rqst=rqst)

    return res or "", 200
