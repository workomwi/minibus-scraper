import os

import requests

TG_TOKEN = os.getenv('TG_TOKEN')
TG_LOGGER_TOKEN = os.getenv('TG_LOGGER_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def tg_notify(message: str):
  requests.get(f"https://api.telegram.org/bot{TG_TOKEN}" +
               f"/sendMessage?chat_id={TG_CHAT_ID}&text={message}")


def tg_log(log: str):
 requests.get(f"https://api.telegram.org/bot{TG_LOGGER_TOKEN}" +
               f"/sendMessage?chat_id={TG_CHAT_ID}&text={log}")
  