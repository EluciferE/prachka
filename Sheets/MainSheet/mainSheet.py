from Sheets.sheetInterface import SheetInterface
from random import randrange
from Sheets.MainSheet.utils import parseCell

from os.path import exists
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class MainSheet(SheetInterface):
    def __init__(self, service, sheet_id):
        super().__init__(sheet_id)
        self.service = service

    def makeDefault(self, place: str):
        try:
            cellPlaces = self.__getCellPlaces(place)

            color = {"red": 1, "green": 1, "blue": 1}

            request = self.__requestBackground(cellPlaces, color)

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id, body=request).execute()

            color = {"red": 0, "green": 0, "blue": 0}
            border = {"style": "SOLID", "width": 1, "color": color}

            request = self.__requestBorders(cellPlaces, border)
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id, body=request).execute()
            return 0

        except Exception as e:
            self.api_logger.error(f"Error in MainSheet (Make default): {e}")
            return -1

    def changeBorder(self, place: str):
        try:
            color1 = randrange(100, 250)
            color2 = randrange(100, 250)
            color3 = randrange(100, 250)

            color = {"red": color1, "green": color2, "blue": color3}
            border = {"style": "SOLID", "width": 2, "color": color}

            cellPlaces = self.__getCellPlaces(place)

            request = self.__requestBorders(cellPlaces, border)

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id, body=request).execute()
            return 0

        except Exception as e:
            self.api_logger.error(f"Error in MainSheet (changBorder): {e}")
            return -1

    def changeBackground(self, place: str):
        try:
            cellPlaces = self.__getCellPlaces(place)
            color = {"red": 0.8, "green": 0.8, "blue": 0.8}

            request = self.__requestBackground(cellPlaces, color)

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id, body=request).execute()
            return 0

        except Exception as e:
            self.api_logger.error(f"Error in MainSheet (changeBackground): {e}")
            return -1

    @staticmethod
    def __requestBackground(cellPlaces: dict, color: dict) -> dict:
        req = {
            "requests": [
                {
                    "updateCells": {
                        "range": cellPlaces,
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredFormat": {
                                            "backgroundColor": color
                                        }
                                    }
                                ]
                            }
                        ],
                        "fields": "userEnteredFormat.backgroundColor"
                    }
                }
            ]
        }
        return req

    @staticmethod
    def __getCellPlaces(place: dict) -> dict:
        cell = parseCell(place)

        num = int(cell["number"])
        num_lat = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(cell["letter"])

        cellPlaces = {
            "sheetId": 0,
            "startRowIndex": num - 1,
            "endRowIndex": num,
            "startColumnIndex": num_lat,
            "endColumnIndex": num_lat + 1
        }
        return cellPlaces

    @staticmethod
    def __requestBorders(cellPlaces: dict, border: dict) -> dict:
        req = {
            "requests": [
                {
                    "updateBorders": {
                        "range": cellPlaces,
                        "top": border,
                        "bottom": border,
                        "right": border,
                        "left": border,
                    },
                },
            ]
        }
        return req


def getMainSheet(tgBot, sheet_id):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None

    if exists('tokens/mainToken.json'):
        creds = Credentials.from_authorized_user_file('tokens/mainToken.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            tgBot.send_to_admin("У тебя фигня какая-то с токеном")
            exit(-1)

    service = build('sheets', 'v4', credentials=creds)

    return MainSheet(service, sheet_id)
