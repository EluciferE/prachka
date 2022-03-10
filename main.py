from Sheets.MainSheet import getMainSheet
from Sheets.Sheet.utils import getSheet

from DataBase import User, getSession
from TelegramBot.telegram_bot import TgBot
from SheetParser.SheetParser import SheetParser

from Announces.AnnounceManager import AnnounceManager

from Announces import Announce
from configs import token, sheet_id

from time import sleep

from threading import Thread
from utils import pasted_date, number_of_week, date_now

from random import randrange, shuffle
from os import path


def main():
    db = getSession()
    tgBot = TgBot(token, db)
    sheepParser = SheetParser(db, tgBot)
    announce = AnnounceManager(tgBot, db)

    Thread(target=sheepParser.run).start()
    Thread(target=tgBot.start_bot).start()
    Thread(target=announce.run).start()


if __name__ == '__main__':
    main()
