import time

import USDT
import BTC
import BNB
import json
import requests
from threading import Thread, Lock
from binance.spot import Spot
import math
file = open("api_key.txt", 'r')
api_key = file.readline()
print(api_key)
file.close()

file = open("api_secret.txt", 'r')
api_secret = file.readline()
print(api_secret)
file.close()

client = Spot(api_key=api_key, api_secret=api_secret)

#quotePrecision = client.exchange_info('DOGEUSDT')
#print(quotePrecision)
#hui = quotePrecision['symbols'][0]['filters'][1]['minQty']
#hui2 = quotePrecision['symbols'][0]['filters'][0]['minPrice']
#print(hui)
#print(hui2)

#левая часть ссылки
refLeft = "https://api.binance.com/api/v3/ticker/price?symbol="
def fix_balance(balance, pair):
    "вычитаем из баланса минимальную сумму сделки"
    quotePrecision = client.exchange_info(pair)
    quotePrecision = quotePrecision['symbols'][1][1][1]
    print(f"quotePrecision:{quotePrecision}")
    round(balance, quotePrecision)
    print(f"fixed_balance:{balance}")
    return balance
def get_balance(pair, client):
    "функция получения цены по ссылке"
    tmp = client.account()
    for counter in range((len(tmp['balances']))):
        if tmp['balances'][counter]['asset'] == pair:
            return float(tmp['balances'][counter]['free'])
    return 0

def get_price(url):
    "функция получения цены по ссылке"
    price = requests.get(url)
    price = price.json()
    return float(price['price'])

# функция расчета спреда для торговой пары с учетом комиссии
def get_spred(start_token, first_token, second_token, target_token, commission):
    "функция расчета спреда для торговой пары"

    spred = 1
    url1 = refLeft + first_token + start_token
    print(url1)
    url2 = refLeft + second_token + first_token
    print(url2)
    url3 = refLeft + second_token + target_token
    print(url3)

    spred /= get_price(url1)
    spred /= get_price(url2)
    spred *= get_price(url3)
    spred *= 1 - (commission * 3)#возможна ошибка изза расчета комиссии в долларах, возможно нужно считать в токенах
    return spred
def realize_spred(start_token, first_token, second_token, target_token, commission):
    "функция покупки цепочки"
    balance = get_balance(start_token, client)
    print(f"balance{start_token}:{balance}")
    url = refLeft + first_token + start_token

    balance = order_market(first_token + start_token, balance, 'BUY')
    balance = get_balance(first_token, client)
    print(f"balance{first_token}:{balance}")
    url = refLeft + second_token + first_token

    balance = order_market(second_token + first_token, balance, 'BUY')
    balance = get_balance(second_token, client)
    print(f"balance{second_token}:{balance}")
    url = refLeft + second_token + target_token

    balance = order_market(second_token + target_token, balance, 'SELL')

    print(f"donerkebabalance:{get_balance(target_token, client)} \n \n \n")
    return balance
def order_market(pair, quoteOrderQty, buy_sell):
    "открытие ордера"
    #quantity = round(quantity, 5)
    #quantity = float("{0:.00001f}".format(quantity))
   # btcusdt
   # bal = usdt
   # adabtc
   # bal=btc
   # adausdt
   # bal = ada
    #сомневаюсь что на бай нужна такая процедура
    if buy_sell == 'SELL':
        rounded = 0
        minQty = client.exchange_info(pair)
        minQty = minQty['symbols'][0]['filters'][1]['minQty']
        count = 0
        qty = float(minQty)
        if float(minQty) > 0.1:
            rounded = round(quoteOrderQty, 0)
        else:
            while qty < 1:
                qty *= 10
                count += 1
            rounded = round(quoteOrderQty, count)

        if (rounded > quoteOrderQty):
            rounded -= float(minQty)
            rounded = round(rounded, 8)

        quoteOrderQty = rounded
        params = {
            'symbol': pair,
            'side': buy_sell,
            'type': 'MARKET',
            'quantity': quoteOrderQty
        }
        print(f"quoteOrderQty (order_market):{params['quantity']}")
    else:
        params = {
            'symbol': pair,
            'side': buy_sell,
            'type': 'MARKET',
            'quoteOrderQty': quoteOrderQty
        }
        print(f"quoteOrderQty (order_market):{params['quoteOrderQty']}")
    response = client.new_order(**params)
    return float(response['executedQty'])
def doWork(pair, comission, token, chat_id, lock:Lock):
    "основная рабочая функция"
    while 1:
        for counter in range(len(pair) - 1):
            spred = get_spred("USDT", pair[0], pair[counter + 1], "USDT", comission)
            print(str(spred))
            if spred > 1.0001:
                lock.acquire()
                message = f"USDT-{pair[0]}-{pair[counter+1]}-USTD:\n{str(spred)}"
                url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
                print(requests.get(url).json())  # Эта строка отсылает сообщение
                print(str(spred))
                realize_spred("USDT", pair[0], pair[counter + 1], "USDT", comission)
                lock.release()

                message = f"balance USDT:{get_balance('USDT', client)}"
                url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
                print(requests.get(url).json())  # Эта строка отсылает сообщение

        print(f"{pair[0]}_DONE!!!!!!!!!!!!!!!!!!!!")
    return 0
#    def Имя(аргументы):
#       "Документация"
  #      Тело(инструкции)
   #     return [значение]