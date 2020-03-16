# Example Slack App

This directory contains a basic working slack app.  Before you begin working
with this app, you should be familiar with setting up the Slack API aspects on
[api.slack.com](https://api.slack.com).  

In order for you app to connect with Slack, your app must be reachable by the
Slack API system.  You can use the program [ngrok](https://ngrok.com/) for this purpose,
as described in this [article](https://api.slack.com/tutorials/tunneling-with-ngrok).

# Before you begin

You will need to export the following environment variables, whose values
are obtained from your app configuration in api.slack.com:

```shell script
$ export SLACK_APP_TOKEN=<your-app-bot-token>
$ export SLACK_APP_SIGNING_SECRET=<your-all-signing-secret>
$ source setup.env
```

If you want to change the Flask app port used for this demonstration, you can
edit the file [flaskapp.env](flaskapp.env) and change the `PORT` value. 

You will then need to create a virtual enviornment, activate it, and
then install the example app requirements:

```shell script
(venv)$ pip install -r requirements.txt
```

# Running the example

Once you have everything configured and setup properly, you can start the example 
application:

```shell script
$ ./run.sh
```

You should see output similar to this:

```shell script
/api/v1/slack/request
/api/v1/slack/select
/api/v1/slack/command/<name>
/api/v1/static/<path:filename>
/static/<path:filename>
/api/v1/slack/request
/api/v1/slack/select
/api/v1/slack/command/<name>
/api/v1/static/<path:filename>
/static/<path:filename>
```

You can then go to your Slack client and issue the "/demo" command.  You will be presented
with a message containing a menu-selector.  You can also issue:

```shell script
/demo --help            # will display the demo help-test
/demo --version         # will display the demo version string
```  

Good luck and have fun!
