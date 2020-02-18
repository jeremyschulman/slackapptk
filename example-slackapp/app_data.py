
from flask import Flask
from slackapp2pyez.app import SlackApp


slackapp = SlackApp()

flaskapp = Flask(__package__)


# class MyEventAdapter(SlackEventAdapter):
#     def emit(self, event, *args, **kwargs):
#         print(f"Event>> {event}")
#         print("Body >> {}".format(json.dumps(args[0], indent=3)))
#         super(MyEventAdapter, self).emit(event, *args, **kwargs)
#
#
# def create_event_adapter(flaskapp, secret):
#     global slack_event_adapter
#     slack_event_adapter = SlackEventAdapter(
#         signing_secret=secret,
#         endpoint='/slack/event',
#         server=flaskapp)
