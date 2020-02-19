import hmac
import hashlib
import time


def verify_request(*, request, signing_secret) -> bool:
    """
    This function validates the received using the process described
    https://api.slack.com/docs/verifying-requests-from-slack and
    using the code in https://github.com/slackapi/python-slack-events-api

    Parameters
    ----------
    request : flask.request
    signing_secret : str

    Returns
    -------
    bool
        True if signature is validated
        False otherwise
    """
    timestamp = request.headers['X-Slack-Request-Timestamp']

    if abs(time.time() - int(timestamp)) > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        return False

    signature = request.headers['X-Slack-Signature']

    req = str.encode('v0:' + str(timestamp) + ':') + request.get_data()

    request_hash = 'v0=' + hmac.new(
        str.encode(signing_secret),
        req, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(request_hash, signature)