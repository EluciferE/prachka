from abc import ABC, abstractmethod
import logging


class SheetInterface(ABC):

    def __init__(self, sheet_id: str):
        FORMAT = '[%(asctime)s] - [%(levelname)s] - %(message)s'
        logging.basicConfig(level=logging.INFO)
        api_logs = logging.FileHandler('logs/sheets.log')
        api_logs.setFormatter(logging.Formatter(FORMAT))

        self.api_logger = logging.getLogger('api')
        self.api_logger.addHandler(api_logs)
        self.api_logger.propagate = False

        self.sheet_id = sheet_id

    def write(self, value: str, place: str) -> bool:
        """
        Write into place in GoogleSheet
        If raise some error log it
        :param value: any string, mostly like <name>, <room>
        :param place: Optional("Текущая запись!")<letter><number>
        :return: True if write successful, False else
        """
        pass
