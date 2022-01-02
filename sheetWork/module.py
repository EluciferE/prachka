import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime
from time import sleep

import gc

from threading import Thread
import logging

from typing import Union

from configs.config import host

# Work with stdout
from io import StringIO
import sys
import queue

# LOGGING
FORMAT = '[%(asctime)s] - [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO)
api_logs = logging.FileHandler('logs/api.log')
api_logs.setFormatter(logging.Formatter(FORMAT))

api_logger = logging.getLogger('api')
api_logger.addHandler(api_logs)
api_logger.propagate = False

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

times = ["8:45 - 10:45", "12:00 - 14:00", "16:00 - 18:00", "20:00 - 22:00"]
days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
machines = {"1": 3, "2": 5, "3": 7}
letters = {"1": "D", "2": "F", "3": "H"}


class Sheet:
    def __init__(self, service, sheet_id):
        self.service = service
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
            if tmp:
                self.timetable = tmp
            gc.collect()
        except Exception as e:
            api_logger.error(e)

    def get_metadata(self):
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
        gc.collect()
        return sheet_metadata

    def get_values(self, range_):
        try:
            if "Текущая запись!" not in range_:
                range_ = "Текущая запись!" + range_
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.sheet_id,
                                        range=range_,
                                        ).execute()
            return result.get('values', "")
        except Exception as e:
            api_logger.error(e)
        finally:
            gc.collect()

    def write(self, values: Union[list, str], ranges: Union[list, str]):
        if type(values) != list:
            values = [values]
            ranges = [ranges]

        for i, range_ in enumerate(ranges):
            if "Текущая запись!" not in range_:
                ranges[i] = "Текущая запись!" + range_

        batch_update_values_request_body = {
            'value_input_option': "RAW",
            'data': [{"range": ranges[i], "values": [[values[i]]]} for i in range(len(values))]
        }
        try:
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.sheet_id, body=batch_update_values_request_body).execute()
            for i in range(len(values)):
                api_logger.info(f"[WRITE] {ranges[i]} -> {values[i]}")
            self.timetable = self.get_values("Текущая запись!A3:I80")
            gc.collect()
            return 0

        except Exception as e:
            api_logger.error(e)
            gc.collect()
            return -1

    def find_places(self, day, time, machine):
        try:
            if not self.timetable:
                self.timetable = self.get_values("Текущая запись!A3:I80")

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
    print(f"Call create_config: {username}")
    flow = InstalledAppFlow.from_client_secrets_file(
        f'configs/credentials.json', SCOPES)

    que = queue.Queue()
    server = Thread(target=lambda q: q.put(flow.run_local_server(host=host, open_browser=False)), args=(que,))

    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    server.start()

    sleep(3)
    sys.stdout = old_stdout
    tg_bot.send_to_user(username, f"{mystdout.getvalue()}")
    while True:
        if not que.empty():
            creds = que.get()
            break
        sleep(1)

    with open(f'tokens/{username}.json', 'w') as token:
        token.write(creds.to_json())

    return creds


def auth(username, tg_bot):
    creds = None
    if os.path.exists(f'tokens/{username}.json'):
        creds = Credentials.from_authorized_user_file(f'tokens/{username}.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

            with open(f'tokens/{username}.json', 'w') as token:
                token.write(creds.to_json())
        elif tg_bot is not None:
            try:
                creds = create_config(username, tg_bot)
            except Exception as e:
                tg_bot.send_to_user(username, "Something goes wrong")
                tg_bot.send_to_admin(e)
        else:
            return -1

    service = build('sheets', 'v4', credentials=creds)

    return service


def get_sheet(username: str, sheet_id: str, tg_bot=None) -> Sheet:
    service = auth(username, tg_bot)
    if service != -1:
        return Sheet(service, sheet_id)
    return -1
