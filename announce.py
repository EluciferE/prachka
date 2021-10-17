from datetime import datetime, time, timedelta, date
from db import note_by_time, add_message, note_by_date


class Announce:
    def __init__(self, message, announce_time, target_time):
        self.message = message
        if len(announce_time) != 2:
            raise ValueError(f"Wrong announce time. Got: {announce_time}")
        self.announce_time = self.create_time(announce_time)
        self.target_time = target_time
        self.done = False

    def try_announce(self) -> bool:
        now = datetime.now()
        now_day, now_month, now_year = map(str, [now.day, now.month, now.year])
        now_day = '0' * (2 - len(now_day)) + now_day
        now_month = '0' * (2 - len(now_month)) + now_month

        if self.target_time:
            minutes = (self.announce_time - now).total_seconds() // 60
            if minutes <= 15 and not self.done:
                users = note_by_time(f"{now_day}.{now_month}.{now_year}", self.target_time)
                for user in users:
                    user = str(user[0])
                    add_message(user, self.message)
                self.done = True
        else:
            next_date = now + timedelta(days=1)
            next_day, next_month, next_year = map(str, [next_date.day, next_date.month, next_date.year])
            next_day = '0' * (2 - len(next_day)) + next_day
            next_month = '0' * (2 - len(next_month)) + next_month

            minutes = (self.announce_time - now).total_seconds() // 60

            if minutes <= 15 and not self.done:
                users = note_by_date(f"{next_day}.{next_month}.{next_year}")
                for user in users:
                    user = str(user[0])
                    add_message(user, self.message)
            self.done = True

        return self.done

    def update_time(self):
        next_date = self.announce_time + timedelta(days=1)
        self.announce_time = next_date

    def create_time(self, announce_time: tuple) -> datetime:
        datenow = datetime.today()
        day, month, year = datenow.day, datenow.month, datenow.year
        hours, minute = datenow.hour, datenow.minute

        if (announce_time[0] * 60 + announce_time[0]) < (hours * 60 + minute):
            self.done = True

        return datetime(year, month, day, announce_time[0], announce_time[1])

    def __repr__(self):
        target = self.target_time
        if not self.target_time:
            target = "anytime"
        return f"{self.__class__.__name__}({self.message}, {self.announce_time}, {target})"
