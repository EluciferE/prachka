from TelegramBot.DialogBranch.Branch import Branch, User

from TelegramBot.templates import days, stand_keyboard, days_keyboard, back, \
    msgTimes, times1Machine, times23Machine

from DataBase.models import Request

from TelegramBot.status import STATUS

from TelegramBot.DialogBranch.utils import createKeyboard


class ChooseDayBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if "Назад" in text:
            self.__backMenu(user)
        else:
            self.__chooseDay(user, text)

    def __backMenu(self, user: User):
        user.status = STATUS.MAIN_MENU
        self.db.commit()
        self.bot.send_message(user.chat_id, "Хорошо", reply_markup=stand_keyboard)

    def __chooseDay(self, user: User, text: str):
        if text not in days:
            self.bot.send_message(user.chat_id, "Некорректный день", reply_markup=days_keyboard)
            return

        text = text.lower()
        user.status = STATUS.CHOOSE_MACHINE
        user.tmp = f"{text}/"
        self.db.commit()

        # Draw a beautiful table
        requests = self.db.query(Request).all()
        requests = [x for x in requests if x.day == text]
        ans = f"Свободные места в расписании бота\n"
        ans += msgTimes[text]

        msgMachines = []

        start = 0
        if text == "среда":
            start = 2

        for i in range(start, 4):
            machines = [x.machine for x in requests if x.time == times1Machine[i] and x.day == text]
            machines += [x.machine for x in requests if x.time == times23Machine[i] and x.day == text]

            msgMachines += [str(x) if str(x) not in machines else "  " for x in range(1, 4)]

        ans = ans.format(*msgMachines)
        self.bot.send_message(user.chat_id, ans)
        tmp_keyboard = createKeyboard(["1", "2", "3"] + [back], 3)
        self.bot.send_message(user.chat_id, "Выбери машинку:", reply_markup=tmp_keyboard)
