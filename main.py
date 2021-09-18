from module import Sheet, auth
from db import get_requests, add_message, made_note, \
    note_by_time, note_by_date
from time import sleep
from datetime import datetime, time, timedelta
from threading import Thread

announce_times = {}

an_times = {(4, 45): "8:45 - 10:45", (8, 00): "12:00 - 14:00",
            (14, 00): "16:00 - 18:00", (16, 00): "20:00 - 22:00", (17, 00): ""}

service = auth()
sheet = Sheet(service)


def main():
    while True:
        sheet.update_timetable()
        requests = get_requests()
        for req in requests:
            places = sheet.find_places(req[1], req[2], req[3])
            #Проверка на то, что я его уже сегодня записал
            users = note_by_date(date_now())
            if req[0] in users:
                continue
                
            if places:
                if not sheet.write(req[4], places[-1]["cell"]):
                    add_message(req[0], f"Записал тебя на стрику\n"
                                        f"{req[1]}\n{req[2]}\nМашинка: {places[-1]['machine']}")
                    made_note(req[0], places[-1], req[4])

        sleep(60)


def update_announce():
    global announce_times

    flag = False
    for x, y in announce_times.items():
        if not y:
            flag = True

    if not flag:
        datenow = datetime.today()
        day, month, year = datenow.day, datenow.month, datenow.year
        hours, minute = datenow.hour, datenow.minute

        announce_times = {
            datetime(year, month, day, an_time[0], an_time[1]): (an_time[0] * 60 + an_time[0]) < (hours * 60 + minute)
            for an_time in an_times}


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
            if minutes <= 100 and not status:
                if not an_times[(announce.hour, announce.minute)]:
                    if list(announce_times.values())[0] == False:
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
                        add_message(user, "Менее чем через час у тебя стирка!")
                announce_times[announce] = True
                update_announce()
        sleep(60 * 5)


def date_now():
    now = datetime.now()
    now_day, now_month, now_year = map(str, [now.day, now.month, now.year])
    now_day = '0' * (2 - len(now_day)) + now_day
    now_month = '0' * (2 - len(now_month)) + now_month
    return f"{now_day}.{now_month}.{now_year}"


if __name__ == '__main__':
    update_announce()
    Thread(target=check_announce).start()
    main()
