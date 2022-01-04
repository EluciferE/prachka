import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime
from time import sleep

import requests
import json
from sheetWork.token import Token

import gc

from threading import Thread
import logging

from typing import Union

from telegramBot.status import STATUS
from telegramBot.templates import *

# LOGGING
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

FORMAT = '[%(asctime)s] - [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO)
api_logs = logging.FileHandler('logs/api.log')
api_logs.setFormatter(logging.Formatter(FORMAT))

api_logger = logging.getLogger('api')
api_logger.addHandler(api_logs)
api_logger.propagate = False

times = ["8:45 - 10:45", "12:00 - 14:00", "16:00 - 18:00", "20:00 - 22:00"]
days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
machines = {"1": 3, "2": 5, "3": 7}
letters = {"1": "D", "2": "F", "3": "H"}


def _params_to_get(url: str, params: dict):
    url += "?"
    for key, value in params.items():
        url += f"{key}={value}&"
    return url


class Sheet:
    def __init__(self, token, sheet_id):
        self.token = token
        self.sheet_id = sheet_id
        self.timetable = None

    @staticmethod
    def _valid_date(date):
        d1 = datetime.strptime(date, "%d.%m.%Y")
        d2 = datetime.today()
        if (d1 - d2).days < 0:
            return False
        return True

    def update_timetable(self):
        try:
            tmp = self.get_values("Текущая запись!A3:I80")
            if tmp is not None:
                self.timetable = tmp
            gc.collect()
        except Exception as e:
            api_logger.error(e)

    def get_values(self, range_):
        try:
            if "Текущая запись!" not in range_:
                range_ = "Текущая запись!" + range_
            url = f'https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/{range_}'

            if not self.token.validate_token():
                self.token.refresh_token()

            url = _params_to_get(url, {"access_token": self.token.access_token()})

            r = requests.get(url)
            if r.json().get("values"):
                return r.json().get("values")

            api_logger.error(r.text)
            return None

        except Exception as e:
            api_logger.error(e)
        finally:
            gc.collect()

    def write(self, value: str, range_: str):
        if "Текущая запись!" not in range_:
            range_ = "Текущая запись!" + range_

        try:
            if not self.token.validate_token():
                self.token.refresh_token()

            url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/{range_}?access_token={self.token.access_token()}&valueInputOption=RAW"
            params = {"majorDimension": "ROWS",
                      "range": range_,
                      "values": [[value]]}
            r = requests.put(url, json=params)
            if "error" in r.json():
                raise ValueError(r.text)

            api_logger.info(f"[WRITE] {value} -> {range_}")
            self.timetable = self.get_values("Текущая запись!A3:I80")
            gc.collect()
            return 0

        except Exception as e:
            api_logger.error(e)
            gc.collect()
            print(e)
            return -1

    def find_places(self, day, time, machine):
        try:
            if self.timetable is None:
                self.timetable = self.get_values("Текущая запись!A3:I80")
                if self.timetable is None:
                    api_logger.error(f"Can't analyze timetable (None type)")
                    return []

            day = day.lower()

            if type(machine) == int:
                machine = str(machine)

            if day not in days:
                raise ValueError(f"Wrong day\n\tGot: {day}\n\tExpected: {days}")
            if time not in times:
                raise ValueError(f"Wrong time\n\tGot: {time}\n\tExpected: {times}")
            if machine not in ["1", "2", "3"]:
                raise ValueError(f"Wrong machine\n\tGot: {machine}\n\tExpected: 1, 2, 3")

            good_places = []

            cur_day = None
            cur_date = None

            line = 2

            for row in self.timetable:
                line += 1
                if not row:
                    continue

                if len(row) > 1 and row[1] in days:
                    cur_day = row[1]
                    cur_date = row[0]
                if cur_day == day and len(row) > 2 and time == row[2]:
                    try:
                        if len(row) <= machines[machine] or not row[machines[machine]].strip():
                            cell = f"{letters[machine]}{line}"
                            place = {"date": cur_date, "day": cur_day,
                                     "time": time, "machine": machine, "cell": cell}
                            if self._valid_date(cur_date):
                                good_places.append(place)
                        else:
                            # ГОВНОКОД, ИДИ НАХУЙ
                            for machine_try in ["1", "2", "3"]:
                                if len(row) <= machines[machine_try] or not row[machines[machine_try]]:
                                    cell = f"{letters[machine_try]}{line}"
                                    place = {"date": cur_date, "day": cur_day,
                                             "time": time, "machine": machine_try, "cell": cell}
                                    if self._valid_date(cur_date):
                                        good_places.append(place)

                    except Exception as e:
                        api_logger.error(f"{e} - {row} - {machine} - {machines[machine]}")

            return good_places

        except Exception as e:
            api_logger.error(e)
            return []


def create_config(username, tg_bot):
    with open("configs/client_secret.json") as json_data:
        d = json.load(json_data)["installed"]
        json_data.close()

    params = {"client_id": d["client_id"],
              "scope": 'https://www.googleapis.com/auth/spreadsheets'}

    r = requests.post("https://oauth2.googleapis.com/device/code", data=params)
    ans = r.json()

    tg_bot.send_to_user(username, f"Follow this link: {ans['verification_url']}\n\nCode: {ans['user_code']}")

    creds = -1
    n = 0

    params = {"client_id": d["client_id"],
              "client_secret": d["client_secret"],
              "device_code": ans["device_code"],
              "grant_type": "urn:ietf:params:oauth:grant-type:device_code"}

    while n < 30 and creds == -1:
        sleep(5)
        r = requests.post("https://oauth2.googleapis.com/token", data=params)

        if r.json().get("error") is not None:
            error = r.json()["error"]
            if error == "access_denied":
                tg_bot.send_to_user(username, "Ты запретил использовать свой токен!")
            elif error == "slow_down":
                sleep(10)
            n += 1
        else:
            tg_bot.send_to_user(username, "Получила твой токен!", keyboard=stand_keyboard)
            tg_bot.db.change_status(username, STATUS.MAIN_MENU)
            creds = r.json()
            break

    if creds == -1:
        return - 1

    with open(f'tokens/{username}.json', 'w') as token:
        token.write(json.dumps(creds))

    return creds


def auth(username, tg_bot):
    creds = None
    if os.path.exists(f'tokens/{username}.json'):
        creds = Token(username, path_to_token=f'tokens/{username}.json')
        if not creds.validate_token():
            creds.refresh_token()
    if not creds:
        if tg_bot is not None:
            creds = Token(username, json_token=create_config(username, tg_bot))
        else:
            return -1

    return creds


def get_sheet(username: str, sheet_id: str, tg_bot=None) -> Sheet:
    service = auth(username, tg_bot)
    if service != -1:
        return Sheet(service, sheet_id)
    return -1
