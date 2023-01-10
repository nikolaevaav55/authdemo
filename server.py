import base64
import hmac
import hashlib
import json
from typing import Optional

from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response

app = FastAPI()

SECRET_KEY = "f3bdda87f0b2151d39f0c1058ab4f50dfef12f9471d7acbc1568b36d21cb72d9"
PASSWORD_SALT = "4dc22feeab0b33685b96967d9da4d55ba6dd83d3992138d7790cda2f5f53a7c7"


def sign_data(data: str) -> str:
    """Возвращает подписанные данные data"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split(".")
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username

def verify_password(username: str, password: str) -> bool:
    password_hash = hashlib.sha256((password + PASSWORD_SALT).encode())\
        .hexdigest().lower()
    stored_password_hash = users[username]["password"].lower()
    return  password_hash == stored_password_hash

users = {
    "alexey@user.com": {
        "name":"Алексей",
        "password": "a50afeb5fc1c1a8850fb580d05d80cb654cbec5bb28e8262dedc35e7080c39ad",
        "balance": 100_000
    },
    "petr@user.com": {
        "name":"Петр",
        "password": "some_password_2",
        "balance": 300_000
    },
        "alexey_2@user.com": {
        "name":"Алексей",
        "password": "some_password_3",
        "balance": 500_00
    }
}



@app.get("/")
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()
    if not username:
        return Response(login_page, media_type="text/html")
    try:
        valid_username = get_username_from_signed_string(username)
        if not valid_username:
            response = Response(login_page, media_type="text/html")
            response.delete_cookie(key="username")
            return response
        return Response(f"Привет, {users[valid_username]['name']}!", media_type="text/html")
    except (KeyError, UnicodeDecodeError):
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response


@app.post("/login")
def process_login_page(username : str = Form(...), password : str = Form(...)):
    user = users.get(username)
    print('user is', user, 'pasword is', password)
    if not user or not verify_password(username, password):
        return Response(
            json.dumps({
                "success": False,
                "message": "Я вас не знаю!" 
                }),
                media_type='application/json')
    response = Response(            
        json.dumps({
            "success": True,
            "message": f"Привет: {user['name']}! <br /> Баланс: {user['balance']}"
            }),
            media_type='application/json')

    username_signed = base64.b64encode(username.encode()).decode() + "." + \
        sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response