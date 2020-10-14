# Python3 Toolkit for building Slack apps

The `slackapptk` package is used to facilitate the development of Slack
applications using Python3 and your choice of web frameworks.  As a developer
of Slack apps in Python, I want a library that would allow me to accomplish two
primary goals:

1.  Provide a mechanism to route messages received from *api.slack.com* to 
the proper code in my app.  This process is sometimes referred to callback
routing. 
  
1.  Create /slash-commands with a rich set of feature capabiltiies as 
found using the Python standard [argparse](https://docs.python.org/3/library/argparse.html) package.

_NOTE:  The slapapptk package uses the Slack provided [slackclient](https://github.com/slackapi/python-slackclient)
package and is not meant to be a replacement.  That said, there are _widgets_ defined
in `slackapptk.web` that are not yet available in slackclient; and as slackclient is updated
these widgets will be depreciated_


# NOTE: For SlackClient <= 2.5

If you are looking to develop on the Slack Client 2.5.0 release, please use the branch `v1`.

# TLDR; See working example

The documentation for using `slackapptk` is currently under development.  That
said you can find a complete working example that uses the Flask web-framework
in [example-slackapp](example-slackapp); see that
[README.md](example-slackapp/README.md) more details.


# Overview

A Slack app can receive messages from api.slack.com for a number of reasons and depending
on the way the app was configured in the api.slack.com portal.  

For the purpose of this `README` the term _entrypoint_ will be used:

   * User entered a */slash-command*
   * User initiaties some kind of *interactivity* request, for example clicking a button
   * User actuates a dropdown and the app has to fetch data from an *external source*
   * User selected an *action* attached to a Slack message
   * App receives a Slack *Event* as a result of its configured subscriptions

The term _request_ will refer to the message recieved from api.slack.com as a result of
any of these entrpoints.

When the app is configured in the api.slack.com portal, the developer will
identify the specific app API routes to invoke.  The developer would then need
to write the prerequist code handlers using their API framework of choice,
Flask for example.

To create a an app instance:

```python
from slackapptk.app import SlackApp

app = SlackApp()
app.config.token = "<My app bot token value>"
app.config.signing_secret = "<My app signing secret"
```

You can bind your application specific code to handle inbound api.slack.com
messages using the following:

* `app.ic.<interactive-component>.on` - where <interactive-component> is one of the following
   * `block_actions` - to bind callbacks for block action request
   * `select` - to bind callbacks for external menu select population
   * `view` - to bind callbacks for View submission
   * `view_closed` - to bind callbacks for View closed
   * `imsg` - to bind callbacks to interactive message attachaments _(outmoded)_
   * `dialog` - to bind callbacks to Dialog submit _(outmoded)_

* `app.commands.register` - to register your /slash-command parser and callback handler
* `app.events` - to register all for any Event subscriptions   

To process inbound messages from api.slack.com you will need to call one of the app
handlers from the context of the API route handler.  For example, if you defined
an API route handler for one of your /slash-commands, you would call
`app.handler_slash_command()` to process ihe message.

## Example 

A primary motivator for slackapptk is to receive the request and direct it to
the app entrypoint handler that is specific to the request payload.  Consider
an example where the app presents the User with a surface that contains a
button, and the User clicks on that button. The app code creates the button in
a block, and then binds that block ID to the app "interactive component"
handler for block IDs, as shown in this code snippet:

````python
from slack.web.classes.blocks import SectionBlock
from slack.web.classes.elements import ButtonElement

from slackapptk.app import SlackApp
from slackapptk.request.interactive import BlockActionRequest, ActionEvent
from slackapptk.response import Response

def demo(app: SlackApp):

    # this function uses the provided app to send a message to the User so that
    # they can click a button.  Note this is an incomplete example, but used to
    # show the machanics of the of the entrypoint bind / callback mechanism.

    block = SectionBlock(
        block_id='this is the block id',
        text='Click the button and see what happens',
        accessory=ButtonElement(
            text='Click Me',
            action_id='button action id',
            value='10'
        )
    ) 
    
    # register the block-id callback to the function for handling when the User
    # clicks the button.  

    app.ic.block_actions.on(block.block_id, on_block_button)
    
    # ... assume some code that sends the above block in a Slack
    # surface like a message or modal view ...


def on_block_button(
    rqst: BlockActionRequest,
    action: ActionEvent
):
    # this function is called when the app receives the request message from
    # api.slack.com when the User clicked the button.

    # send a message back to the User indicating the value of the button

    resp = Response(rqst)
    resp.send("button pressed, block vlaue is: %s", action.value)
````

The registration / callback mechanism could also be coded as a decorator, for
example:

````python

    @app.ic.block_actions.on(block.block_id)
    def on_block_button(
        rqst: BlockActionRequest,
        action: ActionEvent
    ):
        # this function is called when the app receives the request message from
        # api.slack.com when the User clicked the button.
    
        # send a message back to the User indicating the value of the button
    
        resp = Response(rqst)
        resp.send("button pressed, block vlaue is: %s", action.value)

````
