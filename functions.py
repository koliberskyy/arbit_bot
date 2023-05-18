import time
import requests
from threading import Thread, Lock
from binance.spot import Spot

import main

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

    t_start = time.time()

    #client.user_asset()
    tmp = client.account()
    for counter in range((len(tmp['balances']))):
        if tmp['balances'][counter]['asset'] == pair:
            return float(tmp['balances'][counter]['free'])

    t_end = time.time()
    print("The time of execution of get_balance is :", (t_end - t_start) * 10 ** 3, "ms")

    return 0

def get_price(url):
    "функция получения цены по ссылке"
    #print(f"try to connect:{url}")
    price = requests.get(url)
    #print(f"connection sucsess")
    try:
        price = price.json()
        price = float(price['price'])
    except KeyError:
        price = 1000000.0
    except requests.exceptions.JSONDecodeError:
        price = 1000000.0

    return price

# функция расчета спреда для торговой пары с учетом комиссии
def get_spred(start_token, first_token, second_token, target_token, commission):
    "функция расчета спреда для торговой пары"
    try:
        t_start = time.time()

        spred = 1
        url1 = refLeft + first_token + start_token
        url2 = refLeft + second_token + first_token
        url3 = refLeft + second_token + target_token

        price1 = get_price(url1)
        price2 = get_price(url2)
        price3 = get_price(url3)

        spred /= price1
        spred /= price2
        spred *= price3
    except TimeoutError:
        print(f"timeoutError")
        return 0
    print(f"{start_token}-{first_token}-{second_token}-{target_token}:\t\t{spred}\t\t price chain:{price1, price2, price3}")

    t_end = time.time()
    print("The time of execution of get_spred is :", (t_end - t_start) * 10 ** 3, "ms")

    return spred
def realize_spred(start_token, first_token, second_token, target_token, lock:Lock, balance):
    "функция покупки цепочки"
    lock.acquire()
    print("realise spred")
    t_start = time.time()

    balance = balance
    print(f"balance{start_token}:{balance}")
    balance = order_market(first_token + start_token, balance, 'BUY')

    #balance = get_balance(first_token, client)
    print(f"balance{first_token}:{balance}")
    balance = order_market(second_token + first_token, balance, 'BUY')

    #balance = get_balance(second_token, client)
    print(f"balance{second_token}:{balance}")
    order_market(second_token + target_token, balance, 'SELL')

    t_end = time.time()
    print("\nThe time of execution of realize_spred is :", (t_end - t_start) * 10 ** 3, "ms\n")

    print(f"расчетный баланс:{balance}")
    print(f"donerkebabalance:{get_balance(target_token, client)} \n \n \n")
    lock.release()
    return (t_end - t_start) * 10 ** 3
def order_market(pair, quoteOrderQty, buy_sell):
    "открытие ордера"

    t_start = time.time()

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

    qty = response['fills'][0]['qty']
    commission = response['fills'][0]['commission']
    quoteQty = response['cummulativeQuoteQty']
    price = response['fills'][0]['price']

    if buy_sell == 'SELL':
        result = float(quoteQty) #- float(commission)
    else:
        result = float(quoteQty) / float(price) #- float(commission)
        result -= float(commission) 

    result = round(result, 8)
    print(f"Расчетный баланс:{result}")
    print(f"order:{pair}, qty:{qty}, price{price}, quoteQty:{quoteQty}, commission:{commission}, result(calculated):{result}")

    t_end = time.time()
    print("\nThe time of execution of order_market is :", (t_end - t_start) * 10 ** 3, "ms\n")

    return result
def doWork(pair, comission, token, chat_id, lock:Lock):
    "основная рабочая функция"
    try:
        balance = get_balance('USDT', client)
        print(f"balance usdt:{balance}")
        while 1:
            for counter in range(len(pair) - 1):
                spred = get_spred("USDT", pair[0], pair[counter + 1], "USDT", comission)
                    #лучше даже будет 0.004, изза скачков цены вниз, за время оторое проходит от расчета до покупки спред падае ниже комиссии
                while spred > 1.005:
                    print("realize section here")
                    time_realize = realize_spred("USDT", pair[0], pair[counter + 1], "USDT", lock, balance)
                    message = f"USDT-{pair[0]}-{pair[counter + 1]}-USTD:\n{str(spred)}\n" \
                              f"balance USDT:{get_balance('USDT', client)}\n" \
                              f"balance BTC:{get_balance('BTC', client)}\n" \
                              f"balance BNB:{get_balance('BNB', client)}\n" \
                              f"Время выполнения покупки:{time_realize}"
                    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
                    print(requests.get(url).json())  # Эта строка отсылает сообщение

                    balance = get_balance('USDT', client)
                    spred = get_spred("USDT", pair[0], pair[counter + 1], "USDT", comission)

            print(f"{pair[0]}_DONE!!!!!!!!!!!!!!!!!!!!")

    except requests.exceptions.ConnectTimeout:
        message = f"{pair[0]}-вылетел по интернету"
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
        print(requests.get(url).json())  # Эта строка отсылает сообщение
        

#realize_spred('USDT', 'BTC', 'IDEX', 'USDT', 0.001)


