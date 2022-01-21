from sheetWork.sheet import get_sheet, get_main_sheet
from sheetWork.main_sheet import MainSheet

from dataBase.db import DataBase
from telegramBot.telegram_bot import TgBot
from announces.announce import Announce
from configs.config import token, sheet_id

from time import sleep

from threading import Thread
from utils import pasted_date, number_of_week, date_now

from random import randrange
from os import path

an_times = {(4, 35): "8:45 - 10:45", (7, 50): "12:00 - 14:00",
            (11, 50): "16:00 - 18:00", (15, 50): "20:00 - 22:00", (16, 00): ""}


def main():
    db = DataBase()
    sheet = get_sheet("EluciferE", sheet_id)
    tg_bot = TgBot(token, db, sheet)

    Thread(target=tg_bot.start_bot).start()
    # TODO
    #Thread(target=check_collisions, args=(db, sheet, tg_bot,)).start()
    Thread(target=check_updates, args=(db, tg_bot,)).start()

    Thread(target=check_announce, args=(db, tg_bot,)).start()


def expired_notes(db):
    notes = db.all_notes()
    for note in notes:
        if pasted_date(note[1]):
            db.delete_note_by_day(note[0], note[1])


def check_announce(db, tg_bot):
    announces = []
    for an_time, target_time in an_times.items():
        if not target_time:
            announces.append(Announce(db, tg_bot, "У тебя завтра стирка!", an_time, target_time))
            continue
        announces.append(Announce(db, tg_bot, "Через несколько минут стирка!", an_time, target_time))

        new_time = [an_time[0], an_time[1]]
        # Когда стирка закончилась
        new_time[0] += 2
        announces.append(Announce(db, tg_bot, "Стирка закончилась!", new_time, target_time))

    n = 0
    while True:
        try:
            expired_notes(db)
            for announce in announces:
                announce.try_announce()
            if n % 3600 == 0:
                notes = db.all_notes()
                for note in notes:
                    if pasted_date(note[1]):
                        db.delete_note_by_day(note[0], note[1])
            n += 1

            sleep(10)
        except Exception as e:
            continue


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


def check_updates(db, tg_bot):
    sheet = get_sheet("EluciferE", sheet_id, tg_bot)
    main_sheet = get_main_sheet(sheet_id)

    n = 0
    while True:
        n += 1

        if n % 50 == 0:
            if not sheet.token.validate_token() and sheet.token.refresh_token() == -1:
                tg_bot.send_to_user("EluciferE", "У тебя закончился токен((")
                sheet = get_sheet("EluciferE", sheet_id, tg_bot)

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

                if not path.exists(f"tokens/{req[0]}.json"):
                    ans = db.is_announced(req[0])
                    if not ans or number_of_week(date_now()) != int(ans):
                        tg_bot.send_to_user(req[0], "Запись открыта! Ты не авторизован, поэтому не могут тебя записать(")
                        db.mark_as_announced(req[0], str(number_of_week(date_now())))
                    elif number_of_week(date_now()) != int(ans):
                        db.mark_as_announced(req[0], str(number_of_week(date_now())))
                    continue

                sleep(randrange(3, 5))
                new_sheet = get_sheet(req[0], sheet_id, tg_bot)
                main_sheet.change_color(place["cell"])
                sleep(randrange(3, 5))

                try:
                    ans = new_sheet.write(req[4], place["cell"])
                    main_sheet.change_color(place["cell"], True)
                except Exception as e:
                    print(f"Write exception[{req[0]}]: {e}")
                    continue

                if ans == -1:
                    tg_bot.send_to_user(req[0], "Я не смогла тебя записать(( Попробуй обновить токен")
                    tg_bot.send_to_admin(f"Траблы с записью {req[0]}")
                    continue

                msg = f"Привет! Записала тебя на стирку ^^\n\n{req[1].capitalize()}\n{req[2]}\n" + \
                      f"Машинка: {place['machine']}"
                tg_bot.send_to_user(req[0], msg)
                db.make_note(req[0], place, req[4])
                user_weeks.append(number_of_week(place['date']))

                sleep(10)

        sleep(180)


if __name__ == '__main__':
    main()
