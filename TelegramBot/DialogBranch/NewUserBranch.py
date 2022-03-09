from TelegramBot.DialogBranch.Branch import Branch, User

from TelegramBot.status import STATUS
from TelegramBot.templates import first_keyboard

from TelegramBot.DialogBranch.utils import dateNow

from DataBase.models import SignUp


class NewUserBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):

        if text == "Я хочу пользоваться ботом":
            self.__addNewUser(user)

        else:
            self.__defaultAnswer(user)

    def __addNewUser(self, user: User):
        self.db.add(SignUp(user.username, dateNow()))
        user.status = STATUS.ASK_ALLOW
        self.db.commit()

        admin = self.db.query(User).filter_by(username="EluciferE").first()
        self.bot.send_message(admin.chat_id, f"*{user.username} запрашивает доступ к боту*")

        self.bot.send_message(user.chat_id, "Я отправила запрос ^^")

    def __defaultAnswer(self, user):
        self.bot.send_message(user.chat_id, "Сначала нажми на кнопку ⬇️", reply_markup=first_keyboard)
