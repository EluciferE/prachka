from DataBase.models import Note, Session

from datetime import datetime, timedelta
import logging

from time import sleep


class AnnounceManager:

    def __init__(self, tgBot, db: Session):
        self.bot = tgBot
        self.db = db

        # Logs
        FORMAT = '[%(asctime)s] - [%(levelname)s] - %(message)s'
        logging.basicConfig(level=logging.INFO)
        announceManagerLog = logging.FileHandler('logs/announces.log')
        announceManagerLog.setFormatter(logging.Formatter(FORMAT))

        self.logs = logging.getLogger('announce')
        self.logs.addHandler(announceManagerLog)
        self.logs.propagate = False

    def run(self):
        while True:
            try:
                notes = self.db.query(Note).all()

                self.announce10Min(notes)
                self.announceNextDay(notes)
                self.announceEnd(notes)

                sleep(10)

            except Exception as e:
                print(e)
                self.logs.error(f"SomeTrouble: {e}")
                sleep(10)

    def announce10Min(self, notes):
        for note in notes:

            if note.announceStart:
                continue

            time_ = note.time.split(" - ")[0]
            noteDate = datetime.strptime(f"{note.date} {time_}", "%d.%m.%Y %H:%M")
            now = datetime.utcnow() + timedelta(hours=7)

            if now + timedelta(minutes=10) > noteDate:
                self.bot.send_to_user(note.username, "У тебя скоро стирка!")
                note.announceStart = True
                self.db.commit()
                self.logs.info(f"Announced: {note.username}")

    def announceNextDay(self, notes):

        if (datetime.utcnow() + timedelta(hours=7)).hour > 19:
            for note in notes:

                if note.announceNextDay:
                    continue

                noteDate = datetime.strptime(f"{note.date}", "%d.%m.%Y")
                nowDay = datetime.utcnow() + timedelta(hours=7)
                nextDay = datetime.utcnow() + timedelta(hours=7 + 4, days=1)

                if nowDay < noteDate < nextDay:
                    self.bot.send_to_user(note.username, "У тебя завтра стирка!")
                    self.logs.info(f"Announced: {note.username}")
                    note.announceNextDay = True
                    self.db.commit()

    def announceEnd(self, notes):
        for note in notes:

            if note.announceEnd:
                continue

            time_ = note.time.split(" - ")[1]
            noteDate = datetime.strptime(f"{note.date} {time_}", "%d.%m.%Y %H:%M")
            if datetime.strptime(time_, "%H:%M") < datetime.strptime("5:00", "%H:%M"):
                noteDate += timedelta(days=1)

            now = datetime.utcnow() + timedelta(hours=7)

            if now + timedelta(minutes=15) > noteDate:
                self.bot.send_to_user(note.username, "У тебя закончилась стирка!")
                note.announceEnd = True
                self.db.commit()
                self.logs.info(f"Announced: {note.username}")