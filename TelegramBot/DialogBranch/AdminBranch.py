from TelegramBot.DialogBranch.Branch import Branch, User
from TelegramBot.status import STATUS

from DataBase.models import SignUp

from TelegramBot.DialogBranch.utils import createKeyboard
from TelegramBot.templates import back, admin_keyboard, stand_keyboard


class AdminBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if user.username != "EluciferE":
            admin = self.db.query(User).filter_by(username="EluciferE").first()
            self.bot.send_message(admin.chat_id, f"Кто-то в админке, hehe... {user.username}")

        elif text == "Запросы на доступ":
            self.__askedAllows(user)

        elif text == "Пользователи":
            self.__getUsers(user)

        elif text == "Основное меню":
            self.__toMainMenu(user)

        elif text == "Забанить":
            self.__banUser(user)

        elif text == "Разбанить":
            self.__unbanUser(user)

        else:
            self.__defaultAnswer(user)

    def __askedAllows(self, user: User):
        signups = self.db.query(SignUp).all()
        if signups:
            ans, users = "", []
            for signup in signups:
                target_user, date = signup.username, signup.date
                ans += f"{date} - {target_user}\n"
                users.append(target_user)
            ans += "Одобрить кому-нибудь доступ?"

            keyboard = createKeyboard(users + [back], 2)
            self.bot.send_message(user.chat_id, ans, reply_markup=keyboard)
            user.status = STATUS.ACCEPT_ACCESS
            self.db.commit()

        else:
            self.bot.send_message(user.chat_id, "Запросов нет", reply_markup=admin_keyboard)

    def __getUsers(self, user: User):
        users = self.db.query(User).all()
        ans = "Пользователи:\n\n"
        ans += '\n'.join([f"{ind + 1}. {botUser.username}" for ind, botUser in enumerate(users)])
        self.bot.send_message(user.chat_id, ans, reply_markup=admin_keyboard)

    def __toMainMenu(self, user: User):
        self.bot.send_message(user.chat_id, "Хорошо", reply_markup=stand_keyboard)
        user.status = STATUS.MAIN_MENU
        self.db.commit()

    def __banUser(self, user: User):
        users = self.db.query(User).all()
        users = [x.username for x in users]

        if "EluciferE" in users:
            users.remove("EluciferE")

        if not users:
            self.bot.send_message(user.chat_id, "Нет юзеров", reply_markup=admin_keyboard)
            return

        ans = '\n'.join(users)
        ans += "\nКого хочешь забанить?"

        tmp_keyboard = createKeyboard(users + [back], 2)
        self.bot.send_message(user.chat_id, ans, reply_markup=tmp_keyboard)
        user.status = STATUS.BAN_SOMEONE
        self.db.commit()

    def __unbanUser(self, user: User):
        users = self.db.query(User).filter_by(status=STATUS.BANNED).all()
        users = [x.username for x in users]

        if not users:
            self.bot.send_message(user.chat_id, "Нет забаненных юзеров", reply_markup=admin_keyboard)
            return

        ans = '\n'.join(users)
        ans += "\nКого хочешь разбанить?"

        tmp_keyboard = createKeyboard(users + ["Отмена"], 2)
        self.bot.send_message(user.chat_id, ans, reply_markup=tmp_keyboard)

        user.status = STATUS.UNBAN_SOMEONE
        self.db.commit()

    def __defaultAnswer(self, user: User):
        self.bot.send_message(user.chat_id, "нипанятна", reply_markup=admin_keyboard)
