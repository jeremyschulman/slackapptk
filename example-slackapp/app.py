#  Copyright 2019 Jeremy Schulman, nwkautomaniac@gmail.com
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#  http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
from importlib import import_module

from flask import jsonify, request
from blueprint import blueprint
from slack.web.classes.blocks import SectionBlock

from slackapp2pyez.exceptions import SlackAppError
from slackapp2pyez.sessions import SlackAppSessionInterface

from app_data import (
    flaskapp,
    slackapp
)


def create_app():

    app = flaskapp
    app.config.from_envvar('FLASKAPP_SETTINGS')

    # -------------------------------------------------------------------------
    # Setup our Slackapp client
    # -------------------------------------------------------------------------

    slackapp.config.from_envar('SLACKAPP_SETTINGS')
    slackapp.log.setLevel(logging.DEBUG)

    sessiondb_path = slackapp.config['sessions']['path']

    app.session_interface = SlackAppSessionInterface(
        signing_secret=slackapp.config.signing_secret,
        directory=sessiondb_path
    )

    # -------------------------------------------------------------------------
    # now register all the API routes and Slack event handlers
    # -------------------------------------------------------------------------

    import_module('api')

    app.register_blueprint(blueprint)
    for route in app.url_map.iter_rules():
        print(route)

    app.register_error_handler(SlackAppError, on_401_unauthorized)
    return app


def on_401_unauthorized(exc):

    try:
        msg, code, rqst = exc.args

    except Exception as exc:
        errmsg = "App error called with exception: {}".format(str(exc))
        slackapp.log.error(errmsg)
        err = dict(blocks=[SectionBlock(text=errmsg).to_dict()])
        return jsonify(err)

    errmsg = f"I'm sorry {rqst.user_name}, I'm not authorized do to that."
    msg = dict(blocks=[SectionBlock(text=errmsg).to_dict()])
    return jsonify(msg)
