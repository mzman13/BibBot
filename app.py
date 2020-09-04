import os, time
from flask import Flask, request
from pymessenger.bot import Bot
from Planner import Planner

startTime = time.time()
app = Flask(__name__)
# ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
# VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
ACCESS_TOKEN = "EAAw80bZAYciMBAAZBcoXpnIxZANsm66HCatKZBJj1Hu8iFrd6a39BDSUe6PNvbcfx3qp7ideRbklDZA2Ej6KMwM5GlLFnqttArTrULVwJmdofr3B6JPRTVNp6SNoLVwBfLZC2HgE3QZBEzrsGtwyn9xxvYtJ6Ja7VHTHcJ8IJOisgZDZD"
VERIFY_TOKEN = "PXuyXrrJXoX5m2jHqyVj4cQvpzUqXYqWTlO7BRSC7HVZVgo9la7Y7WA3L3xZZXZbkd4akW"
users = {}
# print(f"bot start up {time.time() - startTime}")

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
        # startTime = time.time()
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if recipient_id not in users:
                        users[recipient_id] = Planner(Bot(ACCESS_TOKEN))
                    messageText = message['message'].get('text')
                    try:
                        users[recipient_id].process((messageText, recipient_id,))
                    except:
                        print(f"ERROR: could not find {recipient_id} in users!")
        # print(f"post process {time.time() - startTime}")
    return "Message Processed"

if __name__ == '__main__':
    app.run()


# TODO: why take so long to process first message? - usually when there is unprocessed message by user
# why state machine running startPlan.next() after startPlan.run() and waiting for input? - checking if next state is none runs next()
# why sending multiple POST requests per message? - watermark post request
# how to pass information between states? context object in stateMachine to be passed around
# separate initial state from menu state
# update current book/chp every night
# camel case book name when responding to user
# TODO: congratulations message after finishing revelation
# better error message for no plan created yet / bad values
# TODO: thread track reminder time
# TODO: random verse
# TODO?: option to ready chronologically?
# TODO?: have tutorials?
# TODO?: what if user reads more than daily amount?
# setCurrentReading() and getTomorrow() similar code
# TODO?: if reading plan exists, and user tries starting new reading plan but errors, then current reading plan is gone? should still retain current reading plan
# TODO: back option
""" 
TODO: Test Cases: 
    today/tomorrowReading/endDate when plan not set?
    starting book/chp outside of bible?
    starting chp/readingRate is '', negative
    readingRate > bible[book][chapters]? 100? 1000? 2000? 0?
    reading rate:
        genesis 1 + 3
        genesis 48 + 3
        genesis 50 + 3
    missed reading:
        50-2   (read 2) -> 50-1
        50-2   (read 1) -> 50
        48-50 (read 0) -> 45-47
        48-50 (read 3) -> N/A
    """
