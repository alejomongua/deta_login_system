from typing import Optional
from fastapi import FastAPI, Response, Header

from user import User

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.post("/users", status_code=201)
def users_create(email: str, password: str, response: Response):
    """Register a user into the database"""
    new_user = User(email, password)
    response1 = new_user.insert()
    if 'error' in response1:
        response.status_code = 403

    return response1


@app.post("/users/login")
def users_authenticate(email: str, password: str, response: Response):
    """Identifies user already registered"""
    new_user = User(email, password)
    response1 = new_user.authenticate()
    if 'error' in response1:
        response.status_code = 403

    return response1


@app.delete('/users/login', status_code=403)
def users_logout(response: Response, authorization: Optional[str] = Header(None)):
    output = verify_token(authorization)
    if 'error' in output:
        return output

    response.status_code = 200
    user = User(output['email'])
    return user.expire_token()


@app.get('/restricted_path', status_code=403)
def restricted_resource(response: Response, authorization: Optional[str] = Header(None)):
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

    return user.check_token(token)
