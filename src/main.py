from typing import Optional
from fastapi import FastAPI, Response, Header

from user import User, UserBaseModel, NewPassword

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
    new_user = User(user.email)
    response1 = new_user.insert(user.password)
    if 'error' in response1:
        response.status_code = 403

    return response1


@app.post("/users/login")
def users_authenticate(user: UserBaseModel, response: Response):
    """Identifies user already registered"""
    new_user = User(user.email)
    response1 = new_user.authenticate(user.password)
    if 'error' in response1:
        response.status_code = 403

    return response1


@app.delete('/users/login')
def users_logout(response: Response, access_token: Optional[str] = Header(None)):
    """Logs out user, invalidates token"""
    output = verify_token(access_token)
    if 'error' in output:
        response.status_code = 403
        return output

    user = output['user']
    return user.expire_token()


@app.get('/users/check_token')
def users_check_token(response: Response, access_token: Optional[str] = Header(None)):
    """Check if token is valid and it's not expired"""
    output = verify_token(access_token)
    if 'error' in output:
        response.status_code = 403
        return output

    # Change default response code

    # Get user
    user = output['user']

    # Remove sensitive data
    user.user_in_db.pop('password')
    user.user_in_db.pop('token')

    # Rename key to email
    user.user_in_db['email'] = user.user_in_db.pop('key')

    # Return user
    return user.user_in_db


@app.post('/users/forgot_password')
def users_forgot_password(email: str):
    """Sends an email to recover access"""
    user = User(email)

    user.recover_password()

    return {'message': 'If email is registered, a recovery email was sent'}


@app.get('/users/recover_password')
def users_recovery_password(email: str, token: str, response: Response):
    """Recover access through an email"""
    user = User(email)
    response1 = user.verify_recover_password(token)
    if 'error' in response1:
        response.status_code = 403

    return response1


@app.post('/users/update_password', status_code=200)
def users_update_password(user: UserBaseModel,
                          new_password: NewPassword,
                          response: Response,
                          access_token: Optional[str] = Header(None)):
    """Allows a user change it's own password,
    for security, it needs current password"""
    output = verify_token(access_token)
    if 'user' not in output:
        response.status_code = 403
        return output

    token_user = output['user']

    if token_user.email != user.email:
        response.status_code = 403
        return {'error': "You are not allowed to change this users' password"}

    output = token_user.update_password(
        user.password, new_password.new_password)
    if 'error' in output:
        response.status_code = 403
        return output

    return {'success': True}


@app.get('/restricted_path')
def restricted_resource(response: Response, access_token: Optional[str] = Header(None)):
    """Demo of a private route"""

    output = verify_token(access_token)
    if 'error' in output:
        response.status_code = 403
        return output

    return {'secret': 'unclassified'}


def verify_token(token: str):
    """Verify access token header to check if token is valid"""
    if token is None:
        return {'error': 'No access-token header found'}

    user = User('')

    output = user.check_token(token)

    if 'error' in output:
        return output

    return {'user': user}
