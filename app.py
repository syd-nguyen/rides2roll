from flask import Flask, render_template, request, jsonify, redirect, url_for
#from storage import append_json_line
from pymongo import MongoClient
from pydantic import ValidationError
# from models import EventSubmission, EventSubmissionRecord, CarSubmission, RiderSubmission
from datetime import datetime, timezone
from hashlib import sha256
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