from module import Sheet, auth
from db import get_requests, add_message, make_note, \
    note_by_time, note_by_date, get_notes, all_notes, delete_note
from time import sleep
from datetime import datetime, time, timedelta, date
from threading import Thread
from announce import Announce

announces = []
an_times = {(4, 45): "8:45 - 10:45", (8, 00): "12:00 - 14:00",
            (12, 00): "16:00 - 18:00", (16, 00): "20:00 - 22:00", (17, 00): ""}

for an_time, target_time in an_times.items():
    if not target_time:
        announces.append(Announce("У тебя завтра стирка!", an_time, target_time))
        continue
    announces.append(Announce("Через несколько минут стирка!", an_time, target_time))

    new_time = [an_time[0], an_time[1]]
    new_time[0] += 2
    announces.append(Announce("Стирка закончилась!", new_time, target_time))


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
    not_done = [x for x in announces if not x.done]
    if not not_done:
        for announce in announces:
            announce.update_time()

    notes = all_notes()
    for note in notes:
        if pasted_date(note[1]):
            delete_note(note[0], note[1])


def check_announce():
    while True:
        for announce in announces:
            if announce.try_announce():
                update_announce()
        print(*announces, sep="\n")
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
    # main()
