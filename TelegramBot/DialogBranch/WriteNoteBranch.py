from TelegramBot.DialogBranch.Branch import Branch, User
from TelegramBot.DialogBranch.utils import parseTmp, createKeyboard

from DataBase.models import Request

from TelegramBot.templates import TIMETABLE, accept_timetable_keyboard, back, times1Machine, times23Machine
from TelegramBot.status import STATUS


class WriteNoteBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if "Назад" in text:
            self.__backMenu(user)
        else:
            self.__writeNote(user, text)

    def __backMenu(self, user: User):
        tmp = parseTmp(user.tmp)
        day, machine = tmp["day"], tmp["machine"]

        user.tmp = f"{day}/{machine}/"
        user.status = STATUS.CHOOSE_TIME
        self.db.commit()

        keys = times1Machine + [back]
        if machine != "1":
            keys = times23Machine + [back]

        if day == "среда":
            keys = keys[2:]

        keyboard = createKeyboard(keys, 2)
        self.bot.send_message(user.chat_id, "Выбери машинку:", reply_markup=keyboard)

    def __writeNote(self, user: User, text: str):
        if len(text) > 30:
            self.bot.send_message(user.chat_id, "Слишком много... Попробуй ещё раз")
            return

        user.status = STATUS.ACCEPT_TIMETABLE

        tmp = parseTmp(user.tmp)
        day = tmp["day"]
        time = tmp["time"]
        machine = tmp["machine"]
        user.tmp = f"{day}/{time}/{machine}/{text}"

        self.db.commit()

        self.bot.send_message(user.chat_id, TIMETABLE.format(day.capitalize(), time, machine, text),
                              reply_markup=accept_timetable_keyboard)

    def __freeMachines(self, day, time):
        requests = self.db.query(Request).filter_by(day=day, time=time)
        free = ["1", "2", "3"]
        req = [x.machine for x in requests]
        for m in req:
            free.remove(m)
        return free
