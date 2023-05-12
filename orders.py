from binance.spot import Spot
import requests

client = Spot()
# Get server timestamp
print(client.time())

def get_balance(token, client):
    "функция получения цены по ссылке"
    tmp = client.account()
    for counter in range((len(tmp['balances']))):
        if tmp['balances'][counter]['asset'] == token:
            return float(tmp['balances'][counter]['free'])
    return 0



file = open("api_key.txt", 'r')
api_key = file.readline()
print(api_key)
file.close()

file = open("api_secret.txt", 'r')
api_secret = file.readline()
print(api_secret)
file.close()

# API key/secret are required for user data endpoints
client = Spot(api_key=api_key, api_secret=api_secret)

# Get account and balance information
#print(client.account())

acc = client.account()

print(f"balance:{acc['balances'][0]['free']}")
print(f"func:{get_balance('BTC', client)}")

# вытащить баланс
# Post a new order
params = {
    'symbol': 'BTCUSDT',
    'side': 'BUY',
    'type': 'LIMIT',
    'timeInForce': 'IOC',
    'quantity': 0.00090,
    'price': 25000
}
#response = client.new_order(**params)
#print(response)