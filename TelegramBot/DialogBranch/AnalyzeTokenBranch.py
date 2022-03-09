from TelegramBot.DialogBranch.Branch import Branch, User

from TelegramBot.status import STATUS
from Sheets.Sheet.utils import createToken

from TelegramBot.templates import stand_keyboard

from os import remove


class AnalyzeTokenBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if text == "Поменять учетную запись":
            self.__changeToken(user)
        elif text == "Удалить авторизацию":
            self.__deleteToken(user)
        else:
            self.__defaultAnswer(user)

    #TODO Also Anti-ddos
    def __changeToken(self, user: User):
        remove(f"tokens/{user.username}.json")
        createToken(user, self.bot, stand_keyboard)

    def __deleteToken(self, user: User):
        remove(f"tokens/{user.username}.json")
        self.bot.send_message(user.chat_id, "Авторизация удалена", reply_markup=stand_keyboard)

    def __defaultAnswer(self, user: User):
        user.status = STATUS.MAIN_MENU
        self.db.commit()
        self.bot.send_message(user.chat_id, "^^", reply_markup=stand_keyboard)
