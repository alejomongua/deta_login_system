import json
import os

import jwt

THIS_FILE_DIR = '/'.join(os.path.realpath(__file__).split('/')[0:-1])
with open(f'{THIS_FILE_DIR}/secrets.json') as jsonfile:
    JWT_SECRET = json.load(jsonfile)['main']

def encode(payload: dict):
    """Generate an encoded JWT"""
    return jwt.encode(payload, JWT_SECRET)

def decode(token: str):
    """Gets payload from an encoded token"""
    try:
        return jwt.decode(token, JWT_SECRET)
    except jwt.exceptions.InvalidTokenError:
        # Something went wrong
        return None
