import time
import requests
import functions
from threading import Lock
from binance.spot import Spot

# инициализация аккаунта(ключей)
file = open("api_key.txt", 'r')
api_key = file.readline()
print(api_key)
file.close()

file = open("api_secret.txt", 'r')
api_secret = file.readline()
print(api_secret)
file.close()

client = Spot(api_key=api_key, api_secret=api_secret)


def get_spred(start_token, first_token, second_token, target_token):
    """функция расчета спреда для торговой пары"""
    try:
        t_start = time.time()

        spred = 1
        url1 = functions.refLeft + first_token + start_token
        url2 = functions.refLeft + second_token + first_token
        url3 = functions.refLeft + second_token + target_token

        price1 = functions.get_price(url1)
        price2 = functions.get_price(url2)
        price3 = functions.get_price(url3)

        t_end = time.time()

        spred /= price1
        spred /= price2
        spred *= price3
    except TimeoutError:
        print(f"timeoutError")
        return 0

    print("The time of execution of get_spred is :", (t_end - t_start) * 10 ** 3, "ms")

    price_chain = {
        first_token + start_token: price1,
        second_token + first_token: price2,
        second_token + target_token: price3,
        'spred': spred
    }
    print(price_chain)
    return price_chain


def order_limit(pair, qty, buy_sell, price_chain):
    """открытие лимитного ордера"""

    t_start = time.time()

    if buy_sell == 'SELL':
        min_qty = client.exchange_info(pair)
        min_qty = min_qty['symbols'][0]['filters'][1]['minQty']
        count = 0
        qty = float(min_qty)
        if float(min_qty) > 0.1:
            rounded = round(qty, 0)
        else:
            while qty < 1:
                qty *= 10
                count += 1
            rounded = round(qty, count)

        if rounded > qty:
            rounded -= float(min_qty)
            rounded = round(rounded, 8)

        qty = rounded
        params = {
            'symbol': pair,
            'side': buy_sell,
            'quantity': qty,
            'price': price_chain[pair],
            'type': 'LIMIT',
            'timeInForce': 'IOC'
        }
        print(f"qty (order_market):{params['quantity']}")

        t_end_sell = time.time()
        print("\nThe time of SELL SECTION :", (t_end_sell - t_start) * 10 ** 3, "ms\n")
    else:
        params = {
            'symbol': pair,
            'side': buy_sell,
            'quoteOrderQty': qty,
            'price': price_chain[pair],
            'type': 'LIMIT',
            'timeInForce': 'IOC'
        }
        print(f"quoteOrderQty (order_market):{params['quoteOrderQty']}")
    response = client.new_order(**params)

    qty = response['fills'][0]['qty']
    commission = response['fills'][0]['commission']
    quote_qty = response['cummulativeQuoteQty']
    price = response['fills'][0]['price']

    if buy_sell == 'SELL':
        result = float(quote_qty)  # - float(commission)
    else:
        result = float(quote_qty) / float(price)  # - float(commission)

    result = round(result, 8)
    print(f"Расчетный баланс:{result}")
    print(f"order:{pair}, qty:{qty}, price{price}, quoteQty:{quote_qty}, commission:{commission}")

    t_end = time.time()
    print("\nThe time of execution of order_limit is :", (t_end - t_start) * 10 ** 3, "ms\n")

    return result


def realize_spred(start_token, first_token, second_token, target_token, lock: Lock, balance, price_chain):
    """функция покупки цепочки"""
    lock.acquire()
    print("realise spred")
    t_start = time.time()

    balance = balance
    print(f"balance{start_token}:{balance}")
    balance = order_limit(first_token + start_token, balance, 'BUY', price_chain)

    # balance = get_balance(first_token, client)
    print(f"balance{first_token}:{balance}")
    balance = order_limit(second_token + first_token, balance, 'BUY', price_chain)

    # balance = get_balance(second_token, client)
    print(f"balance{second_token}:{balance}")
    order_limit(second_token + target_token, balance, 'SELL', price_chain)

    t_end = time.time()
    print("\nThe time of execution of realize_spred is :", (t_end - t_start) * 10 ** 3, "ms\n")

    print(f"расчетный баланс:{balance}")
    print(f"donerkebabalance:{functions.get_balance(target_token, client)} \n \n \n")
    lock.release()
    return (t_end - t_start) * 10 ** 3


def do_work(pair, token, chat_id, lock: Lock):
    """основная рабочая функция"""
    try:
        balance = functions.get_balance('USDT', client)
        print(f"balance usdt:{balance}")
        while 1:
            for counter in range(len(pair) - 1):
                price_chain = get_spred("USDT", pair[0], pair[counter + 1], "USDT")
                while price_chain['spred'] > 1.005:
                    print("realize section here")
                    time_realize = realize_spred("USDT", pair[0], pair[counter + 1], "USDT", lock, balance, price_chain)
                    message = f"USDT-{pair[0]}-{pair[counter + 1]}-USTD:\n{str(price_chain['spred'])}\n" \
                              f"balance USDT:{functions.get_balance('USDT', client)}\n" \
                              f"balance BTC:{functions.get_balance('BTC', client)}\n" \
                              f"balance BNB:{functions.get_balance('BNB', client)}\n" \
                              f"Время выполнения покупки:{time_realize}"
                    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
                    print(requests.get(url).json())  # Эта строка отсылает сообщение

                    balance = functions.get_balance('USDT', client)
                    price_chain = get_spred("USDT", pair[0], pair[counter + 1], "USDT")

            print(f"{pair[0]}_DONE!!!!!!!!!!!!!!!!!!!!")

    except requests.exceptions.ConnectTimeout:
        message = f"{pair[0]}-вылетел по интернету"
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
        print(requests.get(url).json())  # Эта строка отсылает сообщение
        # ВНИМАНИЕ МОЖЕТ СЛОМАТЬ ПРОГРАММУ#################################################################
        do_work(pair, token, chat_id, lock)
