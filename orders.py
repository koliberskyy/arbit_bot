import time
from threading import Lock
from binance.spot import Spot


class Orders:
    """класс работы для с аккаунтом бинанс"""

    def __init__(self, api_key_filename="api_key.txt", api_secret_filename="api_secret.txt"):
        file = open(api_key_filename, 'r')
        api_key = file.readline()
        file.close()

        file = open(api_secret_filename, 'r')
        api_secret = file.readline()
        file.close()

        self.__client = Spot(api_key=api_key, api_secret=api_secret)

    def buy_buy_sell(self, spred_result, lock:Lock):

        lock.acquire()
        t = time.time()
        balance_before = self.get_balance('USDT')

        self.buy_market(spred_result['coin1'], 'USDT')

        self.buy_market(spred_result['coin2'], spred_result['coin1'])

        print(f"try to post order: {spred_result['coin2']}USDT, SELL, {spred_result['price3']}")
        self.post_order(spred_result['coin2'], 'USDT', 'SELL', spred_result['price3'])
        if self.wait(10):
            print(f"buy_buy_sell denied")
            self.close_orders(spred_result['coin2'] + 'USDT')
            self.sell_market(spred_result['coin2'], 'USDT')

        balance_after = self.get_balance('USDT')
        result = {
            'balance_before': balance_before,
            'balance_after': balance_after,
            'profit': balance_after - balance_before,
            'profit_percent': (balance_after - balance_before) / balance_before,
            'spred': spred_result['spred'],
            'coin_chain': f"USDT-{spred_result['coin1']}-{spred_result['coin2']}-USDT",
            'exec_time': f"{(time.time() - t) * 10 ** 3}ms",
            'spred_result': spred_result
        }

        print(f"buy_buy_sell({spred_result}) = {result}")
        lock.release()
        return result

    def wait(self, sec):
        for i in range(sec):
            time.sleep(1)
            print(f"waiting...")
            if self.is_orders_opened() == 0:
                return 0
        return 1

    def buy_sell_sell(self, spred_result, lock:Lock):

        lock.acquire()
        t = time.time()
        balance_before = self.get_balance('USDT')

        print(f"try to post order: {spred_result['coin1']}USDT, BUY, {spred_result['price1']}")
        self.post_order(spred_result['coin1'], 'USDT', 'BUY', spred_result['price1'])
        if self.wait(1):
            print(f"buy_sell_sell denied")
            self.close_orders(spred_result['coin1'] + 'USDT')
            lock.release()
            return 1

        self.sell_market(spred_result['coin1'], spred_result['coin2'])

        self.sell_market(spred_result['coin2'], 'USDT')

        balance_after = self.get_balance('USDT')
        result = {
            'balance_before': balance_before,
            'balance_after': balance_after,
            'profit': balance_after - balance_before,
            'profit_percent': (balance_after - balance_before) / balance_before,
            'spred': spred_result['spred'],
            'coin_chain': f"USDT-{spred_result['coin1']}-{spred_result['coin2']}-USDT",
            'exec_time': f"{(time.time() - t) * 10 ** 3}ms",
            'spred_result': spred_result
        }

        print(f"buy_buy_sell({spred_result}) = {result}")
        lock.release()
        return result

    def close_orders(self, pair):
        self.client.cancel_open_orders(pair)

    def sell_market(self, coin2, coin1):
        qty = f"{self.fix_min_notional(self.get_balance(coin2), coin2 + coin1):.8f}"
        params = {

            'type': 'MARKET',
            'symbol': coin2 + coin1,
            'side': 'SELL',
            'quantity': qty
        }
        result = self.client.new_order(**params)
        print(f"sell_market({coin2}, {coin1}) = {result}")

    def buy_market(self, coin2, coin1):
        params = {
            'type': 'MARKET',
            'symbol': coin2 + coin1,
            'side': 'BUY',
            'quoteOrderQty': self.get_balance(coin1)
        }
        result = self.client.new_order(**params)
        print(f"sell_market({coin2}, {coin1}) = {result}")

    def is_orders_opened(self):
        if len(self.client.get_open_orders()) == 0:
            return 0
        return 1

    def post_order(self, coin2, coin1, side, price):
        qty = self.get_qty(coin2, coin1, side, price)
        params = {
            'type': 'LIMIT',
            'symbol': coin2 + coin1,
            'side': side,
            'price': f"{price:.8f}",
            'timeInForce': 'GTC',
            'quantity': qty
        }
        response = self.client.new_order(**params)
        print(f"orders.post_order({coin2}, {coin1}, {side}, {price:.8f}) "
              f"qty = {qty}) = {response}")

        return response

    def get_qty(self, coin2, coin1, side, price):
        if side == 'BUY':
            qty = self.get_balance(coin1)
            qty /= price
        else:
            qty = self.get_balance(coin2)
        qty = self.fix_min_notional(qty, coin2 + coin1)
        print(f"orders.get_qty({coin2}, {coin1}, {side}, {price})"
              f"= {qty:.8f}")
        return f"{qty:.8f}"

    def get_balance(self, coin):
        tmp = self.client.account()
        for counter in range((len(tmp['balances']))):
            if tmp['balances'][counter]['asset'] == coin:
                print(f"orders.get_balance({coin})={float(tmp['balances'][counter]['free'])}")
                if tmp['balances'][counter]['free'] > tmp['balances'][counter]['locked']:
                    return float(tmp['balances'][counter]['free'])
                else:
                    return float(tmp['balances'][counter]['locked'])
        print(f"orders.get_balance({coin})=0")
        return 0

    def fix_min_notional(self, value, pair):
        min_qty = self.client.exchange_info(pair)
        min_qty = min_qty['symbols'][0]['filters'][1]['minQty']
        count = 0
        qty = float(min_qty)
        if float(min_qty) > 0.1:
            rounded = round(value, 0)
        else:
            while qty < 1:
                qty *= 10
                count += 1
            rounded = round(value, count)

        if rounded > value:
            rounded -= float(min_qty)
            rounded = round(rounded, 8)

        print(f"orders.fix_min_notional({value}, {pair})={rounded}, minQty = {min_qty}")

        return rounded

    @property
    def client(self):
        return self.__client
