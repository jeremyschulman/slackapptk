from typing import Optional, Callable

import re
import fnmatch
import sre_constants


__all__ = ['match_maker']


def match_maker(
    pattern: str,
    regex: Optional[bool] = False
) -> Callable:
    """
    This function returns a function that is responsible for determining a
    string-pattern-match.  This program supports two different types of
    pattern matching.  By default it uses wildcard "glob" matching.

    Parameters
    ----------
    pattern : str
        The matching pattern "tr*"

    regex : bool
        If True then `pattern` is a Python regular express
        If False then `pattern` is a glob wildcard

    Returns
    -------
    Callable[str] -> bool
    """

    # if not regular expression it will be treated as glob wildcard
    # translate the glob pattern to a regex pattern so we can use
    # the same regex processing below.

    if not regex:
        pattern = fnmatch.translate(pattern)

    # create the pattern matching ignoring case.

    try:
        match = re.compile(pattern, re.IGNORECASE).match

    except sre_constants.error:
        raise ValueError(
            f'Bad regular expression: {pattern}',
        )

    def matcher(value):
        return bool(match(value))

    matcher.pattern = pattern
    return matcher
