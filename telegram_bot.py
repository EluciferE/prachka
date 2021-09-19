from config import token
import telebot
import logging
from db import *
from threading import Thread
from time import sleep
from main import sheet

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

# BUTTONS
days_buttons = [telebot.types.KeyboardButton(x.capitalize()) for x in days]
days_menu = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
days_menu.row(days_buttons[0], days_buttons[1], days_buttons[2])
days_menu.row(days_buttons[3], days_buttons[4], days_buttons[5])
days_menu.row(days_buttons[6])

times_buttons = [telebot.types.KeyboardButton(x) for x in times]
times_menu = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
times_menu.row(times_buttons[0], times_buttons[1])
times_menu.row(times_buttons[2], times_buttons[3])

wedn_times_menu = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
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
accept_menu = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
accept_menu.row(accept_buttons[0], accept_buttons[1])


def send_messages():
    while True:
        sleep(5)
        try:
            messages = get_messages()
            for message in messages:
                chat_id = get_chat_id(message[0])[0]
                chat_id = list(chat_id)[0]
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

    if status:
        status = status[0][0]

    if not status:
        add_user(message.chat.id, user)
        bot.send_message(message.chat.id, banner)

    elif "Not logged" in status:
        if text != "^^":
            bot.send_message(message.chat.id, "Неправильный пароль =(")
        else:
            bot.send_message(message.chat.id, "Congrats!", reply_markup=stand_menu)
            change_status(user, "Logged MainMenu")

    elif "Logged" in status:
        if text == "Мои записи":
            notes = get_notes(user)
            ans = ""
            if notes:
                for note in notes:
                    ans += f"Дата: {note[1]}\nДень недели: {note[2]}\n" \
                           f"Время: {note[3]}\nМашинка: {note[4]}\n\n"
                bot.send_message(message.chat.id, ans, reply_markup=stand_menu)

            if not notes:
                bot.send_message(message.chat.id, "В данный момент у вас нет записей", reply_markup=stand_menu)

        elif text == "Удалить запись":
            notes = get_notes(user)
            if not notes:
                bot.send_message(message.chat.id, "У вас нет записей", reply_markup=stand_menu)
            elif len(notes) == 1:
                note = notes[0]
                bot.send_message(message.chat.id, f"Ваша запись:\n\n"
                                                  f"Дата: {note[1]}\n"
                                                  f"День недели: {note[2]}\n"
                                                  f"Время: {note[3]}\n"
                                                  f"Машинка: {note[4]}\n\nУдалить?", reply_markup=accept_menu)
                change_status(user, "Logged/DeleteSingleNote")
            else:
                ans = "Ваши записи:\n\n"
                dates = []
                for note in notes:
                    dates.append(note[1])
                    ans += f"Дата: {note[1]}\nДень недели: {note[2]}\n" \
                           f"Время: {note[3]}\nМашинка: {note[4]}\n\n"
                ans += "Какую хотите удалить?"
                tmp_buttons = [telebot.types.KeyboardButton(x) for x in dates + ["Отмена"]]
                tmp_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                                 one_time_keyboard=True)
                tmp_keyboard.row(tmp_buttons[0], tmp_buttons[1])
                tmp_keyboard.row(tmp_buttons[2])
                bot.send_message(message.chat.id, ans, reply_markup=tmp_keyboard)
                change_status(user, "Logged/DeleteMultiNote")

        elif "DeleteMultiNote" in status:
            if text == "Отмена":
                bot.send_message(message.chat.id, "Ок...", reply_markup=stand_menu)
            deleted = False
            notes = get_notes(user)
            for note in notes:
                if text == note[1]:
                    delete_note(user, text)
                    sheet.write("", note[6])
                    deleted = True
            if deleted:
                change_status(user, "Logged")
                bot.send_message(message.chat.id, "Запись была удалена", reply_markup=stand_menu)
            else:
                change_status(user, "Logged")
                bot.send_message(message.chat.id, "Некоректная дата (или баг, ахах))", reply_markup=stand_menu)

        elif "DeleteSingleNote" in status:
            if text == "Подтвердить":
                note = get_notes(user)[0]
                delete_note(user, note[1])
                sheet.write("", note[6])
                bot.send_message(message.chat.id, "Запись удалена!", reply_markup=stand_menu)
            else:
                bot.send_message(message.chat.id, "Запись не удалена", reply_markup=stand_menu)
            change_status(user, "Logged")

        elif text == "Текущее расписание":
            req = get_request(user)
            if not req:
                bot.send_message(message.chat.id, "В данный момент у вас нет расписания", reply_markup=stand_menu)
                change_status(user, "Logged")
            else:
                req = req[0]
                bot.send_message(message.chat.id, f"День недели: {req[1]}\n"
                                                  f"Время: {req[2]}\n"
                                                  f"Машинка: {req[3]}\n"
                                                  f"Запись: {req[4]}", reply_markup=stand_menu)

        elif text == "Настроить расписание":
            change_status(user, "Logged/Day")
            bot.send_message(message.chat.id, "Выберете день:", reply_markup=days_menu)

        elif text == "Удалить расписание":
            req = get_request(user)

            if not req:
                bot.send_message(message.chat.id, "В данный момент у вас нет расписания", reply_markup=stand_menu)
                change_status(user, "Logged")
            else:
                req = req[0]
                change_status(user, "Logged/DeleteTimetable")
                bot.send_message(message.chat.id, f"Удалить это расписание?\nДень недели: {req[1]}\n"
                                                  f"Время: {req[2]}\n"
                                                  f"Машинка: {req[3]}\n"
                                                  f"Запись: {req[4]}", reply_markup=accept_menu)
        elif "DeleteTimetable" in status:
            if text == "Подтвердить":
                change_status(user, "Logged")
                delete_request(user)
                bot.send_message(message.chat.id, "Расписание удалено!", reply_markup=stand_menu)
            elif text == "Отмена":
                change_status(user, "Logged")
                bot.send_message(message.chat.id, "Расписание не удалено", reply_markup=stand_menu)

        elif text in list(map(lambda x: x.capitalize(), days)) and \
                len(status.split("/")) == 2:

            change_status(user, f"Logged/{text}")
            if text == "Среда":
                bot.send_message(message.chat.id, "Выберете время:", reply_markup=wedn_times_menu)
            else:
                bot.send_message(message.chat.id, "Выберете время:", reply_markup=times_menu)

        elif text in times and len(status.split("/")) == 2:
            change_status(user, status + f"/{text}")
            bot.send_message(message.chat.id, "Выберете машинку:", reply_markup=machines_menu)

        elif text in ["1", "2", "3"] and len(status.split("/")) == 3:
            change_status(user, status + f"/{text}")
            bot.send_message(message.chat.id, "Что вписать в таблицу?", reply_markup=None)

        elif len(status.split("/")) == 4:
            change_status(user, status + f"/{text}")
            day = status.split("/")[1]
            time = status.split("/")[2]
            machine = status.split("/")[3]
            bot.send_message(message.chat.id, f"День недели: {day}\n"
                                              f"Время: {time}\n"
                                              f"Машинка: {machine}\n"
                                              f"Вписать туда: {text}", reply_markup=accept_menu)
        elif len(status.split("/")) >= 5:
            if text == "Подтвердить":
                delete_request(user)
                request = {"day": status.split("/")[1],
                           "time": status.split("/")[2],
                           "machine": status.split("/")[3],
                           "value": "/".join(status.split("/")[4:])}
                insert_request(user, request)
                change_status(user, "Logged")
                bot.send_message(message.chat.id, "Запись сохранена", reply_markup=stand_menu)
            elif text == "Отмена":
                change_status(user, "Logged")
                bot.send_message(message.chat.id, "Запись не сохранена", reply_markup=stand_menu)


Thread(target=send_messages).start()
bot.polling()
