from TelegramBot.DialogBranch.Branch import Branch, User


class AskedAllowBranch(Branch):

    def __init__(self, bot):
        super().__init__(bot)

    def work(self, user: User, text: str):
        self.bot.send_message(user.chat_id, "Ты уже попросил доступ")
