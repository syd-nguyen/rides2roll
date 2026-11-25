from hashlib import sha256

def hash(str):
    return sha256(str.encode('utf-8')).hexdigest()