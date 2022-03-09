from TelegramBot.DialogBranch.Branch import Branch, User
from random import choice
from TelegramBot.stikers import THANK_STIKERS


class ThankBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        self.bot.send_sticker(user.chat_id, choice(THANK_STIKERS))
