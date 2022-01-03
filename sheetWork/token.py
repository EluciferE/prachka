import requests
import json
from configs.config import client_secret

from typing import Union


class Token:
    def __init__(self, username: str,
                 path_to_token: str = None, json_token: Union[str, dict] = None):
        self.token = None
        self.username = username

        with open(client_secret, "r") as client_data:
            data = client_data.read()
            self.client_data = json.loads(data)

        if path_to_token is not None:
            self._read_from_file(path_to_token)

        elif json_token is not None:
            if isinstance(json_token, type(str)):
                self.token = json.load(json_token)
            elif isinstance(json_token, type(dict)):
                self.token = json_token

    def _read_from_file(self, path):
        with open(path, "r") as file:
            self.token = json.loads(file.read())

    def refresh_token(self):
        params = {"client_id": self.client_data["installed"]["client_id"],
                  "client_secret": self.client_data["installed"]["client_secret"],
                  "refresh_token": self.token["refresh_token"],
                  "grant_type": "refresh_token"}

        r = requests.post("https://oauth2.googleapis.com/token", data=params)
        print("DEBUG:: REFRESH::", r.text)
        if not "error" in r.text:
            with open(f"tokens/{self.username}.json", "w") as file:
                file.write(json.dumps(r.json()))

    def access_token(self):
        return self.token["access_token"]
