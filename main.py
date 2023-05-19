# version 2.0a
# author:koliberskyy(github)
# date: 19.05.23

# x.0 - значительные изменения в порядке работы программы
# 1.x - незначитеьные изменения в поряке работы программы связанные с исправлением ошбок,
# корректировкой входных(выходных) данных
# a(alpha) - версия программы с неподтвержденной работоспособностью
# (возможны ошибки приводящие к генерации необработанных исключений)
# b(beta) - работоспособная версия программы, с нестабильными(не всегда корректными) выходными данными
# s(stable) - стабильно-работоспособная версия программы

import requests
import threading
from threading import Lock
import BTC
import BNB
import ETH
import functions
import telebot
import limit

# bot initialization
file = open("bot.key", 'r')
token = file.readline()
file.close()

bot = telebot.TeleBot(token)
comission = 0.001
chat_id = -1001798375923

message = f"Мы открываем бизнес, мы будем делать бабки.{functions.get_balance('USDT', functions.client)}"
url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
print(requests.get(url).json())  # Эта строка отсылает сообщение

type_of_order = 'LIMIT'
lock = Lock()
if type_of_order == 'MARKET':
    thr1 = threading.Thread(target=functions.doWork, args=(BTC.pair, comission, token, chat_id, lock), daemon=True)
    thr2 = threading.Thread(target=functions.doWork, args=(BNB.pair, comission, token, chat_id, lock), daemon=True)
    thr1.start()
    thr2.start()
    thr1.join()
    thr2.join()

elif type_of_order == 'LIMIT':
    thr1 = threading.Thread(target=limit.do_work, args=(BTC.pair, token, chat_id, lock), daemon=True)
    thr2 = threading.Thread(target=limit.do_work, args=(BNB.pair, token, chat_id, lock), daemon=True)
    thr3 = threading.Thread(target=limit.do_work, args=(ETH.pair, token, chat_id, lock), daemon=True)
    thr1.start()
    thr2.start()
    thr3.start()
    thr1.join()
    thr2.join()
    thr3.join()

message = f"bot finished..."
url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
print(requests.get(url).json())  # Эта строка отсылает сообщение

bot.polling(none_stop=True, interval=0)  # обязательная для работы бота часть
