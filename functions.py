import USDT
import BTC
import BNB
import json
import requests
from threading import Thread, Lock
#левая часть ссылки
refLeft = "https://api.binance.com/api/v3/ticker/price?symbol="

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
    spred *= 1 - (commission * 3)
    return spred

def doWork(pair, comission, token, chat_id, lock:Lock):
    "основная рабочая функция"
    while 1:
        for counter in range(len(pair) - 1):
            spred = get_spred("USDT", pair[0], pair[counter + 1], "USDT", comission)
            if spred > 1:
                #lock.acquire()
                message = f"USDT-{pair[0]}-{pair[counter+1]}-USTD:\n{str(spred)}"
                url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
                print(requests.get(url).json())  # Эта строка отсылает сообщение
                print(str(spred))
                #lock.release()
        print(f"{pair[0]}_DONE!!!!!!!!!!!!!!!!!!!!")
    return 0
#    def Имя(аргументы):
#       "Документация"
  #      Тело(инструкции)
   #     return [значение]