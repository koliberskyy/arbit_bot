# version 3.0b
# author:koliberskyy(github)
# date: 22.05.23

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
import coins
from tg_bot import TgBot

import spred
from orders import Orders

orders_obj = Orders()
tg_bot = TgBot()


def do_bbs(coins, lock:Lock):
    try:
        while 1:
            for it in range(len(coins) - 1):
                if lock.locked() != True:
                    spred_result = spred.get_spred_bbs(coins[0], coins[it + 1])
                    while spred_result['spred'] > 1.005:
                        bbs_result = orders_obj.buy_buy_sell(spred_result, lock)
                        tg_bot.send_message(bbs_result)
                        spred_result = spred.get_spred_bbs(coins[0], coins[it + 1])
    except requests.exceptions.ConnectTimeout:
        do_bbs(coins, lock)


def do_bss(coins, lock:Lock):
    try:
        while 1:
            for it in range(len(coins) - 1):
                if lock.locked() != True:
                    spred_result = spred.get_spred_bss(coins[it + 1], coins[0])
                    while spred_result['spred'] > 1.005:
                        bss_result = orders_obj.buy_sell_sell(spred_result, lock)
                        tg_bot.send_message(bss_result)
                        spred_result = spred.get_spred_bbs(coins[it + 1], coins[0])
    except requests.exceptions.ConnectTimeout:
        do_bbs(coins, lock)


lock = Lock()

#BBS red
#BSS green

trigger = 'BBS'

if trigger == 'BBS':
    thr1 = threading.Thread(target=do_bbs, args=(coins.BTC, lock), daemon=True)
    thr2 = threading.Thread(target=do_bbs, args=(coins.BNB, lock), daemon=True)
    thr3 = threading.Thread(target=do_bbs, args=(coins.ETH, lock), daemon=True)
    thr1.start()
    thr2.start()
    thr3.start()
    thr1.join()
    thr2.join()
    thr3.join()
else:
    thr1 = threading.Thread(target=do_bss, args=(coins.BTC, lock), daemon=True)
    thr2 = threading.Thread(target=do_bss, args=(coins.BNB, lock), daemon=True)
    thr3 = threading.Thread(target=do_bss, args=(coins.ETH, lock), daemon=True)
    thr1.start()
    thr2.start()
    thr3.start()
    thr1.join()
    thr2.join()
    thr3.join()


