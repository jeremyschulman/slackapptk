from slackapptk.verify_request import verify_request as stk_verify_request


def verify_request(
    request,
    signing_secret: str
) -> bool:
    """
    This function validates the received using the process described
    https://api.slack.com/docs/verifying-requests-from-slack and
    using the code in https://github.com/slackapi/python-slack-events-api

    Parameters
    ----------
    request : flask.request

    signing_secret: str
        The app signing-secret value from config

    Returns
    -------
    bool
        True if signature is validated
        False otherwise
    """
    return stk_verify_request(
        timestamp=request.headers['X-Slack-Request-Timestamp'],
        signature=request.headers['X-Slack-Signature'],
        request_data=request.get_data(),
        signing_secret=signing_secret
    )
