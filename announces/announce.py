from datetime import datetime, timedelta
from TelegramBot.telegram_bot import TgBot

from DataBase import Session, Note


class Announce:
    def __init__(self, db: Session, tg_bot: TgBot, message, announce_time, target_time):
        self.db = db
        self.tg_bot = tg_bot
        self.message = message
        if len(announce_time) != 2:
            raise ValueError(f"Wrong announce time. Got: {announce_time}")
        self.target_time = target_time
        self.done = False
        self.announce_time = self.create_time(announce_time)

    def try_announce(self) -> bool:
        now = datetime.now()
        dateNow = self.dateToStr(now)

        if self.target_time:
            seconds = (self.announce_time - now).total_seconds()
            if seconds <= 0 and not self.done:
                notes = self.db.query(Note).filter()
                users = self.db.note_by_time(dateNow, self.target_time)
                for user in users:
                    user = str(user[0])
                    self.tg_bot.send_to_user(user, self.message)
                self.update_time()
        else:  # ANNOUNCE FOR THE NEXT DAY
            next_date = now + timedelta(days=1)
            next_day, next_month, next_year = map(str, [next_date.day, next_date.month, next_date.year])
            next_day = '0' * (2 - len(next_day)) + next_day
            next_month = '0' * (2 - len(next_month)) + next_month

            seconds = (self.announce_time - now).total_seconds()

            if seconds <= 0 and not self.done:
                users = self.db.note_by_date(f"{next_day}.{next_month}.{next_year}")
                for user in users:
                    user = str(user[0])
                    self.tg_bot.send_to_user(user, self.message)
                self.update_time()

        return self.done

    def update_time(self):
        next_date = self.announce_time + timedelta(days=1)
        self.announce_time = next_date
        self.done = False

    @staticmethod
    def dateToStr(date) -> str:
        day, month, year = map(str, [date.day, date.month, date.year])
        day = day.zfill(2)
        month = month.zfill(2)
        return  f"{year}.{day}.{month}"

    @staticmethod
    def create_time(announce_time: tuple) -> datetime:
        datenow = datetime.today()
        day, month, year = datenow.day, datenow.month, datenow.year
        hours, minute = datenow.hour, datenow.minute

        if (announce_time[0] * 60 + announce_time[0]) < (hours * 60 + minute):
            return datetime(year, month, day, announce_time[0], announce_time[1]) + timedelta(days=1)

        return datetime(year, month, day, announce_time[0], announce_time[1])

    def __repr__(self):
        target = self.target_time
        if not self.target_time:
            target = "anytime"
        return f"{self.__class__.__name__}(done: {self.done}, {self.message}, {self.announce_time}, {target})"
