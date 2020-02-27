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

"""
This file implements a Flask SessionInterface that will create sessions based
on the Slack user_id value.  If the inbound message is not "slack related",
then it will use a standard cookies approach.

Some of this code was inspired from: http://flask.pocoo.org/snippets/132/
"""

import os
from contextlib import suppress
from collections import UserDict

import pickle
from uuid import uuid1

from flask.sessions import SessionMixin


__all__ = [
    'PickleSlackSession',
    'PickleCookieSession'
]


class PickleSession(UserDict, SessionMixin):

    def __init__(self, session_if, session_id):
        super(PickleSession, self).__init__()
        self.session_if = session_if
        self.path = session_if.directory / session_id
        self.session_id = session_id
        self.read()

    def read(self):
        try:
            pdata = pickle.load(self.path.open('rb'))
            self.update(pdata)
        except (FileNotFoundError, ValueError, EOFError, pickle.UnpicklingError):
            pass

    def save(self, *vargs, **kwargs):
        with self.path.open('wb') as ofile:
            pickle.dump(dict(self), ofile)


class PickleSlackSession(PickleSession):

    def save(self, *vargs, **kwargs):
        super(PickleSlackSession, self).save()


class PickleCookieSession(PickleSession):

    def __init__(self, session_if, request, app):
        sid = (request.cookies.get(app.session_cookie_name) or
               '{}-{}'.format(uuid1(), os.getpid()))

        super(PickleCookieSession, self).__init__(session_if, sid)

    def save(self, app, session, response):
        domain = self.session_if.get_cookie_domain(app)

        if not session:
            with suppress(FileNotFoundError):
                session.path.unlink()
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        cookie_exp = self.session_if.get_expiration_time(app, session)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True, domain=domain)


