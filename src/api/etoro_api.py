

import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import pandas as pd
import datetime
import requests
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

headers = {
'authority': 'api.etorostatic.com',
'pragma': 'no-cache',
'cache-control': 'no-cache',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
'accept': '*/*',
'origin': 'https://www.etoro.com',
'sec-fetch-site': 'cross-site',
'sec-fetch-mode': 'cors',
'sec-fetch-dest': 'empty',
'referer': 'https://www.etoro.com/discover/markets/stocks/exchange/frankfurt?sort=SymbolFull',
'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
}

class EtoroApi:
  '''This class analysis a stock and makes a recommendation
  for buying it
  '''

  def get_data(self):
    headers = {
    'authority': 'api.etorostatic.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
    'accept': '*/*',
    'origin': 'https://www.etoro.com',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.etoro.com/discover/markets/stocks/exchange/frankfurt?sort=SymbolFull',
    'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    params = (
        ('cv', 'f533225eb8edff28f28f448b15f55486_ccf1dd923418a7527712207498d5c0d9'),
    )
    response = requests.get('https://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments', headers=headers, params=params)

    if (response.status_code == 200):
        data = json.loads(response.text)["InstrumentDisplayDatas"]
        data = pd.DataFrame(data)
        return data


  def get_stocks(self, get_all = False):
    stocks = self.get_data()
    # InstrumentTypeID: 6 => Germany; 4 => US
    stocks = stocks[(stocks["ExchangeID"] == 6) | (stocks["ExchangeID"] == 4) ]
    stocks = stocks[['InstrumentID', 'InstrumentDisplayName', 'InstrumentTypeID', 'ExchangeID', 'SymbolFull']]

    # Only take stocks, where market is open
    if not get_all:
      stocks = stocks[stocks.apply(lambda x: self.is_market_open(x['ExchangeID']), axis=1)]

    return stocks

  def get_instrument_id(self, symbol):
    try:
      df = self.get_stocks(get_all = True).copy()
      symbol = df[df['SymbolFull'].str.contains(symbol)]['InstrumentID']
      return symbol.values[0]
    except:
      return False

  # We stop one hour before market close so that all orders get closed until market close
  def is_market_open(self, exchange_id):
    # We start 2 minutes after market starts to avoid bad buys
    wait_after_market_started = 5
    # Monday is 0 and Sunday is 6
    weekday = datetime.today().weekday()
    if (weekday >= 5):
      return False
    exchange_id = int(exchange_id)
    now = datetime.now()
    # German market with exchangeId 6 starts at: 9:00 and closes at 17:30
    if (exchange_id == 6):
        if (now.hour == 16):
            return (now.minute <= 30)
        if (now.hour == 9):
          # 5 Minutes after market opens
          return (now.minute > wait_after_market_started)
        return (now.hour >= 10) and (now.hour < 16)
    # US market with exchangeId 4 starts at: 15:30 and closes at 22:00
    if (exchange_id == 4):
        if (now.hour == 15):
            # 5 Minutes after market opens
            return (now.minute > (30 + wait_after_market_started))
        return (now.hour >= 15) and (now.hour < 21)
    return False
  # Interval: 'OneMinute' | 'FiveMinutes' | 'TenMinutes' | 'OneHour'
  def get_stock_data(self, instrument_id, rows=100, interval="TenMinutes"):

    params = (
        ('client_request_id', '0c244813-c1eb-4b2f-b279-9898684c3b4f'),
    )

    response = requests.get(f'https://candle.etoro.com/candles/asc.json/{interval}/{rows}/{instrument_id}', headers=headers, params=params)

    if (response.status_code == 200):
        data = json.loads(response.text)["Candles"][0]["Candles"]
        stock_data = pd.DataFrame(data)
        if (not len(stock_data)):
          return None
        # We need a rowIndex to calculate the simple moving averages (sma)
        stock_data['rowIndex'] = stock_data.apply(lambda row: row.name, axis=1)
        return stock_data[["rowIndex","FromDate", "Close"]]
    print(f'Request for instrument_id: {instrument_id} failed with status code: {response.status_code}')

  def get_last_price(self, instrument_id, interval="OneMinute"):

    params = (
        ('client_request_id', '0c244813-c1eb-4b2f-b279-9898684c3b4f'),
    )

    response = requests.get(f'https://candle.etoro.com/candles/asc.json/{interval}/1/{instrument_id}', headers=headers, params=params)

    if (response.status_code == 200):
        data = json.loads(response.text)["Candles"][0]
        return { "range_open": data["RangeOpen"], "range_close": data["RangeClose"]}
    print(f'Request for instrument_id: {instrument_id} failed with status code: {response.status_code}')

  def is_any_market_open(self):
    return self.is_market_open(4) or self.is_market_open(6)