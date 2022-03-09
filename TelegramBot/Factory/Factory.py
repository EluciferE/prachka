from TelegramBot.DialogBranch.MainBranch import MainBranch
from TelegramBot.DialogBranch.NewUserBranch import NewUserBranch
from TelegramBot.DialogBranch.BannedBranch import BannedBranch
from TelegramBot.DialogBranch.ThankBranch import ThankBranch
from TelegramBot.DialogBranch.AskedAllowBranch import AskedAllowBranch
from TelegramBot.DialogBranch.AdminBranch import AdminBranch
from TelegramBot.DialogBranch.AcceptAccessBranch import AcceptAccessBranch
from TelegramBot.DialogBranch.BanSomeoneBranch import BanSomeoneBranch
from TelegramBot.DialogBranch.UnbanSomeoneBranch import UnbanSomeoneBranch
from TelegramBot.DialogBranch.DeleteNoteBranch import DeleteNoteBranch
from TelegramBot.DialogBranch.DeleteTimetableBranch import DeleteTimetableBranch

from TelegramBot.DialogBranch.ChooseDayBranch import ChooseDayBranch
from TelegramBot.DialogBranch.ChooseTimeBranch import ChooseTimeBranch
from TelegramBot.DialogBranch.ChooseMachineBranch import ChooseMachineBranch
from TelegramBot.DialogBranch.WriteNoteBranch import WriteNoteBranch
from TelegramBot.DialogBranch.AcceptTimetableBranch import AcceptTimetableBranch
from TelegramBot.DialogBranch.CheckTokenBranch import CheckTokenBranch
from TelegramBot.DialogBranch.AnalyzeTokenBranch import AnalyzeTokenBranch

from TelegramBot.status import STATUS

from DataBase.models import User


class Factory:
    def __init__(self, bot):
        self.bot = bot

    def execute(self, user: User, text: str):
        branch = None

        if user.status != STATUS.WRITE_NOTE and "спасибо" in text.lower():
            branch = ThankBranch(self.bot)

        elif user.status == STATUS.ASK_ALLOW:
            branch = AskedAllowBranch(self.bot)

        elif user.status == STATUS.MAIN_MENU:
            branch = MainBranch(self.bot)

        elif user.status == STATUS.NEW:
            branch = NewUserBranch(self.bot)

        elif user.status == STATUS.BANNED:
            branch = BannedBranch(self.bot)

        elif user.status == STATUS.ADMIN_MENU:
            branch = AdminBranch(self.bot)

        elif user.status == STATUS.ACCEPT_ACCESS:
            branch = AcceptAccessBranch(self.bot)

        elif user.status == STATUS.BAN_SOMEONE:
            branch = BanSomeoneBranch(self.bot)

        elif user.status == STATUS.UNBAN_SOMEONE:
            branch = UnbanSomeoneBranch(self.bot)

        elif user.status == STATUS.DELETE_NOTE:
            branch = DeleteNoteBranch(self.bot)

        elif user.status == STATUS.DELETE_TIMETABLE:
            branch = DeleteTimetableBranch(self.bot)

        elif user.status == STATUS.CHOOSE_DAY:
            branch = ChooseDayBranch(self.bot)

        elif user.status == STATUS.CHOOSE_TIME:
            branch = ChooseTimeBranch(self.bot)

        elif user.status == STATUS.CHOOSE_MACHINE:
            branch = ChooseMachineBranch(self.bot)

        elif user.status == STATUS.WRITE_NOTE:
            branch = WriteNoteBranch(self.bot)

        elif user.status == STATUS.ACCEPT_TIMETABLE:
            branch = AcceptTimetableBranch(self.bot)

        elif user.status == STATUS.CHECK_TOKEN:
            branch = CheckTokenBranch(self.bot)

        elif user.status == STATUS.ANALYZE_TOKEN:
            branch = AnalyzeTokenBranch(self.bot)

        if branch:
            branch.work(user, text)
