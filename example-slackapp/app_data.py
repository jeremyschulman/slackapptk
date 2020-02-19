
from flask import Flask
from slackapp2pyez.app import SlackApp


flaskapp = Flask(__package__)
slackapp = SlackApp()


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
