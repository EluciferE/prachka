from abc import ABC, abstractmethod

from DataBase.models import User


class Branch(ABC):

    def __init__(self, bot):
        self.bot = bot.bot
        self.db = bot.db

    @abstractmethod
    def work(self, user: User, text: str):
        pass
