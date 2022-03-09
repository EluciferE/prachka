from TelegramBot.DialogBranch.Branch import Branch
from DataBase.models import Session, User, Note, Request

from datetime import datetime
from TelegramBot.templates import *

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from TelegramBot.status import STATUS

from os.path import exists
from TelegramBot.DialogBranch.utils import dateNow, createKeyboard


class MainBranch(Branch):
    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if text == "Мои записи":
            self.__myNotes(user)

        elif text == "Удалить запись":
            self.__deleteNote(user)

        elif text == "Моё расписание":
            self.__myTimetable(user)

        elif text == "Настроить расписание":
            self.__editTimetable(user)

        elif text == "Удалить расписание":
            self.__deleteTimetable(user)

        elif text == "Авторизация":
            self.__auth(user)

        elif text.lower() == 'admin':
            self.__adminMenu(user)

        else:
            self.__defaultAnswer(user)

    def __myNotes(self, user: User):
        notes = self.__getValidNotes(user)

        if not notes:
            self.bot.send_message(user.chat_id, "Я не нашла твоих записей", reply_markup=stand_keyboard)
            return

        ans = ""
        for note in notes:
            ans += NOTE.format(note.date, note.day.capitalize(), note.time, note.machine) + '\n\n'

        self.bot.send_message(user.chat_id, ans, reply_markup=stand_keyboard)

    def __deleteNote(self, user: User):
        notes = self.__getValidNotes(user)

        if not notes:
            self.bot.send_message(user.chat_id, "Я не нашла твоих записей", reply_markup=stand_keyboard)
            return

        ans = "Ваши записи:\n\n"
        dates = []
        for note in notes:
            dates.append(note.date)
            ans += NOTE.format(note.date, note.day, note.time, note.machine) + '\n\n'
        ans += "Какую хочешь удалить?"

        keyboard = createKeyboard(dates + [back], 2)
        self.bot.send_message(user.chat_id, ans, reply_markup=keyboard)

        user.status = STATUS.DELETE_NOTE
        self.db.commit()

    def __myTimetable(self, user: User):
        req: Request = self.db.query(Request).filter_by(username=user.username).first()
        if not req:
            self.bot.send_message(user.chat_id, "У тебя нет расписания", reply_markup=stand_keyboard)
        else:
            msg = TIMETABLE.format(req.day.capitalize(), req.time, req.machine, req.value)
            self.bot.send_message(user.chat_id, msg, reply_markup=stand_keyboard)

    def __editTimetable(self, user: User):
        user.status = STATUS.CHOOSE_DAY
        self.db.commit()
        self.bot.send_message(user.chat_id, "Выбери день:", reply_markup=days_keyboard)

    def __deleteTimetable(self, user: User):
        req = self.db.query(Request).filter_by(username=user.username).first()

        if not req:
            self.bot.send_message(user.chat_id, "У тебя нет расписания", reply_markup=stand_keyboard)
        else:
            user.status = STATUS.DELETE_TIMETABLE
            self.db.commit()

            msg = f"Удалить это расписание?\n" + TIMETABLE.format(req.day.capitalize(), req.time, req.machine,
                                                                  req.value)
            self.bot.send_message(user.chat_id, msg, reply_markup=accept_keyboard)

    def __auth(self, user: User):
        if exists(f"tokens/{user.username}.json"):
            self.bot.send_message(user.chat_id, "Ты уже авторизован", reply_markup=analyze_token_keyboard)
            user.status = STATUS.ANALYZE_TOKEN
        else:
            self.bot.send_message(user.chat_id, "Ты не авторизован. Хочешь авторизоваться сейчас?",
                                  reply_markup=ask_token_keyboard)
            user.status = STATUS.CHECK_TOKEN
        self.db.commit()

    def __adminMenu(self, user: User):
        if user.username == "EluciferE":
            user.status = STATUS.ADMIN_MENU
            self.db.commit()

            self.bot.send_message(user.chat_id, "^^ приветик ^^", reply_markup=admin_keyboard)
            return
        else:
            self.bot.send_message(user.chat_id, "Тебе сюда нельзя, бяка", reply_markup=stand_keyboard)

    def __defaultAnswer(self, user: User):
        self.bot.send_message(user.chat_id, "Некорректная команда", reply_markup=stand_keyboard)

    def __getValidNotes(self, user: User) -> list:
        notes = self.db.query(Note).filter_by(username=user.username).all()
        now = datetime.strptime(dateNow(), "%d.%m.%Y")

        validNotes = []
        for note in notes:
            note_date = datetime.strptime(note.date, "%d.%m.%Y")
            if now <= note_date:
                validNotes.append(note)

        return validNotes
