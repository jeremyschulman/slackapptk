from typing import Optional, Callable

import re
from fnmatch import fnmatch
import sre_constants


__all__ = ['make_matcher']


def make_matcher(
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

    if not regex:
        def fnmatch_matcher(value):
            return fnmatch(value, pattern)

        return fnmatch_matcher

    # regular expression based matching

    try:
        re_pattern = re.compile(pattern, re.IGNORECASE)

    except sre_constants.error:
        raise ValueError(
            f'Bad regular expression: {pattern}',
        )

    def regex_matcher(value):
        return bool(re_pattern.match(value))

    return regex_matcher
