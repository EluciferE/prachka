from TelegramBot.DialogBranch.Branch import Branch, User

from TelegramBot.status import STATUS
from TelegramBot.templates import admin_keyboard, stand_keyboard

class UnbanSomeoneBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if "Назад" in text:
            self.__backMenu(user)
        else:
            self.__unbanUser(user, text)

    def __backMenu(self, user: User):
        user.status = STATUS.ADMIN_MENU
        self.bot.send_message(user.chat_id, "Хорошо", reply_markup=admin_keyboard)
        self.db.commit()

    def __unbanUser(self, user: User, text: str):
        users = self.db.query(User).filter_by(status=STATUS.BANNED).all()
        users = [x.username for x in users]
        if text not in users:
            user.status = STATUS.ADMIN_MENU
            self.db.commit()
            self.bot.send_message(user.chat_id, "Такого пользователя нет",
                                  reply_markup=admin_keyboard)
            return

        newUser = self.db.query(User).filter_by(username=text).first()
        newUser.status = STATUS.MAIN_MENU
        newUser.tmp = ""

        self.db.commit()

        self.bot.send_message(user.chat_id, f"Разбанила {text}", reply_markup=admin_keyboard)
        self.bot.send_message(newUser.chat_id, f"Unbanned", reply_markup=stand_keyboard)
