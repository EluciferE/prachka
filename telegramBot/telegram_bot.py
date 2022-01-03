import logging
from time import sleep
import gc
from telegramBot.templates import *
from telegramBot.status import STATUS
from dataBase.db import DataBase
from datetime import datetime
from utils import date_now

# For thank stiker
from random import choice
from telegramBot.stikers import THANK_STIKERS

from sheetWork.sheet import get_sheet
from configs.config import sheet_id
from sheetWork.sheet import create_config

from os import path, remove


class TgBot:
    def __init__(self, token_, database: DataBase, sheet_=None):
        self.bot = telebot.TeleBot(token_)
        self.sheet = sheet_
        self.db = database

        logging.basicConfig(level=logging.INFO)
        tg_logs = logging.FileHandler('logs/chat.log')
        tg_logs.setFormatter(logging.Formatter('[%(asctime)s] - [%(levelname)s] - %(message)s'))
        self.tg_logger = logging.getLogger('chat')
        self.tg_logger.addHandler(tg_logs)
        self.tg_logger.propagate = False

        bot_logs = logging.FileHandler('logs/bot.log')
        bot_logs.setFormatter(logging.Formatter('[%(asctime)s] - [%(levelname)s] - %(message)s'))
        self.bot_logger = logging.getLogger('bot')
        self.bot_logger.addHandler(bot_logs)
        self.bot_logger.propagate = False

        self.working = True

        @self.bot.message_handler(func=lambda message: True)
        def any_command(message):

            if self.sheet == -1:
                self.sheet = get_sheet("EluciferE", sheet_id, self)
                if self.sheet != -1:
                    self.send_to_admin("Получила токен, спасибо <3")

            user = message.from_user.username
            text = message.text

            if "Назад" in text:
                self.tg_logger.info(f"[GOT] {user}: Назад")
            else:
                self.tg_logger.info(f"[GOT] {user}: {text}")

            status = self.db.user_status(user)

            if not status:
                self.db.add_user(message.chat.id, user)
                self.bot.send_message(message.chat.id, banner, reply_markup=first_keyboard)
                status = self.db.user_status(user)

            if status == STATUS.NEW and text == "Я хочу пользоваться ботом":
                self.new_user(message)
                return

            elif status == STATUS.BANNED:
                self.bot.send_message(message.chat.id, "Злюка(")
                return

            elif "спасибо" in text.lower() and status != STATUS.WRITE_NOTE:
                self.bot.send_sticker(message.chat.id, choice(THANK_STIKERS))
                return

            elif status == STATUS.NEW:
                self.bot.send_message(message.chat.id, "Сначала нажми на кнопку ⬇️", reply_markup=first_keyboard)

            elif status == STATUS.ASK_ALLOW:
                self.bot.send_message(message.chat.id, "Ты уже попросил доступ")
                return

            elif status == STATUS.MAIN_MENU:
                if text == "Мои записи":
                    self.my_notes(message)

                elif text == "Удалить запись":
                    self.delete_notes(message)

                elif text == "Моё расписание":
                    self.my_timetable(message)

                elif text == "Настроить расписание":
                    self.db.change_status(user, STATUS.CHOOSE_DAY)
                    self.bot.send_message(message.chat.id, "Выбери день:", reply_markup=days_keyboard)

                elif text == "Удалить расписание":
                    self.delete_timetable(message)

                elif text == "Авторизация":
                    self.check_token(message)

                elif text.lower() == 'admin':
                    if user == "EluciferE":
                        self.db.change_status(user, STATUS.ADMIN_MENU)
                        self.bot.send_message(message.chat.id, "^^ приветик ^^", reply_markup=admin_keyboard)
                    else:
                        self.bot.send_message(message.chat.id, "Тебе сюда нельзя, бяка", reply_markup=stand_keyboard)

                else:
                    self.bot.send_message(message.chat.id, "Некорректная команда", reply_markup=stand_keyboard)

            elif status == STATUS.ADMIN_MENU:
                if user != "EluciferE":
                    self.send_to_admin(f"Someone in admin menu. {user}")
                    return

                if text == "Запросы на доступ":
                    self.ask_for_allow(message)

                elif text == "Пользователи":
                    users = self.db.get_users()
                    ans = '\n'.join([list(x)[0] for x in users])
                    self.bot.send_message(message.chat.id, ans, reply_markup=admin_keyboard)

                elif text == "Основное меню":
                    self.bot.send_message(message.chat.id, "Как прикажете", reply_markup=stand_keyboard)
                    self.db.change_status(user, STATUS.MAIN_MENU)

                elif text == "Забанить":
                    self.ban_someone(message)

                elif text == "Разбанить":
                    self.unban_someone(message)

                else:
                    self.bot.send_message(message.chat.id, "Я не поняла....прости...", reply_markup=admin_keyboard)

            elif status == STATUS.ACCEPT_ACCESS:
                if text == "Отмена":
                    self.bot.send_message(message.chat.id, "Как скажешь", reply_markup=admin_keyboard)
                elif self.db.get_signup(text):
                    self.db.accept_signup(text)
                    self.bot.send_message(self.db.get_chat_id(text), "Можешь записываться ^^",
                                          reply_markup=stand_keyboard)
                    self.db.change_status(text, STATUS.MAIN_MENU)
                    self.bot.send_message(message.chat.id, "Вы такой щедрый ^^", reply_markup=admin_keyboard)
                else:
                    self.bot.send_message(message.chat.id, "Я не смогла найти такого пользователя T_T",
                                          reply_markup=admin_keyboard)
                self.db.change_status(user, "AdminMenu")

            elif status == STATUS.BAN_SOMEONE:
                self.try_to_ban(message)

            elif status == STATUS.UNBAN_SOMEONE:
                self.try_to_unban(message)

            elif status == STATUS.DELETE_NOTE:
                self.db.change_status(user, STATUS.MAIN_MENU)
                if text == "Отмена":
                    self.bot.send_message(message.chat.id, "Как хочешь", reply_markup=stand_keyboard)
                else:
                    deleted = False
                    notes = self.db.get_notes(user)
                    for note in notes:
                        if text == note[1]:
                            if not path.exists(f"tokens/{user}.json"):
                                self.bot.send_message(message.chat.id, "Ты не авторизован", reply_markup=stand_keyboard)
                                return

                            tmp_sheet = get_sheet(user, sheet_id, self)
                            ans = tmp_sheet.write("", note[6])
                            if ans != 0:
                                self.bot.send_message(message.chat.id, "Что-то пошло не так(((", reply_markup=stand_keyboard)
                                self.send_to_admin(f"{user} не смог удалить запись... Чекай логи")
                            else:
                                self.db.delete_note_by_day(user, text)
                                gc.collect()
                                deleted = True
                    if deleted:
                        self.bot.send_message(message.chat.id, "Я удалила запись", reply_markup=stand_keyboard)

            elif status == STATUS.DELETE_TIMETABLE:
                self.db.change_status(user, STATUS.MAIN_MENU)
                if text == "Подтвердить":
                    self.db.delete_request(user)
                    self.bot.send_message(message.chat.id, "Я удалила расписание", reply_markup=stand_keyboard)
                    self.send_to_admin(f"*{user} удалил расписание*")
                elif text == "Отмена":
                    self.bot.send_message(message.chat.id, "Расписание не удалено", reply_markup=stand_keyboard)

            elif status == STATUS.CHOOSE_DAY:
                if "Назад" in text:
                    self.db.change_status(user, STATUS.MAIN_MENU)
                    self.bot.send_message(message.chat.id, "^^", reply_markup=stand_keyboard)
                    return

                if text not in days:
                    self.bot.send_message(message.chat.id, "Некорректный день", reply_markup=days_keyboard)

                else:
                    text = text.lower()
                    self.db.change_status(user, STATUS.CHOOSE_TIME)
                    self.db.change_tmp(user, f"{text}/")

                    # Покажем ему время!!!!
                    banned_time = []
                    requests = self.get_all_requests()
                    requests = [x for x in requests if x["day"] == text]
                    ans = f"Свободные места в расписании бота\n\n"
                    if text == "понедельник":
                        ans += f"{text.capitalize()}   Машинки\n"
                    elif text == "вторник":
                        ans += f"    {text.capitalize()}         Машинки\n"
                    elif text == "среда":
                        ans += f"       {text.capitalize()}           Машинки\n"
                    elif text == "четверг":
                        ans += f"     {text.capitalize()}         Машинки\n"
                    elif text == "пятница":
                        ans += f"    {text.capitalize()}         Машинки\n"
                    elif text == "суббота":
                        ans += f"    {text.capitalize()}          Машинки\n"
                    elif text == "воскресенье":
                        ans += f"{text.capitalize()}     Машинки\n"
                    my_time = times
                    if text == "среда":
                        my_time = times[2:]
                    for time_ in my_time:
                        if time_ == times[0]:
                            ans += "0"
                        ans += f"{time_}:      "

                        machines = [x["machine"] for x in requests if x["time"] == time_]
                        if len(machines) == 3:
                            banned_time.append(time_)
                        ans += ("1" if "1" not in machines else "  ") + "     "
                        ans += ("2" if "2" not in machines else "  ") + "     "
                        ans += ("3" if "3" not in machines else "  ")
                        ans += "\n"

                    self.bot.send_message(message.chat.id, ans)
                    key_times = [x for x in my_time if x not in banned_time]
                    tmp_keyboard = self.create_keyboard(key_times + [back], 2)
                    if text == "среда":
                        self.bot.send_message(message.chat.id, "Выбери время:", reply_markup=tmp_keyboard)
                    else:
                        self.bot.send_message(message.chat.id, "Выбери время:", reply_markup=tmp_keyboard)

            elif status == STATUS.CHOOSE_TIME:
                day = self.parse_tmp(self.db.get_tmp(user))["day"]

                if "Назад" in text:
                    self.db.change_tmp(user, "")
                    self.db.change_status(user, STATUS.CHOOSE_DAY)
                    self.bot.send_message(message.chat.id, "Выбери день:", reply_markup=days_keyboard)
                    return

                if day == "среда" and text not in times[2:]:
                    self.bot.send_message(message.chat.id, "Некорректное время", reply_markup=wedn_times_keyboard)

                elif text not in times:
                    self.bot.send_message(message.chat.id, "Некорректное время", reply_markup=times_keyboard)

                else:
                    self.db.change_status(user, STATUS.CHOOSE_MACHINE)
                    tmp = self.db.get_tmp(user)
                    self.db.change_tmp(user, tmp + f'{text}/')
                    free_machines = self.free_machines(day, text)
                    tmp_keyboard = self.create_keyboard(free_machines + [back], 3)
                    self.bot.send_message(message.chat.id, "Выбери машинку:", reply_markup=tmp_keyboard)

            elif status == STATUS.CHOOSE_MACHINE:
                tmp = self.db.get_tmp(user)

                if "Назад" in text:
                    day = self.parse_tmp(tmp)["day"]
                    self.db.change_tmp(user, day + "/")
                    self.db.change_status(user, STATUS.CHOOSE_TIME)

                    # Пересмотреть клавиатуру
                    key_times = self.free_times(day)
                    tmp_keyboard = self.create_keyboard(key_times + [back], 2)
                    if text == "среда":
                        self.bot.send_message(message.chat.id, "Выбери время:", reply_markup=tmp_keyboard)
                    else:
                        self.bot.send_message(message.chat.id, "Выбери время:", reply_markup=tmp_keyboard)
                    return

                if text not in ["1", "2", "3"]:
                    tmp = self.parse_tmp(tmp)
                    free_machines = self.free_machines(tmp["day"], tmp["time"])
                    tmp_keyboard = self.create_keyboard(free_machines + [back], 3)
                    self.bot.send_message(message.chat.id, "Некорректный номер машинки", reply_markup=tmp_keyboard)
                else:
                    self.db.change_tmp(user, tmp + f"{text}/")
                    self.db.change_status(user, STATUS.WRITE_NOTE)

                    req = self.db.get_request(user)
                    keyboard = back_keyboard
                    if req:
                        value = req[0][-1]
                        keyboard = self.create_keyboard([value, back], 2)

                    self.bot.send_message(message.chat.id, "Что вписать в таблицу? (f.e. Иванов, 228г)",
                                          reply_markup=keyboard)

            elif status == STATUS.WRITE_NOTE:
                tmp = self.parse_tmp(self.db.get_tmp(user))
                if "Назад" in text:
                    day, time_ = tmp["day"], tmp["time"]
                    self.db.change_tmp(user, f"{day}/{time_}/")
                    self.db.change_status(user, STATUS.CHOOSE_MACHINE)

                    free_machines = self.free_machines(day, time_)
                    tmp_keyboard = self.create_keyboard(free_machines + [back], 3)
                    self.bot.send_message(message.chat.id, "Выбери машинку:", reply_markup=tmp_keyboard)

                elif len(text) > 30:
                    self.bot.send_message(message.chat.id, "Слишком много... Попробуй ещё раз")
                else:
                    self.db.change_status(user, STATUS.ACCEPT_TIMETABLE)
                    day = tmp["day"]
                    time_ = tmp["time"]
                    machine = tmp["machine"]
                    self.db.change_tmp(user, f"{day}/{time_}/{machine}/{text}")

                    self.bot.send_message(message.chat.id, TIMETABLE.format(day.capitalize(), time_, machine, text),
                                          reply_markup=accept_timetable_keyboard)

            elif status == STATUS.ACCEPT_TIMETABLE:
                if "Назад" in text:
                    tmp = self.db.get_tmp(user)
                    day, time_, machine = tmp["day"], tmp["time"], tmp["machine"]
                    self.db.change_status(user, f"{day}/{time}/{machine}/")
                    self.db.change_status(user, STATUS.WRITE_NOTE)
                    self.bot.send_message(message.chat.id, "Что вписать в таблицу? (f.e. Иванов, 228г)",
                                          reply_markup=back_keyboard)

                elif text == "Подтвердить":
                    tmp = self.parse_tmp(self.db.get_tmp(user))
                    request = {"day": tmp["day"], "time": tmp["time"],
                               "machine": tmp["machine"], "value": tmp["note"]}

                    all_req = self.get_all_requests()
                    target = [x for x in all_req if
                              x["day"] == tmp["day"] and x["time"] == tmp["time"] and x["machine"] == tmp["machine"]]

                    if target:
                        self.db.change_status(user, STATUS.MAIN_MENU)
                        self.db.change_tmp(user, "")
                        self.bot.send_message(message.chat.id, "Это место уже занято", reply_markup=stand_keyboard)
                        return

                    self.db.delete_request(user)
                    self.db.insert_request(user, request)
                    self.db.change_status(user, STATUS.MAIN_MENU)
                    self.db.change_tmp(user, "")

                    self.bot.send_message(message.chat.id, "Я сохранила расписание", reply_markup=stand_keyboard)
                    if user != "EluciferE":
                        self.send_to_admin(f"*{user} обновил расписание:\n{tmp['day']}\n" +
                                           f"{tmp['time']}\nМашинка: {tmp['machine']}\n{tmp['note']}*")

                else:
                    self.db.change_status(user, STATUS.MAIN_MENU)
                    self.db.change_tmp(user, "")
                    self.bot.send_message(message.chat.id, "Расписание не сохранено", reply_markup=stand_keyboard)
            elif status == STATUS.CHECK_TOKEN:
                self.db.change_status(user, STATUS.MAIN_MENU)
                if text == "Да":
                    create_config(user, self)
                else:
                    self.bot.send_message(message.chat.id, "Хорошо", reply_markup=stand_keyboard)

            elif status == STATUS.ANALYZE_TOKEN:
                self.db.change_status(user, STATUS.MAIN_MENU)
                if text == "Поменять учетную запись":
                    remove(f"tokens/{user}.json")
                    create_config(user, self)
                elif text == "Удалить авторизацию":
                    remove(f"tokens/{user}.json")
                    self.bot.send_message(message.chat.id, "Авторизация удалена", reply_markup=stand_keyboard)
                else:
                    self.bot.send_message(message.chat.id, "^^", reply_markup=stand_keyboard)

    def start_bot(self):
        while True:
            try:
                self.bot_logger.info("Bot has just started")
                self.bot.polling(none_stop=True)
                self.working = True
            except Exception as e:
                self.bot_logger.error(e)
                self.bot_logger.info("Bot has just stopped")
                self.working = False
                sleep(15)

    def send_to_admin(self, msg):
        id_ = self.db.get_chat_id("EluciferE")
        self.bot.send_message(id_, msg)

    def send_messages(self, user, message):
        try:
            chat_id = self.db.get_chat_id(user)
            self.bot.send_message(chat_id, message)

        except Exception as e:
            self.tg_logger.error(f"[SEND] - {e}")

    def get_all_requests(self):
        requests = self.db.get_requests()
        req = []
        for request in requests:
            tmp = {"day": request[1], "time": request[2], "machine": request[3]}
            req.append(tmp)
        return req

    def check_token(self, message):
        if path.exists(f"tokens/{message.from_user.username}.json"):
            self.bot.send_message(message.chat.id, "Ты уже авторизован", reply_markup=analyze_token_keyboard)
            self.db.change_status(message.from_user.username, STATUS.ANALYZE_TOKEN)
        else:
            self.bot.send_message(message.chat.id, "Ты не авторизован. Хочешь авторизоваться сейчас?",
                                  reply_markup=ask_token_keyboard)
            self.db.change_status(message.from_user.username, STATUS.CHECK_TOKEN)

    @staticmethod
    def parse_tmp(tmp):
        tmp = tmp.split('/')
        tmp = [x for x in tmp if x]
        ans = {}
        if len(tmp) > 0:
            ans["day"] = tmp[0]
        if len(tmp) > 1:
            ans["time"] = tmp[1]
        if len(tmp) > 2:
            ans["machine"] = tmp[2]
        if len(tmp) > 3:
            ans["note"] = '/'.join(tmp[3:])
        return ans

    def new_user(self, message):
        user = message.from_user.username

        self.db.insert_signup(user, date_now())
        self.db.change_status(user, STATUS.ASK_ALLOW)
        self.send_to_admin(f"*{user} запрашивает доступ к боту*")
        self.bot.send_message(message.chat.id, "Я отправила запрос ^^")

    def my_notes(self, message):
        user = message.from_user.username

        notes = self.db.get_notes(user)
        ans = ""
        if notes:
            for note in notes:
                now = datetime.strptime(date_now(), "%d.%m.%Y")
                note_date = datetime.strptime(note[1], "%d.%m.%Y")
                if now <= note_date:
                    ans += NOTE.format(note[1], note[2].capitalize(), note[3], note[4]) + '\n\n'
            if ans:
                self.bot.send_message(message.chat.id, ans, reply_markup=stand_keyboard)
            else:
                self.bot.send_message(message.chat.id, "Я не нашла твоих записей", reply_markup=stand_keyboard)
        else:
            self.bot.send_message(message.chat.id, "Я не нашла твоих записей", reply_markup=stand_keyboard)

    def delete_notes(self, message):
        user = message.from_user.username
        notes = self.db.get_notes(user)

        now = datetime.strptime(date_now(), "%d.%m.%Y")

        if not notes:
            self.bot.send_message(message.chat.id, "Я не нашла твоих записей", reply_markup=stand_keyboard)
            return

        ans = "Ваши записи:\n\n"
        dates = []
        for note in notes:
            note_date = datetime.strptime(note[1], "%d.%m.%Y")
            if now <= note_date:
                dates.append(note[1])
                ans += NOTE.format(note[1], note[2], note[3], note[4]) + '\n\n'
        ans += "Какую хочешь удалить?"

        if not dates:
            self.bot.send_message(message.chat.id, "Я не нашла твоих записей", reply_markup=stand_keyboard)
            return

        tmp_buttons = [telebot.types.KeyboardButton(x) for x in dates + ["Отмена"]]
        tmp_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for x in tmp_buttons:
            tmp_keyboard.row(x)
        self.bot.send_message(message.chat.id, ans, reply_markup=tmp_keyboard)
        self.db.change_status(user, STATUS.DELETE_NOTE)

    def my_timetable(self, message):
        user = message.from_user.username
        req = self.db.get_request(user)
        if not req:
            self.bot.send_message(message.chat.id, "У тебя нет расписания", reply_markup=stand_keyboard)
        else:
            req = req[0]
            self.bot.send_message(message.chat.id, TIMETABLE.format(req[1].capitalize(), req[2], req[3], req[4]),
                                  reply_markup=stand_keyboard)

    def delete_timetable(self, message):
        user = message.from_user.username
        req = self.db.get_request(user)

        if not req:
            self.bot.send_message(message.chat.id, "У тебя нет расписания", reply_markup=stand_keyboard)
        else:
            req = req[0]
            self.db.change_status(user, STATUS.DELETE_TIMETABLE)
            self.bot.send_message(message.chat.id, f"Удалить это расписание?\n" +
                                  TIMETABLE.format(req[1].capitalize(), req[2], req[3], req[4]),
                                  reply_markup=accept_keyboard)

    def ask_for_allow(self, message):
        user = message.from_user.username

        signups = self.db.get_signups()
        if signups:
            ans, users = "", []
            for info in signups:
                target_user, date = info
                ans += f"{date} - {target_user}\n"
                users.append(target_user)
            ans += "Одобрить кому-нибудь доступ?"

            tmp_buttons = [telebot.types.KeyboardButton(x) for x in users + ["Отмена"]]
            tmp_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True,
                                                             one_time_keyboard=True)
            for but in tmp_buttons:
                tmp_keyboard.row(but)

            self.bot.send_message(message.chat.id, ans, reply_markup=tmp_keyboard)
            self.db.change_status(user, STATUS.ACCEPT_ACCESS)
        else:
            self.bot.send_message(message.chat.id, "Нет запросов", reply_markup=admin_keyboard)

    def ban_someone(self, message):
        user = message.from_user.username
        users = self.db.get_users()
        users = [list(x)[0] for x in users]
        ans = '\n'.join(users)
        ans += "\nКого хочешь забанить?"

        tmp_keyboard = self.create_keyboard(users + ["Отмена"], 2)
        self.bot.send_message(message.chat.id, ans, reply_markup=tmp_keyboard)
        self.db.change_status(user, STATUS.BAN_SOMEONE)

    def unban_someone(self, message):
        user = message.from_user.username
        users = self.db.banned_users()
        users = [list(x)[0] for x in users]
        ans = '\n'.join(users)
        ans += "\nКого хочешь разбанить?"

        tmp_keyboard = self.create_keyboard(users + ["Отмена"], 2)
        self.bot.send_message(message.chat.id, ans, reply_markup=tmp_keyboard)
        self.db.change_status(user, STATUS.UNBAN_SOMEONE)

    def try_to_ban(self, message):
        text = message.text
        user = message.from_user.username

        self.db.change_status(user, STATUS.ADMIN_MENU)

        if "Отмена" in text:
            self.bot.send_message(message.chat.id, "^^", reply_markup=admin_keyboard)

        else:
            users = self.db.get_users()
            users = [x[0] for x in users]
            if text not in users:
                self.bot.send_message(message.chat.id, "Я не смогла найти такого пользователя T_T",
                                      reply_markup=admin_keyboard)
                return

            if text == "EluciferE":
                self.bot.send_message(message.chat.id, "Нинада банить себя((",
                                      reply_markup=admin_keyboard)
                return

            self.db.change_status(text, STATUS.BANNED)
            self.db.change_tmp(text, "")

            self.bot.send_message(message.chat.id, f"Забанила {text}", reply_markup=admin_keyboard)
            self.bot.send_message(self.db.get_chat_id(text), f"Banned", reply_markup=banned_keyboard)
            self.db.delete_request(text)

            notes = self.db.get_notes(text)
            for note in notes:
                self.sheet.write("", note[6])
                self.db.delete_all_notes(text)

    def try_to_unban(self, message):
        text = message.text
        user = message.from_user.username

        self.db.change_status(user, STATUS.ADMIN_MENU)

        if "Отмена" in text:
            self.bot.send_message(message.chat.id, "^^", reply_markup=admin_keyboard)

        else:
            users = self.db.banned_users()
            users = [x[0] for x in users]
            if text not in users:
                self.bot.send_message(message.chat.id, "Я не смогла найти такого пользователя T_T",
                                      reply_markup=admin_keyboard)
                return

            self.db.change_status(text, STATUS.MAIN_MENU)
            self.db.change_tmp(text, "")

            self.bot.send_message(message.chat.id, f"Разбанила {text}", reply_markup=admin_keyboard)
            self.bot.send_message(self.db.get_chat_id(text), f"Unbanned", reply_markup=stand_keyboard)

    def send_to_user(self, username, message, keyboard=None):
        while True:
            try:
                chat_id = self.db.get_chat_id(username)
                self.bot.send_message(chat_id, message, reply_markup=keyboard)
                break
            except Exception as e:
                self.tg_logger.error(f"SEND TO USER {username = }, {message = }, error: {e}")
                sleep(5)

    def free_times(self, day):
        requests = self.get_all_requests()
        req = [x for x in requests if x["day"] == day]
        my_time = times
        if day == "среда":
            my_time = times[2:]
        free_time = my_time
        for time_ in my_time:
            here_req = [x for x in req if x["time"] == time_]
            if len(here_req) == 3:
                free_time.remove(time_)
        return free_time

    def free_machines(self, day, time_):
        requests = self.get_all_requests()
        free = ["1", "2", "3"]
        req = [x["machine"] for x in requests if x["day"] == day and x["time"] == time_]
        for m in req:
            free.remove(m)
        return free

    @staticmethod
    def create_keyboard(buttons, row):
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=row, resize_keyboard=True)
        new_buttons = [telebot.types.KeyboardButton(x) for x in buttons]
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
