from TelegramBot.DialogBranch.Branch import Branch, User

from DataBase.models import Request, Note

from TelegramBot.status import STATUS
from TelegramBot.templates import admin_keyboard, banned_keyboard


class BanSomeoneBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if text == "Назад":
            self.__backMenu(user)
        else:
            self.__banUser(user, text)

    def __backMenu(self, user: User):
        user.status = STATUS.ADMIN_MENU
        self.db.commit()
        self.bot.send_message(user.chat_id, "Хорошо", reply_markup=admin_keyboard)

    def __banUser(self, user: User, text: str):
        user.status = STATUS.ADMIN_MENU

        users = self.db.query(User).all()
        users = [x.username for x in users]

        if "EluciferE" in users:
            users.remove("EluciferE")

        if text not in users:
            self.bot.send_message(user.chat_id, "Такого пользователя нет",
                                  reply_markup=admin_keyboard)
            return

        bannedUser = self.db.query(User).filter_by(username=text).first()
        bannedUser.status = STATUS.BANNED
        bannedUser.tmp = ""

        self.bot.send_message(user.chat_id, f"Забанила {text}", reply_markup=admin_keyboard)
        self.bot.send_message(bannedUser.chat_id, f"Banned", reply_markup=banned_keyboard)

        self.db.query(Request).filter_by(username=bannedUser.username).delete()
        self.db.query(Note).filter_by(username=bannedUser.username).delete()

        self.db.commit()
