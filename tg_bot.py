import telebot
import requests


class TgBot:
    """класс для отправки сообщений в группу тг через бота"""
    def __init__(self, key_filename="bot.key", chat_id=-1001798375923):
        file = open(key_filename, 'r')
        self.__token = file.readline()
        file.close()

        self.__chat_id = chat_id

        self.__bot = telebot.TeleBot(self.__token)

    def send_message(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage?" \
              f"chat_id={self.chat_id}&" \
              f"text={message}"
        print(requests.get(url).json())  # Эта строка отсылает сообщение

    @property
    def token(self):
        """токен бота, его дает bot_father"""
        return self.__token

    @property
    def bot(self):
        """объект бота"""
        return self.__bot

    @property
    def chat_id(self):
        """рабочий чат"""
        return self.__chat_id
