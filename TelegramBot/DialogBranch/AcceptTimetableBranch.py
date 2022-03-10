from TelegramBot.DialogBranch.Branch import Branch, User
from TelegramBot.DialogBranch.utils import createKeyboard, parseTmp

from TelegramBot.status import STATUS
from TelegramBot.templates import stand_keyboard, back_keyboard

from DataBase.models import Request


class AcceptTimetableBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if "Назад" in text:
            self.__backMenu(user)

        elif text == "Подтвердить":
            self.__acceptTimetable(user)

        else:
            self.__declineTimetable(user)

    def __backMenu(self, user: User):
        tmp = parseTmp(user.tmp)
        day, time, machine = tmp["day"], tmp["time"], tmp["machine"]

        user.tmp = f"{day}/{machine}/{time}/"
        user.status = STATUS.WRITE_NOTE

        self.db.commit()

        req = self.db.query(Request).filter_by(username=user.username).first()
        keyboard = back_keyboard
        if req:
            value = req.value
            keyboard = createKeyboard([value, back], 2)

        self.bot.send_message(user.chat_id, "Что вписать в таблицу? (f.e. Иванов, 228г)",
                              reply_markup=keyboard)

    def __acceptTimetable(self, user: User):
        tmp = parseTmp(user.tmp)
        user.tmp = ""

        request = self.db.query(Request).filter_by(day=tmp["day"], time=tmp["time"], machine=tmp["machine"]).first()

        if request:
            user.status = STATUS.MAIN_MENU
            self.db.commit()
            self.bot.send_message(user.chat_id, "Это место уже занято", reply_markup=stand_keyboard)
            return

        self.db.query(Request).filter_by(username=user.username).delete()
        self.db.add(Request(user.username, tmp["day"],
                            tmp["time"], tmp["machine"], tmp["note"]))

        user.status = STATUS.MAIN_MENU
        self.db.commit()

        self.bot.send_message(user.chat_id, "Я сохранила расписание", reply_markup=stand_keyboard)

        if user.username != "EluciferE":
            admin = self.db.query(User).filter_by(username="EluciferE").first()
            msg = f"*{user.username} обновил расписание:\n{tmp['day']}\n" + \
                  f"{tmp['time']}\nМашинка: {tmp['machine']}\n{tmp['note']}*"

            self.bot.send_message(admin.chat_id, msg)

    def __declineTimetable(self, user: User):
        user.status = STATUS.MAIN_MENU
        user.tmp = ""
        self.db.commit()

        self.bot.send_message(user.chat_id, "Расписание не сохранено", reply_markup=stand_keyboard)
