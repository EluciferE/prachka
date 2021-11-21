from module import Sheet, auth
from db import DataBase
from telegram_bot import TgBot
from announce import Announce
from config import token, sheet_id

from time import sleep
from datetime import datetime, time, timedelta, date
from threading import Thread
from utils import pasted_date, number_of_week, date_now

announces = []
an_times = {(4, 35): "8:45 - 10:45", (7, 50): "12:00 - 14:00",
            (11, 50): "16:00 - 18:00", (15, 50): "20:00 - 22:00", (16, 00): ""}


def main():
    service = auth()
    sheet = Sheet(service, sheet_id)

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
        # Когда стирка закончилась
        new_time[0] += 2
        announces.append(Announce(db, tg_bot, "Стирка закончилась!", new_time, target_time))

    update_announce(db)
    print(*announces, sep="\n")
    Thread(target=check_announce, args=(db,)).start()


def update_announce(db):
    notes = db.all_notes()
    for note in notes:
        if pasted_date(note[1]):
            db.delete_note_by_day(note[0], note[1])


def check_announce(db):
    global announces
    while True:
        for announce in announces:
            announce.try_announce()

        sleep(10)


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
    sleep(180 * 60)


def check_updates(db, sheet, tg_bot):
    while True:
        sheet.update_timetable()
        requests = db.get_requests()
        would_write = []
        used_places = []

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

                if place["cell"] in used_places:
                    continue

                used_places.append(place["cell"])
                would_write.append({"value": req[4], "cell": place["cell"],
                                    "username": req[0], "day": req[1].capitalize(),
                                    "time": req[2], 'place': place})

                user_weeks.append(number_of_week(place['date']))

        if would_write:
            all_values = [x["value"] for x in would_write]
            all_ranges = [x["cell"] for x in would_write]

            ans = sheet.write(all_values, all_ranges)
            while ans != 0:
                ans = sheet.write(all_values, all_ranges)

            for record in would_write:
                msg = f"Привет! Записала тебя на стирку ^^\n\n{record['day']}\n{record['time']}\n" + \
                      f"Машинка: {record['place']['machine']}"
                tg_bot.send_to_user(record['username'], msg)
                db.make_note(record['username'], record['place'], record['value'])

        sleep(10)


if __name__ == '__main__':
    main()
