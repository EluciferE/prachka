from TelegramBot.DialogBranch.Branch import Branch, User

from TelegramBot.DialogBranch.utils import parseTmp, createKeyboard

from DataBase.models import Request

from TelegramBot.status import STATUS
from TelegramBot.templates import back, times1Machine, times23Machine, back_keyboard


class ChooseTimeBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if "Назад" in text:
            self.__backMenu(user)

        else:
            self.__chooseTime(user, text)

    def __backMenu(self, user: User):
        day = parseTmp(user.tmp)["day"]

        user.tmp = f"{day}/"
        user.status = STATUS.CHOOSE_MACHINE
        self.db.commit()

        keyboard = createKeyboard(["1", "2", "3", back], 3)

        self.bot.send_message(user.chat_id, "Выбери машинку:", reply_markup=keyboard)

    def __chooseTime(self, user: User, text: str):
        day = parseTmp(user.tmp)["day"]
        machine = parseTmp(user.tmp)["machine"]

        times = times1Machine
        if machine != "1":
            times = times23Machine

        if day == "среда" and text not in times[2:]:
            self.bot.send_message(user.chat_id, "Некорректное время")
            return

        if text not in times:
            self.bot.send_message(user.chat_id, "Некорректное время")
            return

        user.status = STATUS.WRITE_NOTE
        user.tmp += f'{text}/'
        self.db.commit()

        req = self.db.query(Request).filter_by(username=user.username).first()
        keyboard = back_keyboard
        if req:
            value = req.value
            keyboard = createKeyboard([value, back], 2)

        self.bot.send_message(user.chat_id, "Что вписать в таблицу? (f.e. Иванов, 228б)", reply_markup=keyboard)

    def __freeMachines(self, day, time):
        requests = self.db.query(Request).filter_by(day=day, time=time).all()
        free = ["1", "2", "3"]
        req = [x.machine for x in requests]
        for m in req:
            free.remove(m)
        return free
