from hashlib import sha256

def hash(str):
    return sha256(str.encode('utf-8')).hexdigest()

def getEvent(eventId):
    return events.find_one({'eventId' : eventId})

def getEventCars(eventId, driverName):
    return getEvent(eventId)['cars']