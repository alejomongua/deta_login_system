from typing import Optional
from fastapi import FastAPI, Response, Header

from user import User, UserBaseModel

app = FastAPI(
    title="Login system",
    description="This is test of what I can do using Deta Micros and Deta Base",
    version="0.0.1",
)


@app.get("/")
def read_root():
    """Demo of a public route"""
    return {"Hello": "World"}


@app.post("/users", status_code=201)
def users_create(user: UserBaseModel, response: Response):
    """Register a user into the database"""
    new_user = User(user.email, user.password)
    response1 = new_user.insert()
    if 'error' in response1:
        response.status_code = 403

    return response1


@app.post("/users/login")
def users_authenticate(user: UserBaseModel, response: Response):
    """Identifies user already registered"""
    new_user = User(user.email, user.password)
    response1 = new_user.authenticate()
    if 'error' in response1:
        response.status_code = 403

    return response1


@app.delete('/users/login', status_code=403)
def users_logout(response: Response, authorization: Optional[str] = Header(None)):
    """Logs out user, invalidates token"""
    output = verify_token(authorization)
    if 'error' in output:
        return output

    response.status_code = 200
    user = User(output['email'])
    return user.expire_token()


@app.get('/users/check_token', status_code=403)
def users_check_token(response: Response, authorization: Optional[str] = Header(None)):
    """Check if token is valid and it's not expired"""
    output = verify_token(authorization)
    if 'error' in output:
        return output

    # Change default response code
    response.status_code = 200

    # Get user
    user = output['user']

    # Remove sensitive data
    user.user_in_db.pop('password')
    user.user_in_db.pop('token')

    # Rename key to email
    user.user_in_db['email'] = user.user_in_db.pop('key')

    # Return user
    return user.user_in_db


@app.post('/users/forgot_password', status_code=200)
def users_forgot_password(email: str):
    """Sends an email to recover access"""
    user = User(email)

    user.recover_password()

    return {'message': 'If email is registered, a recovery email was sent'}


@app.get('/users/recover_password', status_code=200)
def users_recovery_password(email: str, token: str, response: Response):
    """Recover access through an email"""
    user = User(email)
    response1 = user.verify_recover_password(token)
    if 'error' in response1:
        response.status_code = 403

    return response1


@app.get('/restricted_path', status_code=403)
def restricted_resource(response: Response, authorization: Optional[str] = Header(None)):
    """Demo of a private route"""

    output = verify_token(authorization)
    if 'error' in output:
        return output

    response.status_code = 200
    return {'secret': 'unclassified'}


def verify_token(authorization: str):
    """Verify authorization header to check if token is valid"""
    if authorization is None:
        return {'error': 'No authentication header found'}

    if not authorization.startswith('Bearer '):
        return {'error': 'Authentication header invalid'}

    token = authorization[7:]

    user = User('')

    output = user.check_token(token)

    if 'error' in output:
        return output

    return {'user': user}
