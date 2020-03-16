"""
This is the main entrypoint file for the sample Slack app.  This file should be
called from the "./run.sh" script which is a simple wrapper for invoking python
on this file.
"""

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from werkzeug import run_simple

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from app import create_app


# -----------------------------------------------------------------------------
#
#                                 MAIN CODE BEGINS
#
# -----------------------------------------------------------------------------


def main():

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
