import requests
import threading
from threading import Lock
import USDT
import BTC
import BNB
import functions
import telebot



#bot initialization
file = open("bot.key", 'r')
token = file.readline()
file.close()

bot = telebot.TeleBot(token)
message = ""
comission = 0.001
chat_id = -1001798375923

message = f"bot starts..."
url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
print(requests.get(url).json())  # Эта строка отсылает сообщение

lock = Lock()
thr1 = threading.Thread(target=functions.doWork, args=(BTC.pair, comission, token, chat_id, lock), daemon=True)
thr2 = threading.Thread(target=functions.doWork, args=(BNB.pair, comission, token, chat_id, lock), daemon=True)
thr1.start()
thr2.start()
thr1.join()
thr2.join()

message = f"bot finished..."
url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
print(requests.get(url).json())  # Эта строка отсылает сообщение

bot.polling(none_stop=True, interval=0)  # обязательная для работы бота часть




