from Sheets.Sheet.sheet import Sheet
from Sheets.Sheet.utils import getSheet
from Sheets.MainSheet.mainSheet import getMainSheet, MainSheet

from configs import sheet_id

from DataBase.models import Session, Request, Note, AntiSpam, User
from TelegramBot.telegram_bot import TgBot
from TelegramBot.status import STATUS

from time import sleep, perf_counter
from random import randrange, shuffle

from datetime import datetime, date, timedelta
from os import path

import logging


class SheetParser:
    __times1Machine = ["10:45 - 12:45", "15:00 - 17:00", "19:00 - 21:00", "22:45 - 0:30"]
    __times23Machine = ["8:45 - 10:45", "13:00 - 15:00", "17:00 - 19:00", "21:00 - 22:45"]
    __days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

    def __init__(self, db: Session, tgBot: TgBot):
        self.db = db
        self.tgBot = tgBot

        self.sheet = None
        self.mainSheet = None

        if path.exists("tokens/EluciferE.json"):
            self.sheet = getSheet("EluciferE", sheet_id)

        if path.exists("tokens/mainToken.json"):
            self.mainSheet: MainSheet = getMainSheet(tgBot, sheet_id)

        # Logs
        FORMAT = '[%(asctime)s] - [%(levelname)s] - %(message)s'
        logging.basicConfig(level=logging.INFO)
        sheetParser = logging.FileHandler('logs/sheetParser.log')
        sheetParser.setFormatter(logging.Formatter(FORMAT))

        self.parserLog = logging.getLogger('sheepParser')
        self.parserLog.addHandler(sheetParser)
        self.parserLog.propagate = False

    def run(self):
        while True:
            try:
                if not self.mainSheet or not self.sheet:
                    if path.exists("tokens/mainToken.json"):
                        self.mainSheet = getMainSheet(self.tgBot, sheet_id)
                    if path.exists("tokens/EluciferE.json"):
                        self.sheet = getSheet("EluciferE", sheet_id)
                    continue

                table = self.sheet.getTable()

                if not table:
                    continue

                table = self.__parseTable(table)
                self.checkNotes(table)

                lastDate = self.__analyzeTable(table)

                if lastDate:
                    self.__announceUsers(lastDate)
                    continue

                requests = self.db.query(Request).all()
                shuffle(requests)

                for request in requests:

                    if not path.exists(f'tokens/{request.username}.json'):
                        continue

                    time_ = request.time
                    machine = str(request.machine)

                    userNotes = self.db.query(Note).filter_by(username=request.username).all()
                    userWeeks = [self.__weekNumber(note.date) for note in userNotes]

                    for day, date in table.items():

                        if request.day.casefold() != day.casefold():
                            continue

                        for dateString, machines in date.items():

                            if machine not in machines or time_ not in machines[machine]:
                                continue

                            if machines[machine][time_]['value'].strip():
                                continue

                            weekNumber = self.__weekNumber(dateString)
                            if weekNumber in userWeeks:
                                continue

                            newSheet = getSheet(request.username, self.sheet.sheet_id)

                            cell = machine[machine][time_]['cell']

                            isChanged = self.mainSheet.changeBorder(cell)
                            sleep(2)
                            if isChanged == 0:
                                self.mainSheet.changeBackground(cell)
                            sleep(randrange(5, 8))
                            ans = newSheet.write(request.value, cell)

                            isDefault = self.mainSheet.makeDefault(cell)

                            n = 0
                            while isDefault == -1 and n < 10:
                                n += 1
                                isDefault = self.mainSheet.makeDefault(cell)

                            if ans:
                                msg = f"Привет! Записала тебя на стирку ^^\n\n{dateString}\n" + \
                                      f"{day.capitalize()}\n{time_}\nМашинка: {machine}"
                                self.tgBot.send_to_user(request.username, msg)
                                self.db.add(Note(request.username, dateStringe, day, time_,
                                                 machine, request.value, cell))
                                self.db.commit()
                                userWeeks.append(weekNumber)

                sleep(30)

            except Exception as e:
                self.parserLog.error(e)
                sleep(30)
                continue

    def __announceUsers(self, lastDate):
        users = self.db.query(User).all()
        lastDate = f"{lastDate[2]}.{lastDate[1]}.{lastDate[0]}"
        for user in users:
            if user.status in [STATUS.ASK_ALLOW, STATUS.ASK_ALLOW, STATUS.BANNED]:
                continue
            msg = "Запись открыта: https://clck.ru/anGXc"
            self.tgBot.bot.send_message(user.chat_id, msg)

            antiSpam = self.db.query(AntiSpam).filter_by(username=user.username).first()
            if not antiSpam:
                self.db.add(AntiSpam(user.username, lastDate))
            else:
                antiSpam.date = lastDate

        self.db.commit()
        sleep(300)

    @staticmethod
    def __weekNumber(date_):
        d, m, y = map(int, date_.split('.'))
        w = date(y, m, d).isocalendar()[1]
        return w

    def __analyzeTable(self, table: dict):

        dates = []
        for i, date in table.items():
            nowDates = list(date.keys())

            for newDate in nowDates:
                newDate = newDate.split(".")

                day, month, year = int(newDate[0]), int(newDate[1]), int(newDate[2])
                dates.append([year, month, day])

        dates.sort(reverse=True)
        nowLastDate = dates[0]

        antiSpam = self.db.query(AntiSpam).first()
        if antiSpam:
            wasLastDate = antiSpam.date.split(".")
            day, month, year = int(wasLastDate[0]), int(wasLastDate[1]), int(wasLastDate[2])
        else:
            return nowLastDate

        if nowLastDate == [year, month, day]:
            return None

        return nowLastDate

    def __parseTable(self, table: list) -> dict:
        timetable = {}

        if not table:
            return timetable

        date = None
        day = None

        for numLine, line in enumerate(table):

            if len(line) == 0:
                continue

            if line[0] and line[0].count(".") == 2:
                date = line[0]

            if len(line) == 1:
                continue

            if line[1] and line[1].lower() in self.__days and date:
                day = line[1]
                if day not in timetable:
                    timetable[day] = {date: {"1": {}, "2": {}, "3": {}}}
                else:
                    timetable[day][date] = {"1": {}, "2": {}, "3": {}}

            if len(line) < 9:
                continue

            if date and day and line[2] in self.__times1Machine and \
                    line[5] in self.__times23Machine and line[8] in self.__times23Machine:
                time1 = line[2]
                time2 = line[5]
                time3 = line[8]
                timetable[day][date]["1"][time1] = {}
                timetable[day][date]["2"][time2] = {}
                timetable[day][date]["3"][time3] = {}
            else:
                continue

            m1 = line[3] if len(line) > 3 else ""
            m2 = line[6] if len(line) > 6 else ""
            m3 = line[9] if len(line) > 9 else ""

            if date and day and time1 and time2 and time3:
                timetable[day][date]["1"][time1] = {'value': m1, 'cell': f'D{numLine + 3}'}
                timetable[day][date]["2"][time2] = {'value': m2, 'cell': f'G{numLine + 3}'}
                timetable[day][date]["3"][time3] = {'value': m3, 'cell': f'J{numLine + 3}'}

        return timetable

    @staticmethod
    def validDate(date) -> bool:
        d1 = datetime.strptime(date, "%d.%m.%Y")
        d2 = datetime.today()
        if (d1 - d2).days < 0:
            return False
        return True

    @staticmethod
    def __weekNumber(date_):
        d, m, y = map(int, date_.split('.'))
        w = date(y, m, d).isocalendar()[1]
        return w

    @staticmethod
    def __dateNow():
        now = datetime.now()
        now_day, now_month, now_year = map(str, [now.day, now.month, now.year])
        now_day = now_day.zfill(2)
        now_month = now_month.zfill(2)
        return f"{now_day}.{now_month}.{now_year}"

    def checkNotes(self, table):
        requests = self.db.query(Request).all()
        for weekDay, info in table.items():
            for date, info2 in info.items():
                for machine, info3 in info2.items():
                    for time, info4 in info3.items():
                        value, cell = info4["value"], info4["cell"]
                        for req in requests:
                            if value != req.value:
                                continue

                            if datetime.strptime(date, "%d.%m.%Y") + timedelta(days=1) < datetime.now():
                                continue

                            notesThisDay = self.db.query(Note).filter_by(username=req.username,
                                                                         date=date).first()
                            if notesThisDay:
                                continue

                            newNote = Note(req.username, date, weekDay, time,
                                           machine, value, cell)
                            self.db.add(newNote)
                            self.db.commit()
                            ans = f"\n{date}\n{weekDay.capitalize()}\n" + \
                                  f"{time}\nМашинка: {machine}"
                            self.tgBot.send_to_user(req.username, f"Нашла твою запись в таблице!\n" + ans)
