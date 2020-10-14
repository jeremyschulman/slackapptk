#  Copyright 2020 Jeremy Schulman, nwkautomaniac@gmail.com
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

import asyncio
from collections import UserDict
from typing import Any, Optional

from slack.errors import SlackApiError
from slack.web.client import WebClient
from slack.web.async_internal_utils import _get_event_loop

__all__ = ["Messenger"]


class Messenger(UserDict):
    """
    The Messenger class is used to create an object that can respond back to the User
    with the context of a received Request message.  This use is suitable in contexts
    such as code running in a background thread.
    """
    def __init__(
        self,
        app,        # SlackApp
        response_url: Optional[str] = None,
        channel: Optional[str] = None,
        thread_ts: Optional[str] = None
    ):
        """
        Creates an instance of a Messenger based on the provided SlackAPp.

        Parameters
        ----------
        app: SlackApp
            The app context

        response_url: Optional[str]
            If provided, this becomes the default response URL in use with the
            send() method.

        channel: Optional[str]
            If provided, this becomes the default channel value in use with the
            send_channel() method.

        thread_ts: Optional[str]
            If provided, this becomes the default thread timestamp to use,
            and messages will be threaded.
        """
        super(Messenger, self).__init__()
        self.app = app
        self.response_url = response_url
        self.channel = channel

        if thread_ts:
            self['thread_ts'] = thread_ts

        self.client = WebClient(self.app.config.token)

    # noinspection PyProtectedMember
    def send_response(
        self,
        response_url: Optional[str] = None,
        **kwargs: Optional[Any]
    ):
        """
        This method is used to send a message via the response_url rathern
        than using the api.slack.com endpoints.

        Parameters
        ----------
        response_url: str
            The message will be POST to this URL; originates from a message received
            from api.slack.com

        Other Parameters
        ----------------
        Any other kwargs are passed as content into the message.

        Raises
        ------
        SlackApiError upon error sending; HTTP status code other
        than 200.

        Returns
        -------
        True if the message was sent without error (HTTP code 200).

        Notes
        -----
        Ideally this method should be a part of the `slackclient` BaseClient class to avoid
        using the internals of the client instance.  TODO: open issue with that repo.
        """
        req_args = dict(
            # contents of messenger[UserDict]
            **self,
            # any other API fields
            **kwargs
        )

        if self.client._event_loop is None:
            self.client._event_loop = _get_event_loop()

        api_url = response_url or self.response_url

        future = asyncio.ensure_future(
            self.client._request(
                http_verb='POST',
                api_url=api_url,
                req_args=dict(json=req_args)
            ),
            loop=_get_event_loop()
        )

        res = self.client._event_loop.run_until_complete(future)
        status = res['status_code']

        if status != 200:
            raise SlackApiError(
                message='Failed to send response_url: {}: status={}'.format(
                    api_url, status
                ),
                response=res
            )

        return True

    def send(self, channel=None, **kwargs):
        """
        Send a message to the User.

        Parameters
        ----------
        channel: str
           Direct the message to channel, rather than original channel value
           from instance initialization.

        Other Parameters
        ----------------
        user: str
            send a private message (via postEphemeral) to user
        """

        if 'user' in kwargs:
            api_call = self.client.chat_postEphemeral

        else:
            api_call = self.client.chat_postMessage

        return api_call(
            channel=channel or self.channel,
            # contents of messenger[UserDict]
            **self,
            # any other API fields provided by Caller
            **kwargs
        )
