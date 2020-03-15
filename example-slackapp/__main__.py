"""
This is the main entrypoint file for the sample Slack app.  This file should be
called from the "./run.sh" script which is a simple wrapper for invoking python
on this file.
"""

from werkzeug import run_simple

# disable SSL warnings, and such ... this is only done here in the "app/run" so we don't hardcode
# this disable anywhere in the package files.

from urllib3 import disable_warnings
from app import create_app


def main():
    disable_warnings()

    app = create_app()
    hostname, port = app.config["HOST"], int(app.config["PORT"])

    run_simple(
        hostname=hostname, port=port,
        application=app,
        threaded=bool(app.config["THREADING"]),
        use_reloader=True,
        use_evalex=True
    )


if __name__ == "__main__":
    main()
