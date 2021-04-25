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

def send_stock_newsletter(stock_predictions = []):
  html = '';
  for i in range(len(stock_predictions)):
    stock = stock_predictions[i]
    html += create_html_for_stock(stock, i)
  return send(encode_html(html))


def create_html_for_stock(stock_prediction, i):
  # Telegram Bot API currently supports only <b>, <i>, <a>,<code> and <pre> tags, for HTML parse mode
  html = f'<b>{i+1}. <a href="https://www.etoro.com/markets/{stock_prediction["symbol"]}">{stock_prediction["name"]}</a></b> | {stock_prediction["symbol"]} | <pre>{stock_prediction["proba"]}</pre> % \n \n'
  return html

def encode_html(encode_html):
  return urllib.parse.quote_plus(encode_html)
