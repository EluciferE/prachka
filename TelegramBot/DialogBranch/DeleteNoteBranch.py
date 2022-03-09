from TelegramBot.DialogBranch.Branch import Branch, User

from DataBase.models import Note

from TelegramBot.status import STATUS
from TelegramBot.templates import stand_keyboard

from Sheets.Sheet.utils import getSheet
from configs import sheet_id
from os.path import exists

class DeleteNoteBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        if "Назад" in text:
            self.__backMenu(user)
        else:
            self.__deleteNote(user, text)

    def __backMenu(self, user: User):
        user.status = STATUS.MAIN_MENU
        self.bot.send_message(user.chat_id, "Хорошо", reply_markup=stand_keyboard)
        self.db.commit()

    def __deleteNote(self, user: User, text: str):
        user.status = STATUS.MAIN_MENU

        notes = self.db.query(Note).filter_by(username=user.username).all()
        for note in notes:
            if text == note.date:
                if not exists(f"tokens/{user.username}.json"):
                    self.bot.send_message(user.chat_id, "Ты не авторизован", reply_markup=stand_keyboard)
                    self.db.commit()
                    return

                tmp_sheet = getSheet(user.username, sheet_id)
                ans = tmp_sheet.write("", note.cell)
                if not ans:
                    self.bot.send_message(user.chat_id, "Чёт не удалилось... Попробуй ещё раз",
                                          reply_markup=stand_keyboard)

                    admin = self.db.query(User).filter_by(username="EluciferE").first()
                    self.bot.send_message(admin.chat_id, f"{user.username} не смог удалить запись... Чекай логи")
                    self.db.commit()

                else:
                    self.db.query(Note).filter_by(username=user.username, date=text).delete()
                    self.bot.send_message(user.chat_id, "Я удалила запись", reply_markup=stand_keyboard)
                    self.db.commit()
