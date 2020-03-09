
import shutil
import json

from flask.sessions import SessionInterface
from werkzeug.exceptions import Unauthorized
from pathlib import Path


from slackapptk.flask.sessions import (
    PickleSlackSession,
    PickleCookieSession,
)

from slackapptk.flask.verify_request import verify_request


class MyAppSessionInterface(SessionInterface):

    def __init__(self, slackapp, directory):
        self.slackapp = slackapp
        self.directory = Path(directory)
        self.signing_secret = slackapp.config.signing_secret

        if self.directory.exists():
            shutil.rmtree(self.directory)

        self.directory.mkdir()

    def open_session(self, app, request):
        # If this is not a request from api.slack.com, then we'll use standard
        # cookie session methods.

        if 'X-Slack-Signature' not in request.headers:
            return PickleCookieSession(self, request, app)

        # NOTE: this call MUST be executed before the use of `request.form` since
        #       the `verify_request` makes use of request.get_data(), and the use
        #       of form will clear the buffer, as document here:
        #       https://werkzeug.palletsprojects.com/en/1.0.x/wrappers/

        secret = self.slackapp.config.signing_secret
        if not verify_request(request=request, signing_secret=secret):
            raise Unauthorized(
                description='Failed to verify slack request',
            )

        session_id = None
        rqst_data = request.form

        if 'payload' in rqst_data:
            rqst_data = json.loads(rqst_data['payload'] or '{}')
            session_id = rqst_data['user']['id']

        elif 'command' in rqst_data:
            session_id = rqst_data['user_id']

        elif request.json:
            if 'event' in request.json:
                rqst_data = request.json
                event_data = request.json['event']
                session_id = event_data.get('user') or event_data['channel']

        if not session_id:
            raise Unauthorized("Session undetermined request", rqst_data)

        request.slack_rqst_data = rqst_data
        session = PickleSlackSession(session_if=self, session_id=session_id)
        session['user_id'] = session_id

        return session

    def save_session(self, app, session, response):
        session.save(app, session, response)
