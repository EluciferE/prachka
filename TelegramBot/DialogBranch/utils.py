from datetime import datetime

from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def dateNow():
    now = datetime.now()
    now_day, now_month, now_year = map(str, [now.day, now.month, now.year])
    now_day = now_day.zfill(2)
    now_month = now_month.zfill(2)
    return f"{now_day}.{now_month}.{now_year}"


def createKeyboard(buttons, row):
    keyboard = ReplyKeyboardMarkup(row_width=row, resize_keyboard=True)
    new_buttons = [KeyboardButton(x) for x in buttons]
    for i in range(0, len(new_buttons), row):
        if row == 3 and i + 2 < len(new_buttons):
            keyboard.row(new_buttons[i], new_buttons[i + 1], new_buttons[i + 2])
        elif row == 3 and i + 1 < len(new_buttons):
            keyboard.row(new_buttons[i], new_buttons[i + 1])
        elif row == 2 and i + 1 < len(new_buttons):
            keyboard.row(new_buttons[i], new_buttons[i + 1])
        else:
            keyboard.row(new_buttons[i])
    return keyboard


def parseTmp(tmp):
    tmp = tmp.split('/')
    tmp = [x for x in tmp if x]
    ans = {}
    if len(tmp) > 0:
        ans["day"] = tmp[0]
    if len(tmp) > 1:
        ans["machine"] = tmp[1]
    if len(tmp) > 2:
        ans["time"] = tmp[2]
    if len(tmp) > 3:
        ans["note"] = '/'.join(tmp[3:])
    return ans
