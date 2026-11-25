from flask import Flask, render_template, request, jsonify, redirect, url_for
from helpers import hash
from storage import append_json_line
from pymongo import MongoClient
from pydantic import ValidationError
from models import EventSubmission, EventSubmissionRecord, CarSubmission, RiderSubmission
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# load in .env file and use environment variables to connect to Mongo
load_dotenv()
client = MongoClient(os.environ['CONNECTION_STRING'])
db = client[os.environ['DATABASE']]
events = db[os.environ['CONTAINER']]

# set up flask app
app = Flask(__name__, template_folder="templates")

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/api/send-event-to-mongo")
def sendEventToMongo():

    formData = request.get_json(silent=True) # silent=True suppresses warnings and returns None if there is an error
    if formData is None:
        return
    
    # validate form data and throw error if applicable
    try:
        validatedFormData = EventSubmission(**formData)
    except ValidationError as ve:
        print("Error:", ve.errors())
        return jsonify({"error": "validation error", "detail": ve.errors()}), 422
    
    received = datetime.now(timezone.utc)
    validatedFormDataDict = validatedFormData.dict()

    datetimeStr = str(validatedFormDataDict['eventDatetime']) # this is in the format yyyy-mm-dd hh:mm:ss but javascript has it in the format yyyy-mm-ddThh:mm
    datetimeStr = datetimeStr[:10] + 'T' + datetimeStr[11:16]

    strToHash = validatedFormDataDict['eventName'] + validatedFormDataDict['eventDesc'] + datetimeStr; # to do, change this to something that doesn't change, like the time of the event maybe idk
    print(strToHash)
    hashedStr = hash(strToHash)

    # add additional information for record keeping
    eventRecord = EventSubmissionRecord(
        **validatedFormData.dict(),
        receivedAt = received,
        eventHash = hashedStr,
        eventId = hashedStr[:6] # id is first six characters of hash
    )

    eventRecordDict = eventRecord.dict()
    eventRecordDict.update({'cars': []})

    # add to Mongo database along with empty array of cars
    append_json_line(eventRecordDict)
    events.insert_one(eventRecordDict)
    
    return jsonify({"status": "ok"}), 200

@app.get('/<eventId>')
def getEventPage(eventId):
    # get event from Mongo using its id
    event = events.find_one({'eventId' : eventId})
    # render it
    if (event is not None):

        eventDatetime = event['eventDatetime'] # this is in the format yyyy-mm-dd hh:mm:ss; we change it to be in the forms mm.dd.yyyy and hh:mm am/pm or hh am/pm if it's on the hour (eg. 12 pm)
        eventDate = str(eventDatetime.month) + '.' + str(eventDatetime.day) + '.' + str(eventDatetime.year)
        eventMin = eventDatetime.minute

        if (eventMin > 0 and eventMin < 10):
            eventMin = ':0' + str(eventMin)
        elif (eventMin == 0):
            eventMin = ''
        else:
            eventMin = ':' + str(eventMin)
        
        if (eventDatetime.hour > 12):
            eventTime = str(eventDatetime.hour - 12) + eventMin + " pm"
        elif (eventDatetime.hour == 12):
            eventTime = '12' + eventMin + 'pm'
        else:
            eventTime = str(eventDatetime.hour) + eventMin + " am"

        return render_template('event.html', eventName = event['eventName'], eventDesc = event['eventDesc'], eventLocation = event['eventLocation'], eventDate = eventDate, eventTime = eventTime)
    
    return render_template('eventDNE.html', eventId = eventId)
    