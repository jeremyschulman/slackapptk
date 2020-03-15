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

__all__ = ['create_logger']

_default_logfile = 'slackapptk-example.log'
_default_format = '%(asctime)s:%(levelname)s:%(message)s'


def create_logger(logformat=None, logfile=None, stream=None):

    log = logging.getLogger(__package__)
    log.setLevel(logging.INFO)
    formatter = logging.Formatter(logformat or _default_format)

    fh = logging.FileHandler(logfile or _default_logfile)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    if stream:
        fh = logging.StreamHandler(stream)
        fh.setFormatter(formatter)
        log.addHandler(fh)

    return log
