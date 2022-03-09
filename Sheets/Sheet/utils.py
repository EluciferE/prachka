from datetime import datetime
from .sheet import Sheet
from .token import Token
from os.path import exists

from DataBase.models import User

import json
import requests
from time import sleep


def createToken(user: User, tg_bot, keyboard):
    with open("configs/client_secret.json") as json_data:
        client_data = json.load(json_data)["installed"]

    params = {"client_id": client_data["client_id"],
              "scope": 'https://www.googleapis.com/auth/spreadsheets'}

    r = requests.post("https://oauth2.googleapis.com/device/code", data=params)
    ans = r.json()

    tg_bot.send_message(user.chat_id, f"Follow this link: {ans['verification_url']}\n\nCode:", reply_markup=keyboard)
    tg_bot.send_message(user.chat_id, f"{ans['user_code']}", reply_markup=keyboard)

    params = {"client_id": client_data["client_id"],
              "client_secret": client_data["client_secret"],
              "device_code": ans["device_code"],
              "grant_type": "urn:ietf:params:oauth:grant-type:device_code"}

    for iteration in range(30):
        r = requests.post("https://oauth2.googleapis.com/token", data=params)

        if r.json().get("error"):
            sleep(5)
            continue

        creds = r.json()
        tg_bot.send_message(user.chat_id, "Получила твой токен!")
        with open(f'tokens/{user.username}.json', 'w') as token:
            token.write(json.dumps(creds))
        return creds

    return None


def getSheet(username, sheet_id) -> Sheet:
    if not exists(f'tokens/{username}.json'):
        raise ValueError("Token does not exist: " + username)

    token = Token(username, path_to_token=f'tokens/{username}.json')

    if not token.validate_token():
        token.refresh_token()

    return Sheet(token, sheet_id)
