from fastapi import FastAPI, Response

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
