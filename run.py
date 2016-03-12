from flask import Flask, request, redirect, render_template
from pymongo import MongoClient
import twilio.twiml, os, time

server_url = "http://apps.vishnu.io:5000"

client = MongoClient()
db = client.nyphack

app = Flask(__name__)

@app.route("/")
def index_page():
    return "Hello"
 
#recieves sms from Twilio and sends back link to compose message
@app.route("/process_sms", methods=['GET', 'POST'])
def process_sms():
    phone_number = request.values.get('From', None)
    message = request.values.get('Body', None)
    resp = twilio.twiml.Response()
    
    #check if sender's phone number is registered
    valid_number = db.users.find_one({"phone_number" : phone_number})
    if valid_number is not None:
        token = os.urandom(8).encode('hex')
        db.tokens.insert_one({"token": token, "phone_number": phone_number, "time": int(time.time())})
        resp.message("Hi! Tap the link below to send a secure message to the doctor.")
        resp.message(server_url + "/compose/" + token)
    else:
        resp.message("Your number was not recognized as belonging to a current patient. Register at the following link:")
        resp.message(server_url + "/register/" + phone_number)
    
    return str(resp)

#renders form to compose message
@app.route("/compose/<token>", methods=['GET', 'POST'])
def compose(token):
    valid_token = db.tokens.find_one({"token": token})
    if valid_token is not None:
        return render_template('compose.html')
    else:
        return "Invalid Link"
	

#saves message to database
@app.route("/send", methods=['GET', 'POST'])
def save():
    message = request.values.get('message', None)
    
    #validate the token, then insert the message
    db.messages.insert_one({"message": message, "time": int(time.time())})
    return "ok"
    
#register a new phone number
@app.route("/register/<phone_number>")
def register(phone_number):
    return render_template('register.html', phone_number=phone_number)
	
#process new registration
@app.route("/process_registration", methods=['GET', 'POST'])
def process_registration():
    first_name = request.values.get('first_name', None)
    last_name = request.values.get('last_name', None)
    phone_number = request.values.get('phone_number', None)
    db.users.insert_one({"first_name": first_name, "last_name": last_name, "phone_number": phone_number})
    return "ok"

#doctor dashboard
@app.route("/dashboard")
def dashboard():
    return "Dashboard goes here"
 
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')