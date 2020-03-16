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

from typing import Optional, Any
import asyncio
import aiohttp
from aiohttp import ClientResponse

from collections import UserDict
from slack.web.client import WebClient
from slack.errors import SlackApiError


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

    # async def _request(self, *, api_url, req_args):
    #
    #     session = aiohttp.ClientSession(
    #         timeout=aiohttp.ClientTimeout(total=self.client.timeout)
    #     )
    #
    #     res = await session.post(api_url, json=req_args)
    #     await session.close()
    #     return res

    # noinspection PyProtectedMember
    def send_response(
        self,
        response_url: Optional[str] = None,
        **kwargs: Optional[Any]
    ):

        req_args = dict(
            # contents of messenger[UserDict]
            **self,
            # any other API fields
            **kwargs
        )

        if self.client._event_loop is None:
            self.client._event_loop = self.client._get_event_loop()

        api_url = response_url or self.response_url

        future = asyncio.ensure_future(
            self.client._request(
                http_verb='POST',
                api_url=api_url,
                req_args=dict(json=req_args)
            ),
            loop=self.client._get_event_loop()
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

    def send(self, **kwargs):
        """
        Used to send a message to the User.

        Other Parameters
        ----------------
        if 'user' in kwargs, this indicates the Caller wants to send a private
        message (via postEphemeral)

        if 'channel' in kwargs, this indicates the Caller wants to direct
        the message to channel, rather than original channel value from
        instance initialization.
        """

        if 'user' in kwargs:
            api_call = self.client.chat_postEphemeral

        else:
            api_call = self.client.chat_postMessage

        return api_call(
            channel=kwargs.get('channel') or self.channel,
            # contents of messenger[UserDict]
            **self,
            # any other API fields provided by Caller
            **kwargs
        )
