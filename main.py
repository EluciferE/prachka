from module import Sheet, auth
from db import DataBase
from telegram_bot import TgBot
from announce import Announce
from config import token

from time import sleep
from datetime import datetime, time, timedelta, date
from threading import Thread
from utils import pasted_date, number_of_week, date_now

announces = []
an_times = {(4, 35): "8:45 - 10:45", (7, 50): "12:00 - 14:00",
            (11, 50): "16:00 - 18:00", (15, 50): "20:00 - 22:00", (16, 00): ""}


def main():
    service = auth()
    sheet = Sheet(service)

    db = DataBase()
    tg_bot = TgBot(token, sheet, db)
    Thread(target=tg_bot.start_bot).start()
    Thread(target=check_collisions, args=(db, sheet, tg_bot,)).start()
    Thread(target=check_updates, args=(db, sheet, tg_bot,)).start()

    for an_time, target_time in an_times.items():
        if not target_time:
            announces.append(Announce(db, tg_bot, "У тебя завтра стирка!", an_time, target_time))
            continue
        announces.append(Announce(db, tg_bot, "Через несколько минут стирка!", an_time, target_time))

        new_time = [an_time[0], an_time[1]]
        new_time[0] += 2
        announces.append(Announce(db, tg_bot, "Стирка закончилась!", new_time, target_time))

    update_announce(db)
    Thread(target=check_announce, args=(db,)).start()


def update_announce(db):
    not_done = [x for x in announces if not x.done]
    if not not_done:
        for announce in announces:
            announce.update_time()

    notes = db.all_notes()
    for note in notes:
        if pasted_date(note[1]):
            db.delete_note_by_day(note[0], note[1])


def check_announce(db):
    while True:
        for announce in announces:
            if announce.try_announce():
                update_announce(db)
        sleep(2 * 60)


def check_collisions(db, sheet, tg_bot):
    notes = db.all_notes()
    for note in notes:
        cell = note[6]
        info = sheet.get_values(f"{cell}:{cell}")
        if info:
            info = info[0][0]
        if not info or info != note[5]:
            ans = f"Кто-то занял ячейку\n{note}\nТам сейчас: {info}"
            tg_bot.send_to_admin(ans)
    sleep(720 * 60)


def check_updates(db, sheet, tg_bot):
    while True:
        sheet.update_timetable()
        requests = db.get_requests()

        for req in requests:
            places = sheet.find_places(req[1], req[2], req[3])
            # Проверим, записан ли он на этой неделе
            user_weeks = []
            notes = db.get_notes(req[0])
            for note in notes:
                user_weeks.append(number_of_week(note[1]))
            for place in places:
                target_week = number_of_week(place['date'])

                if target_week in user_weeks:
                    continue

                if not sheet.write(req[4], place["cell"]):
                    msg = f"Привет! Записала тебя на стирку ^^\n\n{req[1].capitalize()}\n{req[2]}\n" + \
                          f"Машинка: {place['machine']}"
                    tg_bot.send_to_user(req[0], msg)
                    db.make_note(req[0], place, req[4])
                    user_weeks.append(number_of_week(place['date']))

        sleep(30)


if __name__ == '__main__':
    main()
