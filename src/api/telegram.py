import requests
from dotenv import load_dotenv
load_dotenv()
import os
import urllib

def send(bot_message):
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    bot_chatID = os.environ['TELEGRAM_BOT_CHAT_ID']
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?parse_mode=HTML&chat_id=' + bot_chatID + '&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def send_stock_newsletter(stocks = ["test"]):
  sorted_stocks = stocks
  html = '';
  for i in range(len(sorted_stocks)):
    stock = sorted_stocks[i]
    html += create_html_for_stock(stock, i)
  return send(encode_html(html))


def create_html_for_stock(stock, i):
  # Telegram Bot API currently supports only <b>, <i>, <a>,<code> and <pre> tags, for HTML parse mode
  html = f'<b>Example momentum-trading-sklearn</b> \n'
  return html

def encode_html(encode_html):
  return urllib.parse.quote_plus(encode_html)
