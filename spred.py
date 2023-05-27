import requests

def get_price(symbol):
    "функция получения цены по ссылке"
    ref_left = "https://api.binance.com/api/v3/ticker/price?symbol="
    url = ref_left + symbol
    price = requests.get(url)
    try:
        price = price.json()
        price = float(price['price'])
    except KeyError:
        price = 1000000.0
    except requests.exceptions.JSONDecodeError:
        price = 1000000.0

    return price


def get_spred_bbs(coin1, coin2):
    """функция расчета спреда для торговой пары buy buy sell"""
    try:
        spred = 1

        price1 = get_price(coin1 + 'USDT')
        price2 = get_price(coin2 + coin1)
        price3 = get_price(coin2 + 'USDT')

        spred /= price1
        spred /= price2
        spred *= price3
    except TimeoutError:
        print(f"timeoutError")
        return 0

    result = {
        'price1': price1,
        'price2': price2,
        'price3': price3,
        'spred': spred,
        'coin1': coin1,
        'coin2': coin2
    }

    print (f"get_spred({coin1}, {coin2}= \t{result}")
    return result


def get_spred_bss(coin1, coin2):
    """функция расчета спреда для торговой пары buy sell sell [usdt ada btc usdt]"""
    try:
        spred = 1

        price1 = get_price(coin1 + 'USDT')
        price2 = get_price(coin1 + coin2)
        price3 = get_price(coin2 + 'USDT')

        spred *= price1
        spred /= price2
        spred /= price3
    except TimeoutError:
        print(f"timeoutError")
        return 0

    result = {
        'price1': price1,
        'price2': price2,
        'price3': price3,
        'spred': spred,
        'coin1': coin1,
        'coin2': coin2
    }

    print (f"get_spred({coin1}, {coin2}= \t{result}")
    return result
