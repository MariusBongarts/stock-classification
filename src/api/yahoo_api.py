import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import pandas as pd
import requests
import json
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
from datetime import datetime
import time

class YahooApi:
  '''This class gets data from the yahoo api and maps the data to the same as etoro´s api
  '''

  def get_stock_data(self, symbol, periods=7, frequency=1, take_profit=1.015, intervals_to_profit=30, period_type=share.PERIOD_TYPE_DAY, frequency_type=share.FREQUENCY_TYPE_MINUTE):
    my_share = share.Share(symbol)
    try:
      symbol_data = my_share.get_historical(period_type,
                                          periods,
                                          frequency_type,
                                          frequency)
    except YahooFinanceError as e:
      print(e)
      return

    df = pd.DataFrame(symbol_data)

    # Returns empty dataframe when there is no data
    if (not len(df)):
      return df

    # Rename `close` column to `Close` and round the value
    df['Close'] = round(df['close'],2)
    df = df.dropna(axis=0, how='any')

    # We need a rowIndex to calculate the simple moving averages (sma)
    df['rowIndex'] = df.apply(lambda row: row.name, axis=1)

    # Returns true, when `Close` goes up `take_profit` % in the next `intervals_to_profit` minutes and no value is under stop_loss
    # Adds 2 intervalls to rowIndex because we skip the next interval because we probably miss it in live-action
    df["profit"] = df.apply(lambda x:
    (x["volume"] > 0) &
    ((df.loc[x["rowIndex"] + 2:(x["rowIndex"] + intervals_to_profit)]["Close"] > x["Close"] * take_profit).any()) &
    (not ((df.loc[x["rowIndex"]:(x["rowIndex"] + intervals_to_profit)]["Close"] < x["Close"] * (1 - (take_profit - 1))).any()))
    if True else False, axis=1)

    return df[["rowIndex", "Close", "profit", "timestamp"]]

  def get_most_active_stocks(self):
    headers = {
      'authority': 'query1.finance.yahoo.com',
      'pragma': 'no-cache',
      'cache-control': 'no-cache',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
      'content-type': 'application/json',
      'accept': '*/*',
      'origin': 'https://finance.yahoo.com',
      'sec-fetch-site': 'same-site',
      'sec-fetch-mode': 'cors',
      'sec-fetch-dest': 'empty',
      'referer': 'https://finance.yahoo.com/most-active/?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAABPislZoWpkYqU927PDM0mo-C_pxKK5COO4O9U5ZP9u1fSFIVfLxn184EWrBM7lIF_nsQZcvZK8FBRXcrgZNoZDObMUjmAD6xVlHL5tTnaXEHg7nhUEZDfNEgL-LUnBnQAREcH-_Ccl5XOoivla-e3i_GpTmDd1RT31IrprDWRvT',
      'accept-language': 'en,en-US;q=0.9,de;q=0.8',
      'cookie': 'APID=UP5b8cc8cc-f753-11e9-9ca2-02387f2d3434; B=12mu1e5er6et4&b=3&s=an; GUCS=AU9RiFxR; EuConsent=CO65zs4O65zs4AOACBENA3CoAP_AAH_AACiQGYtf_X_fb2vj-_599_t0eY1f9_63v-wzjgeNs-8Nyd_X_L4Xv2MyvB36pq4KuR4ku3bBAQdtHOncTQmRwIlVqTLsbk2Mq7NKJ7LEilsbe2dYGH9vn8XT-ZKZ70_sf__7_3______774GXkEmGpfAQJCWMBJNmlUKIEIVxIVAOACihGFo0sNCVwU7K4CPUECABAagIwIgQYgoxZBAAAAAElEQAkBwIBEARAIAAQArQEIACJAEFgBIGAQACgGhYARRBKBIQZHBUcogQFSLRQTzRgAA; A1=d=AQABBNNtBl4CEPe2CGDKlq-wp3CQAsBvGsYFEgABAgHWfl9PYO2Nb2UB9iMAAAcIpDuzXXHBWxE&S=AQAAAvNdxTJO207IlgIjbN6_kcc; A3=d=AQABBNNtBl4CEPe2CGDKlq-wp3CQAsBvGsYFEgABAgHWfl9PYO2Nb2UB9iMAAAcIpDuzXXHBWxE&S=AQAAAvNdxTJO207IlgIjbN6_kcc; A1S=d=AQABBNNtBl4CEPe2CGDKlq-wp3CQAsBvGsYFEgABAgHWfl9PYO2Nb2UB9iMAAAcIpDuzXXHBWxE&S=AQAAAvNdxTJO207IlgIjbN6_kcc&j=GDPR; GUC=AQABAgFfftZgT0IcMgQr; APIDTS=1602061808',
    }

    params = (
        ('crumb', 'JiimCS.gUQC'),
        ('lang', 'en-US'),
        ('region', 'US'),
        ('formatted', 'true'),
        ('corsDomain', 'finance.yahoo.com'),
    )

    data = '{"offset":0,"size":25,"sortField":"percentchange","sortType":"desc","quoteType":"EQUITY","query":{"operator":"AND","operands":[{"operator":"eq","operands":["region","us"]},{"operator":"or","operands":[{"operator":"BTWN","operands":["intradaymarketcap",2000000000,10000000000]},{"operator":"BTWN","operands":["intradaymarketcap",10000000000,100000000000]},{"operator":"GT","operands":["intradaymarketcap",100000000000]}]},{"operator":"gt","operands":["dayvolume",5000000]}]},"userId":"","userIdType":"guid"}'

    response = requests.post('https://query1.finance.yahoo.com/v1/finance/screener', headers=headers, params=params, data=data)

    if (response.status_code == 200):
      data = json.loads(response.text)["finance"]["result"][0]["quotes"]
      data = pd.DataFrame(data)
      return data["symbol"]