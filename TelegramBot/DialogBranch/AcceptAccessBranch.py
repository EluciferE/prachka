from TelegramBot.DialogBranch.Branch import Branch, User

from TelegramBot.templates import stand_keyboard, admin_keyboard
from TelegramBot.status import STATUS

from DataBase.models import SignUp


class AcceptAccessBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):

        if text == "Отмена":
            self.bot.send_message(user.chat_id, "Как скажешь", reply_markup=admin_keyboard)
        else:
            self.__acceptAccess(user, text)

        user.status = STATUS.ADMIN_MENU
        self.db.commit()

    def __acceptAccess(self, user: User, text: str):
        if not self.db.query(SignUp).filter_by(username=text).first():
            self.bot.send_message(thisUser.chat_id, "Такого нет!", reply_markup=admin_keyboard)
            return

        newUser = self.db.query(User).filter_by(username=text).first()
        newUser.status = STATUS.MAIN_MENU

        self.db.query(SignUp).filter_by(username=text).delete()
        self.bot.send_message(newUser.chat_id, "Можешь записываться ^^", reply_markup=stand_keyboard)
        self.bot.send_message(user.chat_id, "Добавила его", reply_markup=admin_keyboard)
