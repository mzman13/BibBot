import os, time
from flask import Flask, request
from pymessenger.bot import Bot
from Planner import Planner

startTime = time.time()
app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)
planner = Planner(bot)
print(f"bot start up {time.time() - startTime}")

def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    else:
        startTime = time.time()
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    messageText = message['message'].get('text')
                    planner.process((messageText, recipient_id,))
        print(f"post process {time.time() - startTime}")
    return "Message Processed"

if __name__ == '__main__':
    app.run()


# TODO: why take so long to process first message?
# why sending multiple POST requests per message? - watermark post request
# TODO: how to pass information between states? context object in stateMachine to be passed around
