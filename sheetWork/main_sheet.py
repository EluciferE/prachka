import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime
from time import sleep

import gc

from threading import Thread
import logging

from utils import get_time
from typing import Union

from random import randrange

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class MainSheet:
    def __init__(self, service, sheet_id):
        self.service = service
        self.sheet_id = sheet_id

    def change_color(self, range_: str, default_color: bool = False):
        num = int(range_[1:]) - 1
        num_lat = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(range_[0])

        gray = {"red": 0.8, "green": 0.8, "blue": 0.8}
        if default_color:
            gray = {"red": 1, "green": 1, "blue": 1}

        range_ = {
            "sheetId": 0,
            "startRowIndex": num,
            "endRowIndex": num + 1,
            "startColumnIndex": num_lat,
            "endColumnIndex": num_lat + 1
        }

        batch_update_values_request_body = {
            "requests": [
                {
                    "updateCells": {
                        "range": range_,
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredFormat": {
                                            "backgroundColor": gray
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
        color1 = randrange(100, 250)
        color2 = randrange(100, 250)
        color3 = randrange(100, 250)

        color = {"red": color1, "green": color2, "blue": color3}
        border = {"style": "SOLID", "width": 2, "color": color}
        if default_color:
            color = {"red": 0, "green": 0, "blue": 0}
            border = {"style": "SOLID", "width": 1, "color": color}

        body2 = {
            "requests": [
                {
                    "updateBorders": {
                        "range": range_,
                        "top": border,
                        "bottom": border,
                        "right": border,
                        "left": border,
                    },
                },
            ]
        }
        if default_color:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id, body=batch_update_values_request_body).execute()
            sleep(1)
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id, body=body2).execute()
        else:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id, body=body2).execute()
            sleep(1)
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id, body=batch_update_values_request_body).execute()

        sleep(1)

        return 0
