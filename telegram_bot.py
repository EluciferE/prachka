from config import token
import telebot
import logging
from db import *
from threading import Thread
from time import sleep
from main import sheet, date_now

import gc

bot = telebot.TeleBot(token)

banner = "Привет, это бот для прачечной 5 общаги НГУ\n" \
         "Он будет записывать тебя по нужному времени на стиральную машинку.\n" \
         "Ему от тебя нужно только расписание(день недели/время/машинка)\n" \
         "Если эта машинка будет занята, то он будет пытаться ставить на другие\n" \
         "Также он показывает твои записи и может их удалять с документа\n" \
         "(но не из списка охранницы T_T)\n" \
         "Возможно он будет напоминать тебе за день и за час до стирки\n" \
         "(но это ещё не точно)\n" \
         "Если что-то пойдет не так, то пишите @EluciferE"

TIMETABLE = "День недели: {}\nВремя: {}\nМашинка: {}\nЗапись: {}"
NOTE = "Дата: {}\nДень недели: {}\nВремя: {}\nМашинка: {}"

# LOGGING
FORMAT = '[%(asctime)s] - [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO)
tg_logs = logging.FileHandler('logs/bot.log')
tg_logs.setFormatter(logging.Formatter(FORMAT))

tg_logger = logging.getLogger('bot')
tg_logger.addHandler(tg_logs)
tg_logger.propagate = False

times = ["8:45 - 10:45", "12:00 - 14:00", "16:00 - 18:00", "20:00 - 22:00"]
days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

# BUTTONS/MENUS
first_menu = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
first_menu.row(telebot.types.KeyboardButton("Запросить доступ к боту"))

admin_but = [telebot.types.KeyboardButton(x) for x in ['Запросы на доступ', 'Пользователи',
                                                       'Основное меню']]
admin_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
admin_keyboard.row(admin_but[0], admin_but[1])
admin_keyboard.row(admin_but[2])

days_buttons = [telebot.types.KeyboardButton(x.capitalize()) for x in days]
days_menu = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
days_menu.row(days_buttons[0], days_buttons[1], days_buttons[2])
days_menu.row(days_buttons[3], days_buttons[4], days_buttons[5])
days_menu.row(days_buttons[6])

times_buttons = [telebot.types.KeyboardButton(x) for x in times]
times_menu = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
times_menu.row(times_buttons[0], times_buttons[1])
times_menu.row(times_buttons[2], times_buttons[3])

wedn_times_menu = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
wedn_times_menu.row(times_buttons[2], times_buttons[3])

machines_buttons = [telebot.types.KeyboardButton(x) for x in ["1", "2", "3"]]
machines_menu = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
machines_menu.row(machines_buttons[0], machines_buttons[1], machines_buttons[2])

standard_buttons = [telebot.types.KeyboardButton(x) for x in ["Текущее расписание", "Мои записи",
                                                              "Настроить расписание", "Удалить запись",
                                                              "Удалить расписание"]]
stand_menu = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
stand_menu.row(standard_buttons[0], standard_buttons[1])
stand_menu.row(standard_buttons[2], standard_buttons[3])
stand_menu.row(standard_buttons[4])

accept_buttons = [telebot.types.KeyboardButton(x) for x in ["Подтвердить",
                                                            "Отмена"]]
accept_menu = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
accept_menu.row(accept_buttons[0], accept_buttons[1])


def send_to_admin(msg):
    id_ = get_chat_id("EluciferE")
    bot.send_message(id_, msg)


def send_messages():
    while True:
        sleep(5)
        try:
            messages = get_messages()
            for message in messages:
                chat_id = get_chat_id(message[0])
                bot.send_message(chat_id, message[1])
                remove_message(message[0], message[1])
        except Exception as e:
            tg_logger.error(f"[SEND] - {e}")


@bot.message_handler(func=lambda message: True)
def any_command(message):
    # LOGS
    user = message.from_user.username
    text = message.text
    tg_logger.info(f"[GOT] {user}: {text}")

    status = user_status(user)

    if not status:
        add_user(message.chat.id, user)
        bot.send_message(message.chat.id, banner, reply_markup=first_menu)

    elif "New" in status and text == "Запросить доступ к боту":
        insert_signup(user, date_now())
        change_status(user, "AskAllow")
        send_to_admin(f"*{user} запрашивает доступ к боту*")
        bot.send_message(message.chat.id, "Запрос отправлен")

    elif "AskAllow" in status:
        bot.send_message(message.chat.id, "Вы уже запросили доступ")

    elif "MainMenu" in status:
        if text == "Мои записи":
            notes = get_notes(user)
            ans = ""
            if notes:
                for note in notes:
                    ans += NOTE.format(note[1], note[2], note[3], note[4]) + '\n\n'
                bot.send_message(message.chat.id, ans, reply_markup=stand_menu)

            if not notes:
                bot.send_message(message.chat.id, "В данный момент у вас нет записей", reply_markup=stand_menu)

        elif text == "Удалить запись":
            notes = get_notes(user)
            if not notes:
                bot.send_message(message.chat.id, "У вас нет записей", reply_markup=stand_menu)
            elif len(notes) == 1:
                note = notes[0]
                bot.send_message(message.chat.id,
                                 f"Ваша запись:\n\n" + NOTE.format(note[1], note[2], note[3], note[4]) +
                                 "\n\nУдалить?", reply_markup=accept_menu)
                change_status(user, "DeleteSingleNote")
            else:
                ans = "Ваши записи:\n\n"
                dates = []
                for note in notes:
                    dates.append(note[1])
                    ans += NOTE.format(note[1], note[2], note[3], note[4]) + '\n\n'
                ans += "Какую хотите удалить?"
                tmp_buttons = [telebot.types.KeyboardButton(x) for x in dates + ["Отмена"]]
                tmp_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                tmp_keyboard.row(tmp_buttons[0], tmp_buttons[1])
                tmp_keyboard.row(tmp_buttons[2])
                bot.send_message(message.chat.id, ans, reply_markup=tmp_keyboard)
                change_status(user, "DeleteMultiNote")

        elif text == "Текущее расписание":
            req = get_request(user)
            if not req:
                bot.send_message(message.chat.id, "В данный момент у вас нет расписания", reply_markup=stand_menu)
            else:
                req = req[0]
                bot.send_message(message.chat.id, TIMETABLE.format(req[1], req[2], req[3], req[4]),
                                 reply_markup=stand_menu)

        elif text == "Настроить расписание":
            change_status(user, "ChooseDay")
            bot.send_message(message.chat.id, "Выберете день:", reply_markup=days_menu)

        elif text == "Удалить расписание":
            req = get_request(user)

            if not req:
                bot.send_message(message.chat.id, "В данный момент у вас нет расписания", reply_markup=stand_menu)
            else:
                req = req[0]
                change_status(user, "DeleteTimetable")
                bot.send_message(message.chat.id, f"Удалить это расписание?\n" +
                                 TIMETABLE.format(req[1], req[2], req[3], req[4]), reply_markup=accept_menu)
        elif text.lower() == 'admin':
            if user == "EluciferE":
                change_status(user, "AdminMenu")
                bot.send_message(message.chat.id, "^^ приветик ^^", reply_markup=admin_keyboard)
            else:
                bot.send_message(message.chat.id, "Тебе сюда нельзя, бяка >:((", reply_markup=stand_menu)

        else:
            bot.send_message(message.chat.id, "Некорректная команда", reply_markup=stand_menu)

    elif "AdminMenu" in status:
        if text == "Запросы на доступ":
            signups = get_signups()
            if signups:
                ans, users = "", []
                for info in signups:
                    user, date = info
                    ans += f"{date} - {user}\n"
                    users.append(user)
                ans += "Одобрить кому-нибудь доступ?"

                tmp_buttons = [telebot.types.KeyboardButton(x) for x in users + ["Отмена"]]
                tmp_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True,
                                                                 one_time_keyboard=True)
                for but in tmp_buttons:
                    tmp_keyboard.row(but)

                bot.send_message(message.chat.id, ans, reply_markup=tmp_keyboard)
                change_status(user, "AcceptAccess")
            else:
                bot.send_message(message.chat.id, "Нет запросов", reply_markup=admin_keyboard)

        elif text == "Пользователи":
            users = get_users()
            ans = '\n'.join([list(x)[0] for x in users])
            bot.send_message(message.chat.id, ans, reply_markup=admin_keyboard)

        elif text == "Основное меню":
            bot.send_message(message.chat.id, "Как прикажете", reply_markup=stand_menu)
            change_status(user, "MainMenu")

    elif "AcceptAccess" in status:
        if text == "Отмена":
            bot.send_message(message.chat.id, "Как скажешь", reply_markup=admin_keyboard)
        elif get_signup(text):
            accept_signup(text)
            bot.send_message(get_chat_id(text), "Можешь записываться ^^", reply_markup=stand_menu)
            change_status(text, "MainMenu")
            bot.send_message(message.chat.id, "Вы такой щедрый ^^", reply_markup=admin_keyboard)
        else:
            bot.send_message(user, "Я не смогла найти такого пользователя T_T", reply_markup=admin_keyboard)
        change_status(text, "AdminMenu")

    elif "DeleteSingleNote" in status:
        if text == "Подтвердить":
            note = get_notes(user)[0]
            delete_note(user, note[1])
            sheet.write("", note[6])
            gc.collect()
            bot.send_message(message.chat.id, "Запись удалена!", reply_markup=stand_menu)
        else:
            bot.send_message(message.chat.id, "Запись не удалена", reply_markup=stand_menu)
        change_status(user, "MainMenu")

    elif "DeleteMultiNote" in status:
        if text == "Отмена":
            bot.send_message(message.chat.id, "Ок...", reply_markup=stand_menu)
            change_status(user, "MainMenu")
        else:
            deleted = False
            notes = get_notes(user)
            for note in notes:
                if text == note[1]:
                    delete_note(user, text)
                    sheet.write("", note[6])
                    gc.collect()
                    deleted = True
            if deleted:
                change_status(user, "MainMenu")
                bot.send_message(message.chat.id, "Запись была удалена", reply_markup=stand_menu)
            else:
                change_status(user, "MainMenu")
                bot.send_message(message.chat.id, "Некоректная дата (или баг, ахах))", reply_markup=stand_menu)

    elif "DeleteTimetable" in status:
        change_status(user, "MainMenu")
        if text == "Подтвердить":
            delete_request(user)
            bot.send_message(message.chat.id, "Расписание удалено!", reply_markup=stand_menu)
        elif text == "Отмена":
            bot.send_message(message.chat.id, "Расписание не удалено", reply_markup=stand_menu)

    elif "ChooseDay" in status:
        text = text.lower()
        if text not in days:
            bot.send_message(message.chat.id, "Некорректный день", reply_markup=days_menu)
        else:
            change_status(user, f"ChooseTime")
            change_tmp(user, f"{text}/")
            if text == "среда":
                bot.send_message(message.chat.id, "Выберете время:", reply_markup=wedn_times_menu)
            else:
                bot.send_message(message.chat.id, "Выберете время:", reply_markup=times_menu)

    elif "ChooseTime" in status:
        day = get_tmp(user).split('/')[0]

        if day == "среда" and text not in times[2:]:
            bot.send_message(message.chat.id, "Некорректное время", reply_markup=wedn_times_menu)

        elif text not in times:
            bot.send_message(message.chat.id, "Некорректное время", reply_markup=times_menu)

        else:
            change_status(user, "ChooseMachine")
            tmp = get_tmp(user)
            change_tmp(user, tmp + f'{text}/')
            bot.send_message(message.chat.id, "Выберете машинку:", reply_markup=machines_menu)

    elif "ChooseMachine" in status:
        if text not in ["1", "2", "3"]:
            bot.send_message(message.chat.id, "Некорректный номер машинки", reply_markup=machines_menu)
        else:
            tmp = get_tmp(user)
            change_tmp(user, tmp + f"{text}/")
            change_status(user, "WriteNote")
            bot.send_message(message.chat.id, "Что вписать в таблицу? (f.e. Иванов, 228б)", reply_markup=None)

    elif "WriteNote" in status:
        if len(text) > 30:
            bot.send_message(message.chat.id, "Слишком много...")
        else:
            tmp = get_tmp(user)
            change_tmp(user, tmp + f"{text}")
            change_status(user, "AcceptTimetable")
            day = tmp.split("/")[0]
            time = tmp.split("/")[1]
            machine = tmp.split("/")[2]
            bot.send_message(message.chat.id, TIMETABLE.format(day, time, machine, text),
                             reply_markup=accept_menu)

    elif "AcceptTimetable" in status:
        if text == "Подтвердить":
            delete_request(user)
            tmp = get_tmp(user)
            request = {"day": tmp.split("/")[0], "time": tmp.split("/")[1],
                       "machine": tmp.split("/")[2], "value": "/".join(tmp.split("/")[3:])}
            insert_request(user, request)
            change_status(user, "MainMenu")
            change_tmp(user, "")
            bot.send_message(message.chat.id, "Запись сохранена", reply_markup=stand_menu)
        else:
            change_status(user, "MainMenu")
            bot.send_message(message.chat.id, "Запись не сохранена", reply_markup=stand_menu)


Thread(target=send_messages).start()
bot.polling()
