from TelegramBot.DialogBranch.Branch import Branch, User

from DataBase.models import Request

from TelegramBot.status import STATUS
from TelegramBot.templates import stand_keyboard


class DeleteTimetableBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if text == "Подтвердить":
            self.__deleteTimetable(user)
        else:
            self.__backMenu(user)

    def __backMenu(self, user: User):
        user.status = STATUS.MAIN_MENU
        self.bot.send_message(user.chat_id, "Расписание не удалено", reply_markup=stand_keyboard)
        self.db.commit()

    def __deleteTimetable(self, user: User):
        user.status = STATUS.MAIN_MENU
        self.db.query(Request).filter_by(username=user.username).delete()
        self.bot.send_message(user.chat_id, "Я удалила расписание", reply_markup=stand_keyboard)

        if user.username != "EluciferE":
            admin = self.db.query(User).filter_by(username="EluciferE").first()
            self.bot.send_message(admin.chat_id, f"*{user.username} удалил расписание*")
        self.db.commit()
