import os, time, logging, sys
from flask import Flask, request
from pymessenger.bot import Bot
from Planner import Planner


app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
users = {}

logger = logging.getLogger('testlogger')
formatter = logging.Formatter("%(asctime)15s "
                              "| %(filename)s "
                              "| line: %(lineno)d "
                              "| %(message)s")
stdoutHandler = logging.StreamHandler()
stdoutHandler.setFormatter(formatter)
logger.addHandler(stdoutHandler)
logger.setLevel(logging.INFO)
# logger.info(f"bot start up {time.time()}")

def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'POST':
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if recipient_id not in users:
                        users[recipient_id] = Planner(Bot(ACCESS_TOKEN), recipient_id, logger)
                    messageText = message['message'].get('text')
                    try:
                        users[recipient_id].process((messageText,))
                    except:
                        logger.exception(f"ERROR: could not process message {messageText} for user {recipient_id}", exc_info=True)
        return "Message Processed"
    else:
        """Before allowing people to message your bot, Facebook has implemented a verify token
                that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        response = verify_fb_token(token_sent)
        return response

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)

# why state machine running startPlan.next() after startPlan.run() and waiting for input? - checking if next state is none runs next()
# why sending multiple POST requests per message? - watermark post request
# how to pass information between states? context object in stateMachine to be passed around
# separate initial state from menu state
# update current book/chp every night
# camel case book name when responding to user
# congratulations message after finishing revelation
# better error message for no plan created yet / bad values
# back - getReadingRate()
# setCurrentReading() and getTomorrow() similar code
# thread sleep until reminder time, then send message to ask if read. if no, moved today's reading to tomorrow. check if reminder already exists? how to kill thread?
# store userId in plannerContext?
# if reminderTime is 101pm, 111pm, 121pm
# remove menu, add help option
# validate 1. | 1) | 1 | one
# ask if want to set reminder after starting plan
# if reading plan exists, and user tries starting new reading plan but errors, then current reading plan is gone? should still retain current reading plan
# separate state for getting book, then chapter number
# for yes/no questions, accepted answers are (yes, yup, sure, alright, ok, )
# what if user enters option that can't be lowercase? lock is stuck and next message tries to acquire lock but timeouts
# TODO: unit tests

#  why take so long to process first message? - usually when there is unprocessed message by user
# TODO?: option to read chronologically?
# TODO?: what if user reads more than daily amount?
# TODO?: option link facebook page
# TODO?: reward system for reading every day
# TODO?: randomly get bible verse thru API
""" 
TODO: Test Cases: 
    today/tomorrowReading/endDate when plan not set?
    starting book/chp outside of bible?
    starting chp/readingRate is '', negative
    readingRate > bible[book][chapters]? 100? 1000? 2000? 0?
    books:
        genesis
        1 peter
        song of solomon
        psalm / psalms
    reading rate:
        genesis 1 + 3
        genesis 48 + 3
        genesis 50 + 3
        jude 1 + 20
    missed reading:
        50-2   (read 2) -> 50-1
        50-2   (read 1) -> 50
        48-50 (read 0) -> 45-47
        48-50 (read 3) -> N/A
    back
    end date:
        current chp - revelation 20, rate - 3, next chap - revelation/genesis 1
        current chp - hebrews 1, rate - 56, next chap - revelation/genesis 1
    time:
        09:00am, 09:00 am, 12:00am , 9:30am, 9:30 am, 9am, 9 am, 12am, 930am, 930 am, 1230am, 1500, 15:30, 9, 1230, 101pm, hi, 1ty, 12amam, 1230amty, hi:00, 
    """
