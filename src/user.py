import re
from typing import Optional
from pydantic.main import BaseModel
import email_sender
import manage_tokens
import passwords
from deta import Deta
import time
import secrets
import os
import json
f"""Users model"""


TWO_WEEKS = 60 * 60 * 24 * 14
TWO_HOURS = 60 * 60 * 2
THIS_FILE_DIR = '/'.join(os.path.realpath(__file__).split('/')[0:-1])
with open(f'{THIS_FILE_DIR}/secrets.json') as jsonfile:
    PROJECT_SECRET = json.load(jsonfile)['project']

VALID_EMAIL_REGEX = re.compile(
    '^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$')


class UserBaseModel(BaseModel):
    email: str
    password: Optional[str] = None


class NewPassword(BaseModel):
    new_password: Optional[str] = None


class User():
    """Main user model class"""
    deta = Deta(PROJECT_SECRET)
    users_db = deta.Base('users_main')

    def __init__(self, email):
        self.email = email
        self.user_in_db = None
        self.verified = False

    def insert(self, password, redirect_to):
        """Inserts user into database if does not exist"""
        self.user_in_db = User.users_db.get(self.email)
        if self.user_in_db:
            return {'error': 'User already exists'}

        validation = self.validate(password)

        if validation:  # If dict is not empty
            validation.update({'error': 'Validation errors'})
            return validation

        password = passwords.encode_password(password)

        self.user_in_db = {
            'key': self.email,
            'password': password,
            'verified': False,
            'secret_token': secrets.token_hex(12)
        }
        User.users_db.insert(self.user_in_db, redirect_to)

        return {'success': True, 'message': 'Please check your email'}

    def authenticate(self, password):
        """Authenticates user with login and password"""

        self.user_in_db = User.users_db.get(self.email)
        if not self.user_in_db:
            # User does not exist
            return {'error': 'Invalid email and password combination'}

        if not self.user_in_db['verified']:
            # User does not exist
            return {'error': 'Email not verified'}

        output = self.verify_password(password)
        if 'error' in output:
            return output

        return {'token': self.generate_jwt()}

    def check_token(self, token):
        """Checks if a token is valid"""
        decoded_token = manage_tokens.decode(token)
        if decoded_token is None:
            return {'error': 'Token is invalid'}

        if 'email' not in decoded_token or 'expires' not in decoded_token \
                or 'token' not in decoded_token:
            return {'error': 'Token is invalid'}

        self.email = decoded_token['email']
        self.user_in_db = User.users_db.get(decoded_token['email'])

        if not self.user_in_db:
            # User does not exist
            return {'error': 'User does not exist'}

        if self.user_in_db['token'] != decoded_token['token']:
            return {'error': 'Token is invalid'}

        if decoded_token['expires'] < time.time():
            return {'error': 'Token is expired'}

        return decoded_token

    def expire_token(self):
        """Expires token, for example, for logout"""
        self.user_in_db = User.users_db.get(self.email)

        self.user_in_db.update({'token': ''})

        User.users_db.put(self.user_in_db)

        return {'success': True}

    def update_password(self, old_password: str, new_password: str):
        """Updates user's password"""
        self.user_in_db = User.users_db.get(self.email)
        if not self.user_in_db:
            # User does not exist
            return {'error': 'User does not exists'}

        output = self.verify_password(old_password)
        if 'error' in output:
            return output

        validation = self.validate(new_password)

        if validation:  # If dict is not empty
            validation.update({'error': 'Validation errors'})
            return validation

        password = passwords.encode_password(new_password)

        self.user_in_db.update({'password': password})
        User.users_db.put(self.user_in_db)

        return {'success': True}

    def recover_password(self):
        """Sends an email to recover access"""
        self.user_in_db = User.users_db.get(self.email)
        if not self.user_in_db:
            # User does not exist
            return

        recovery_token = manage_tokens.encode({
            'email': self.email,
            'expires': time.time() + TWO_HOURS,
        })
        email_sender.recover_password(self.email, recovery_token)

    def verify_recover_password(self, token):
        decoded_token = manage_tokens.decode(token)
        if decoded_token is None:
            return {'error': 'Token is invalid'}

        if 'email' not in decoded_token or 'expires' not in decoded_token \
                or decoded_token['email'] != self.email:
            return {'error': 'Token is invalid'}

        self.user_in_db = User.users_db.get(decoded_token['email'])

        if not self.user_in_db:
            # User does not exist
            return {'error': 'User does not exist'}

        if decoded_token['expires'] < time.time():
            return {'error': 'Token is expired'}

        return {'token': self.generate_jwt()}

    def generate_jwt(self):
        """Generates a JWT for an authenticated user"""

        # Generate a random token
        random_token = secrets.token_hex(12)

        # Update database
        self.user_in_db.update({'token': random_token})
        User.users_db.put(self.user_in_db)

        # Create timestamps for the token
        generated = time.time()
        expires = generated + TWO_WEEKS

        # Return the generated jwt
        return manage_tokens.encode({
            'email': self.email,
            'token': random_token,
            'generated': generated,
            'expires': expires,
        })

    def verify_password(self, password):
        """Checks if input password matches"""
        stored_password = self.user_in_db['password']
        password_valid = passwords.verify_password(
            password, stored_password)

        if not password_valid:
            # Invalid password
            return {'error': 'Invalid email and password combination'}

        return {'success': True}

    def validate(self, password):
        """Validates email and password"""

        response = {}

        if not VALID_EMAIL_REGEX.match(self.email):
            response['email'] = 'not valid'

        if len(password) < 8:
            response['password'] = 'too short, must have at least 8 characters'

        return response

    def validate_email(self, token):
        """Recieves the token for email validation"""
        decoded_token = manage_tokens.decode(token)
        if decoded_token is None:
            return {'error': 'Token is invalid'}

        self.user_in_db = User.users_db.get(self.email)
        if not self.user_in_db:
            # User does not exist
            return {'error': 'User does not exist'}

        if 'secret_token' not in decoded_token or decoded_token['secret_token'] != self.user_in_db['secret_token']:
            return {'error': 'Token is invalid'}

        self.user_in_db['secret_token'] = ''
        self.user_in_db['verified'] = True

        User.users_db.put(self.user_in_db)

        return decoded_token

    def send_verify_email(self, redirect_to):
        """Sends and email to verify the user's address"""
        if not self.user_in_db:
            self.user_in_db = User.users_db.get(self.email)
            if not self.user_in_db:
                # User does not exist
                return

        if self.user_in_db['verified']:
            return

        if not self.user_in_db['secret_token']:
            self.user_in_db['secret_token'] = secrets.token_hex(12)
            User.users_db.put(self.user_in_db)

        token = manage_tokens.encode({
            'secret_token': self.user_in_db['secret_token'],
            'redirect_to': redirect_to,
        })

        email_sender.welcome(self.email, token)
