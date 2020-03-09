import hmac
import hashlib
import time


def verify_request(
    *,
    timestamp: str,
    signature: str,
    request_data: bytes,
    signing_secret: str
) -> bool:
    """
    This function validates the received using the process described
    https://api.slack.com/docs/verifying-requests-from-slack and
    using the code in https://github.com/slackapi/python-slack-events-api

    Parameters
    ----------
    timestamp: str
        originates from headers['X-Slack-Request-Timestamp']

    signature: str
        originates from headers['X-Slack-Signature']

    request_data: bytes
        The originating request byte-stream; if using
        Flask, then originates from request.get_data()

    signing_secret : str
        originates from the App config

    Returns
    -------
    bool
        True if signature is validated
        False otherwise
    """

    if abs(time.time() - int(timestamp)) > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        return False

    req = str.encode('v0:' + str(timestamp) + ':') + request_data

    request_hash = 'v0=' + hmac.new(
        str.encode(signing_secret),
        req, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(request_hash, signature)
