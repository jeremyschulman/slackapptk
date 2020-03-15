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

import os
import logging

from importlib import import_module

from app_data import (
    flaskapp, blueprint,
    slackapp
)

import app_errors
import sessions
import log


def create_app():

    app = flaskapp
    app.config.from_envvar('FLASKAPP_SETTINGS')

    # -------------------------------------------------------------------------
    # Setup our Slackapp client
    # -------------------------------------------------------------------------

    try:
        slackapp.config.token = os.environ['SLACK_APP_TOKEN']
        slackapp.config.signing_secret = os.environ['SLACK_APP_SIGNING_SECRET']
        slackapp.log = log.create_logger()

    except Exception as exc:
        print(f"Unable to load Slack app config: {str(exc)}")
        exit(0)

    slackapp.log.setLevel(logging.DEBUG)

    app.session_interface = sessions.MyAppSessionInterface(
        slackapp=slackapp,
        directory=app.config['SESSIONS_DIR']
    )

    # -------------------------------------------------------------------------
    # now register all the API routes and Slack event handlers
    # -------------------------------------------------------------------------

    import_module('api')

    app.register_blueprint(blueprint)
    for route in app.url_map.iter_rules():
        print(route)

    app_errors.register_handlers(app)

    return app
