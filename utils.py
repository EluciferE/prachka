from datetime import date, datetime, timedelta
from time import time


def get_time(func):
    def wrapper(*args, **kwargs):
        a = time()
        result = func(*args, **kwargs)
        b = time()
        print(f"Func: {func.__name__}()\t Time: {b - a}")
        return result

    return wrapper


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

def valid_date(date) -> bool:
    d1 = datetime.strptime(date, "%d.%m.%Y")
    d2 = datetime.today()
    if (d1 - d2).days < 0:
        return False
    return True