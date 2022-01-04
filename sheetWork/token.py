import requests
import json
from configs.config import client_secret

import logging
from typing import Union

FORMAT = '[%(asctime)s] - [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO)
tokens_logs = logging.FileHandler('logs/tokens.log')
tokens_logs.setFormatter(logging.Formatter(FORMAT))

tokens_logger = logging.getLogger('token')
tokens_logger.addHandler(tokens_logs)
tokens_logger.propagate = False


class Token:
    def __init__(self, username: str,
                 path_to_token: str = None, json_token: Union[str, dict] = None):
        self._token = None
        self._username = username

        with open(client_secret, "r") as client_data:
            data = client_data.read()
            self.client_data = json.loads(data)

        if path_to_token is not None:
            self._read_from_file(path_to_token)

        elif json_token is not None:
            if isinstance(json_token, type(str)):
                self._token = json.load(json_token)
            elif isinstance(json_token, type(dict)):
                self._token = json_token

    def _read_from_file(self, path):
        with open(path, "r") as file:
            self._token = json.loads(file.read())

    def refresh_token(self):
        params = {"client_id": self.client_data["installed"]["client_id"],
                  "client_secret": self.client_data["installed"]["client_secret"],
                  "refresh_token": self._token["refresh_token"],
                  "grant_type": "refresh_token"}

        r = requests.post("https://oauth2.googleapis.com/token", data=params)
        if "error" not in r.text:
            tokens_logger.info(f"Success refresh token by {self._username}")
            token_json = r.json()
            token_json["refresh_token"] = self._token["refresh_token"]
            self._token = token_json
            with open(f"tokens/{self._username}.json", "w") as file:
                file.write(json.dumps(token_json))
            return 0
        else:
            tokens_logger.error(f"Refresh token by {self._username}: {r.text}")
            return -1

    def validate_token(self):
        url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={self.access_token()}"
        r = requests.get(url)
        if r.json().get("error"):
            tokens_logger.info(f"Bad validate of token by {self._username}")
            return False
        return True
    #TODO Make property
    def access_token(self):
        return self._token["access_token"]

    def token(self):
        return self._token
