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

    def write(self, value, range_):
        if "Текущая запись!" not in range_:
            range_ = "Текущая запись!" + range_
        values = [[value]]
        body = {'values': values}
        try:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id, range=range_,
                valueInputOption="RAW", body=body).execute()
            api_logger.info(f"[WRITE] {range_} -> {value}")
            self.timetable = self.get_values("Текущая запись!A3:I80")
            return 0

        except Exception as e:
            api_logger.error(e)
            return -1

        finally:
            gc.collect()

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


def auth():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    return service
