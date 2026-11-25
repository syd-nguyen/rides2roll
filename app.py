from flask import Flask, render_template, request, jsonify, redirect, url_for
#from storage import append_json_line
from pymongo import MongoClient
from pydantic import ValidationError
# from models import EventSubmission, EventSubmissionRecord, CarSubmission, RiderSubmission
from datetime import datetime, timezone
from hashlib import sha256
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates")

client = os.environ['CONNECTION_STRING']
db = os.environ['DATABASE']
events = os.environ['CONTAINER']
client = MongoClient(os.environ['CONNECTION_STRING'])
db = client[os.environ['DATABASE']]
events = db[os.environ['CONTAINER']]