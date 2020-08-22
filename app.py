import random, os
from flask import Flask, request
from pymessenger.bot import Bot


app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)

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
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    messageText = message['message'].get('text')
                    if messageText.lower() == '1':
                        response = startPlan()
                    elif messageText.lower() == '2':
                        response = getTodayReading()
                    elif messageText.lower() == '3':
                        response = getYesterdayReading()
                    elif messageText.lower() == '4':
                        response = getTomorrowReading()
                    elif messageText.lower() == '2nd Chronicles 26':
                        response = "How Many Chapters Will You Read a Day?"
                    else:
                        response = getMenu()
                    send_message(recipient_id, response)
    return "Message Processed"

def getMenu():
    return "Hi, Welcome to BibleBot! Please enter the number for the option you want.\n"\
           "1) Start New Reading Plan\n"\
           "2) Get Today's Reading\n"\
           "3) Get Yesterday's Reading\n"\
           "4) Get Tomorrow's Reading"

def startPlan():
    return "Enter the Book and Chapter you are starting on"

def getYesterdayReading():
    return "2nd Chronicles 23 - 25"

def getTodayReading():
    return "2nd Chronicles 26 - 34"

def getTomorrowReading():
    return "2nd Chronicles 35 - 36, Ezra 1 - 4"

# chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!",
                        "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == '__main__':
    app.run()
