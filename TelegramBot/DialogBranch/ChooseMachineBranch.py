from TelegramBot.DialogBranch.Branch import Branch, User
from TelegramBot.DialogBranch.utils import parseTmp, createKeyboard

from DataBase.models import Request

from TelegramBot.status import STATUS
from TelegramBot.templates import times1Machine, times23Machine, back, back_keyboard, days


class ChooseMachineBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if "Назад" in text:
            self.__backMenu(user)

        else:
            self.__chooseMachine(user, text)

    def __backMenu(self, user: User):
        user.tmp = f""
        user.status = STATUS.CHOOSE_DAY
        self.db.commit()

        #key_times = self.__freeTimes(day)
        tmp_keyboard = createKeyboard(days + [back], 3)
        self.bot.send_message(user.chat_id, "Выбери день:", reply_markup=tmp_keyboard)

    def __chooseMachine(self, user: User, text: str):
        if text not in ["1", "2", "3"]:
            self.bot.send_message(user.chat_id, "Некорректный номер машинки")
            return

        day = parseTmp(user.tmp)["day"]
        user.tmp += f"{text}/"
        user.status = STATUS.CHOOSE_TIME

        self.db.commit()

        #req = self.db.query(Request).filter_by(username=user.username).first()
        #keyboard = back_keyboard
        #if req:
        #    value = req.value
        #    keyboard = createKeyboard([value, back], 2)

        #self.bot.send_message(user.chat_id, "Что вписать в таблицу? (f.e. Иванов, 228б)",
        #                      reply_markup=keyboard)
        keys = times1Machine + [back]
        if text != "1":
            keys = times23Machine + [back]

        if day == "среда":
            keys = keys[2:]

        keyboard = createKeyboard(keys, 2)

        self.bot.send_message(user.chat_id, "Выбери время:", reply_markup=keyboard)

    """
    def __freeTimes(self, day):
        requests = self.db.query(Request).filter_by(day=day).all()
        my_time = times

        if day == "среда":
            my_time = times[2:]

        free_time = my_time[:]
        for time_ in my_time:
            here_req = [x for x in requests if x.time == time_]
            if len(here_req) == 3:
                free_time.remove(time_)

        return free_time
    """