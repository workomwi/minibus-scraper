import requests

from const import TG_TOKEN, TG_CHAT_ID

def send_tg_message(message: str):
  requests.get(f"https://api.telegram.org/bot{TG_TOKEN}" +
               f"/sendMessage?chat_id={TG_CHAT_ID}&text={message}")