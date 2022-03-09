from Sheets.sheetInterface import SheetInterface
import requests
from .token import Token


class Sheet(SheetInterface):

    def __init__(self, token: Token, sheet_id: str):
        super().__init__(sheet_id)
        self.token = token

    def write(self, value: str, range_: str):
        if "Текущая запись!" not in range_:
            range_ = "Текущая запись!" + range_

        try:
            if not self.token.validate_token():
                self.token.refresh_token()

            url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/{range_}?access_token={self.token.access_token}&valueInputOption=RAW"
            params = {"majorDimension": "ROWS",
                      "range": range_,
                      "values": [[value]]}

            r = requests.put(url, json=params)
            if "error" in r.json():
                raise ValueError(r.text)

            self.api_logger.info(f"[WRITE] {value} -> {range_}")
            return True

        except Exception as e:
            self.api_logger.error(e)
            return False

    def getTable(self):
        range_ = "Текущая запись!A3:J80"
        url = f'https://sheets.googleapis.com/v4/spreadsheets/' + \
              f'{self.sheet_id}/values/{range_}?access_token={self.token.access_token}'

        if not self.token.validate_token():
            self.token.refresh_token()

        r = requests.get(url)
        if r.json().get("values"):
            return r.json().get("values")

        self.api_logger.error(r.text)
        return None
