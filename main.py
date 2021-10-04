from module import Sheet, auth
from db import get_requests, add_message, make_note, \
    note_by_time, note_by_date, get_notes, all_notes, delete_note
from time import sleep
from datetime import datetime, time, timedelta, date
from threading import Thread

announce_times = {}

an_times = {(4, 45): "8:45 - 10:45", (8, 00): "12:00 - 14:00",
            (12, 00): "16:00 - 18:00", (16, 00): "20:00 - 22:00", (17, 00): ""}

service = auth()
sheet = Sheet(service)


def main():
    while True:
        sheet.update_timetable()
        requests = get_requests()
        for req in requests:
            places = sheet.find_places(req[1], req[2], req[3])
            # Проверим, записан ли он на этой неделе
            user_weeks = []
            notes = get_notes(req[0])
            for note in notes:
                user_weeks.append(number_of_week(note[1]))
            for place in places:
                target_week = number_of_week(place['date'])

                if target_week in user_weeks:
                    continue

                if not sheet.write(req[4], places[-1]["cell"]):
                    add_message(req[0], f"Привет! Записала тебя на стирку ^^\n"
                                        f"{req[1]}\n{req[2]}\nМашинка: {place['machine']}")
                    make_note(req[0], place, req[4])
                    user_weeks.append(number_of_week(place['date']))

        sleep(30)


def update_announce():
    global announce_times

    if len(announce_times) == 0:
        datenow = datetime.today()
        day, month, year = datenow.day, datenow.month, datenow.year
        hours, minute = datenow.hour, datenow.minute

        announce_times = {
            datetime(year, month, day, an_time[0], an_time[1]): (an_time[0] * 60 + an_time[0]) < (hours * 60 + minute)
            for an_time in an_times}

    if not (False in announce_times.values()):
        datenow = datetime.today()
        next_date = datenow + timedelta(days=1)
        day, month, year = next_date.day, next_date.month, next_date.year
        announce_times = {
            datetime(year, month, day, an_time[0], an_time[1]): False
            for an_time in an_times}

    notes = all_notes()
    for note in notes:
        if pasted_date(note[1]):
            delete_note(note[0], note[1])


def check_announce():
    global announce_times

    while True:
        now = datetime.now()
        now_day, now_month, now_year = map(str, [now.day, now.month, now.year])
        now_day = '0' * (2 - len(now_day)) + now_day
        now_month = '0' * (2 - len(now_month)) + now_month

        next_date = now + timedelta(days=1)
        next_day, next_month, next_year = map(str, [next_date.day, next_date.month, next_date.year])
        next_day = '0' * (2 - len(next_day)) + next_day
        next_month = '0' * (2 - len(next_month)) + next_month
        for announce, status in announce_times.items():
            minutes = (announce - now).total_seconds() // 60
            if minutes <= 15 and not status:
                if not an_times[(announce.hour, announce.minute)]:
                    if not list(announce_times.values())[0]:
                        continue
                    users = note_by_date(f"{next_day}.{next_month}.{next_year}")
                    for user in users:
                        user = str(user[0])
                        add_message(user, "У тебя завтра стирка!")
                else:
                    users = note_by_time(f"{now_day}.{now_month}.{now_year}",
                                         an_times[(announce.hour, announce.minute)])
                    for user in users:
                        user = str(user[0])
                        add_message(user, "Через несколько минут стирка!")
                announce_times[announce] = True
                update_announce()
        sleep(5 * 60)


def date_now():
    now = datetime.now()
    now_day, now_month, now_year = map(str, [now.day, now.month, now.year])
    now_day = '0' * (2 - len(now_day)) + now_day
    now_month = '0' * (2 - len(now_month)) + now_month
    return f"{now_day}.{now_month}.{now_year}"


def pasted_date(date_):
    now = datetime.today()
    now = now + timedelta(hours=4)
    now = datetime(now.year, now.month, now.day)
    date_ = datetime.strptime(date_, "%d.%m.%Y") + timedelta(days=7)
    return now > date_


def number_of_week(date_):
    d, m, y = map(int, date_.split('.'))
    w = date(y, m, d).isocalendar()[1]
    return w


if __name__ == '__main__':
    update_announce()
    Thread(target=check_announce).start()
    main()
