import time
from random import randint
from threading import Thread

import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
  return "alive"

def run():
  app.run(host='0.0.0.0', port=randint(2000, 9000))

def ping(target):
  while True:
    requests.get(target)
    time.sleep(randint(180, 300))

    

def keep_alive(target):
  app_thread = Thread(target=run)
  pinger_thread = Thread(target=ping, args=(target,))
  app_thread.start()
  pinger_thread.start()