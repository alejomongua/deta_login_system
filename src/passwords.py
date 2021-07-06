import base64
import hashlib
import os

def encode_password(password: str):
  """Generates a base64 encoded string with the hashed password and a random salt"""
  salt = os.urandom(32)
  key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

  # Store them as:
  storage = salt + key

  storage_str = base64.encodebytes(storage)
  return storage_str.decode()

def verify_password(password: str, storage: str):
  """Verify if password matches"""
  plain_storage = base64.decodebytes(storage.encode())

  salt = plain_storage[:32]
  key = plain_storage[32:]

  calculated_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

  return key == calculated_key
