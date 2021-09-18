import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime
from time import sleep

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
    def __init__(self, service):
        self.service = service
        self.sheet_id = "10B0FULRjxQ-ThMvcDaCJv3VNVL6EmpH6gZyKqzYNir0"
        self.timetable = None

    @staticmethod
    def _valid_date(date):
        d1 = datetime.strptime(date, "%d.%m.%Y")
        d2 = datetime.today()
        if (d1 - d2).days < 0:
            return False
        return True

    def update_timetable(self):
        self.timetable = self.get_values("Текущая запись!A3:I100")
        api_logger.info(f"Updated timetable!")

    def get_metadata(self):
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
        return sheet_metadata

    def get_values(self, range_):
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.sheet_id,
                                    range=range_,
                                    ).execute()
        return result.get('values', "")

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
            self.timetable = self.get_values("Текущая запись!A3:I100")
            return 0

        except Exception as e:
            api_logger.error(e)
            return -1

    def find_places(self, day, time, machine):
        if not self.timetable:
            self.timetable = self.get_values("Текущая запись!A3:I100")

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

            if row[1] in days:
                cur_day = row[1]
                cur_date = row[0]
            if cur_day == day and time == row[2]:
                try:
                    if len(row) <= machines[machine] or not row[machines[machine]]:
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
