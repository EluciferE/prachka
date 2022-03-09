import logging
from time import sleep
from TelegramBot.templates import *
from TelegramBot.status import STATUS

from utils import date_now

from datetime import datetime

from Sheets.Sheet.utils import createToken, getSheet
from configs import sheet_id

# For thank stikers
from random import choice
from TelegramBot.stikers import THANK_STIKERS

from DataBase import Session, User, SignUp, Note, Request, AntiSpam

from TelegramBot.Factory.Factory import Factory

from os import path, remove


# TODO make methods __method
class TgBot:
    def __init__(self, token_, database: Session):
        self.bot = telebot.TeleBot(token_)
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

        @self.bot.message_handler(func=lambda message: True)
        def any_command(message):
            user = message.from_user.username
            text = message.text
            chat_id = message.chat.id

            if "Назад" in text:
                self.tg_logger.info(f"[GOT] {user}: Назад")
            else:
                self.tg_logger.info(f"[GOT] {user}: {text}")

            thisUser = self.db.query(User).filter_by(chat_id=chat_id).first()
            if not thisUser:
                if user == "EluciferE":
                    thisUser = User(message.chat.id, user, STATUS.MAIN_MENU)
                else:
                    thisUser = User(message.chat.id, user, STATUS.NEW)
                self.db.add(thisUser)
                self.db.commit()

                if user != "EluciferE":
                    self.bot.send_message(thisUser.chat_id, banner, reply_markup=first_keyboard)

            elif thisUser.username != user:

                self.db.query(Request).filter_by(username=thisUser.username).all().update(
                    {"username": user}, "fetch"
                )
                self.db.query(Note).filter_by(username=thisUser.username).all().update(
                    {"username": user}, "fetch"
                )
                self.db.query(SignUp).filter_by(username=thisUser.username).all().update(
                    {"username": user}, "fetch"
                )
                self.db.query(AntiSpam).filter_by(username=thisUser.username).all().update(
                    {"username": user}, "fetch"
                )
                thisUser.username = user
                self.db.commit()

            factory = Factory(self)
            factory.execute(thisUser, text)

    def start_bot(self):
        while True:
            try:
                self.bot_logger.info("Bot has just started")
                self.bot.polling(none_stop=True)
            except Exception as e:
                self.bot_logger.error(e)
                print(e)
                self.bot_logger.info("Bot has just stopped")
                sleep(10)

    def send_to_admin(self, msg):
        id_ = self.db.query(User).filter_by(username="EluciferE").first().chat_id
        self.bot.send_message(id_, msg)

    def send_to_user(self, username, message, keyboard=None):
        while True:
            try:
                user: User = self.db.query(User).filter_by(username=username).first()
                self.bot.send_message(user.chat_id, message, reply_markup=keyboard)
                break
            except Exception as e:
                self.tg_logger.error(f"SEND TO USER {username = }, {message = }, error: {e}")
                sleep(5)
