
from flask import Flask, Blueprint
from slackapptk.app import SlackApp

flaskapp = Flask(__package__)

slackapp = SlackApp()

blueprint = Blueprint(__package__, __name__,
                      url_prefix="/api/v1",
                      static_folder='static')
