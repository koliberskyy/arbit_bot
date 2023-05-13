import USDT
import BTC
import BNB
import json
import requests
from threading import Thread, Lock
from binance.spot import Spot

file = open("api_key.txt", 'r')
api_key = file.readline()
print(api_key)
file.close()

file = open("api_secret.txt", 'r')
api_secret = file.readline()
print(api_secret)
file.close()

client = Spot(api_key=api_key, api_secret=api_secret)

#левая часть ссылки
refLeft = "https://api.binance.com/api/v3/ticker/price?symbol="

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
    quantity = balance/get_price(url)
    quantity *= 0.99
    print(f"quantity{first_token}:{quantity}")

    balance = order_market(first_token + start_token, quantity, 'BUY') * commission
    print(f"balance{first_token}:{balance}")
    url = refLeft + second_token + first_token
    quantity = balance/get_price(url)
    quantity *= 0.99
    print(f"quantity{second_token}:{quantity}")

    balance = order_market(second_token + first_token, quantity, 'BUY') * commission #73.42
    print(f"balance{second_token}:{balance}")
    url = refLeft + second_token + target_token #0.364
    quantity = get_price(url) * balance
    quantity *= 0.99
    print(f"quantity{target_token}:{quantity}")

    balance = order_market(second_token + target_token, quantity, 'SELL') * commission
    print(f"balance{target_token}:{balance}")

    return balance
def order_market(pair, quantity, buy_sell):
    "открытие ордера"
    quantity = round(quantity, 5)
    params = {
        'symbol': pair,
        'side': buy_sell,
        'type': 'MARKET',
        'quantity': quantity,
    }
    response = client.new_order(**params)
    return float(response['executedOty'])
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
                print("donerkebab \n \n \n")
                lock.release()
        print(f"{pair[0]}_DONE!!!!!!!!!!!!!!!!!!!!")
    return 0
#    def Имя(аргументы):
#       "Документация"
  #      Тело(инструкции)
   #     return [значение]