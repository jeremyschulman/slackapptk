from pathlib import Path
import shutil

import json

from werkzeug.exceptions import Unauthorized
from flask.sessions import SessionInterface




class SlackAppSessionInterface(SessionInterface):

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

        if not self.slackapp.verify_request(request=request):
            raise Unauthorized(
                description='Failed to verify slack request',
            )

        r_form = request.form
        payload = None

        def error():
            print("HEADERS>> {}".format(json.dumps(dict(request.headers), indent=3)))
            print("FORM>> {}".format(json.dumps(r_form, indent=3)))
            print("JSON>> {}".format(json.dumps(request.json, indent=3)))
            raise RuntimeError("Do not know this Slack API.")

        if 'payload' in r_form:
            payload = json.loads(r_form['payload'] or '{}')
            rqst_type = payload['type']
            session_id = payload['user']['id']
        elif 'command' in r_form:
            rqst_type = 'command'
            session_id = r_form['user_id']
        elif request.json:
            if 'event' in request.json:
                rqst_type = 'event'
                event_data = request.json['event']
                session_id = event_data.get('user') or event_data['channel']
            elif 'type' in request.json:
                return PickleCookieSession(self, request, app)
            else:
                error()
        else:
            error()

        session = PickleSlackSession(session_if=self, session_id=session_id)
        session['rqst_type'] = rqst_type
        session['rqst_data'] = payload or r_form
        session['user_id'] = session_id

        return session

    def save_session(self, app, session, response):
        session.save(app, session, response)
