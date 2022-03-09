from TelegramBot.DialogBranch.Branch import Branch, User

from TelegramBot.status import STATUS
from Sheets.Sheet.utils import createToken

from TelegramBot.templates import stand_keyboard


class CheckTokenBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if text == "Да":
            self.__createToken(user)
        else:
            self.__backMenu(user)

    def __backMenu(self, user: User):
        user.status = STATUS.MAIN_MENU
        self.db.commit()

        self.bot.send_message(user.chat_id, "Хорошо", reply_markup=stand_keyboard)

    #TODO anti-ddos
    def __createToken(self, user: User):
        createToken(user, self.bot, stand_keyboard)
