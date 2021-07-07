import manage_tokens
import passwords
from deta import Deta
import time
import secrets
import os
import json
f"""Users model"""


TWO_WEEKS = 60 * 60 * 24 * 14
THIS_FILE_DIR = '/'.join(os.path.realpath(__file__).split('/')[0:-1])
with open(f'{THIS_FILE_DIR}/secrets.json') as jsonfile:
    PROJECT_SECRET = json.load(jsonfile)['project']


class User():
    """Main user model class"""
    deta = Deta(PROJECT_SECRET)
    users_db = deta.Base('users_main')

    def __init__(self, email, password=''):
        self.email = email
        self.password = password
        self.user_in_db = None
        self.is_verified = False

    def insert(self):
        """Inserts user into database if does not exist"""
        self.user_in_db = User.users_db.get(self.email)
        if self.user_in_db:
            return {'error': 'User already exists'}

        password = passwords.encode_password(self.password)

        self.user_in_db = {'key': self.email, 'password': password}
        User.users_db.insert(self.user_in_db)

        return {'success': True}

    def authenticate(self):
        """Authenticates user with login and password"""

        self.user_in_db = User.users_db.get(self.email)
        if not self.user_in_db:
            # User does not exist
            return {'error': 'Invalid email and password combination'}

        stored_password = self.user_in_db['password']
        password_valid = passwords.verify_password(
            self.password, stored_password)

        if not password_valid:
            # Invalid password
            return {'error': 'Invalid email and password combination'}

        # Generate a random token
        token = secrets.token_hex(12)

        self.user_in_db.update({'token': token})

        User.users_db.put(self.user_in_db)

        generated = time.time()
        expires = generated + TWO_WEEKS

        output_jwt = manage_tokens.encode({
            'email': self.email,
            'token': token,
            'generated': generated,
            'expires': expires,
        })

        return {'token': output_jwt}

    def check_token(self, token):
        """Checks if a token is valid"""
        decoded_token = manage_tokens.decode(token)
        if decoded_token is None:
            return {'error': 'Token is invalid'}

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

    def update_password(self, new_password: str):
        """Updates user's password"""
        self.user_in_db = User.users_db.get(self.email)
        if not self.user_in_db:
            # User does not exist
            return {'error': 'User does not exists'}

        password = passwords.encode_password(self.password)

        self.user_in_db.update({'password': password})

        return {'success': True}
