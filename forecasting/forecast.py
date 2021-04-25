from api.yahoo_api import YahooApi
from preprocessing.data_preparator import DataPreparator
from api.etoro_api import EtoroApi
import pandas as pd
from yahoo_finance_api2 import share
from misc.file_name import file_name, periods, take_profit, period_type, frequency_type, stop_loss, frequency, intervals_to_profit
from training.sklearn_models.my_ensemble import MyEnsemble
from api.telegram import send_stock_newsletter

def run(model=MyEnsemble()):
  yahoo_api = YahooApi()
  etoro_api = EtoroApi()
  data_preparator = DataPreparator()
  stocks = etoro_api.get_stocks(get_all=True)
  print(len(stocks))
  stock_predictions = []
  for stock in stocks.iterrows():
      stock = stock[1]
      stock_data = yahoo_api.get_stock_data(stock["SymbolFull"],  periods=1, take_profit=take_profit, intervals_to_profit=intervals_to_profit, period_type=period_type, frequency_type=frequency_type, frequency=frequency)
      if stock_data is not None:
          stocks = data_preparator.prepare(stock_data,only_last_row=True, intervals_to_profit=intervals_to_profit, take_profit=take_profit, stop_loss=stop_loss)
          if stocks is not None:
              prepared_stock = stocks.tail(1)
              proba = round(model.predict_proba(prepared_stock) * 100, 2)
              stock_predictions.append({"symbol": stock["SymbolFull"], "name": stock["InstrumentDisplayName"], "proba": proba})
              print(f'{stock["InstrumentDisplayName"]}: {proba}')

  sorted_stock_predictions = sorted(stock_predictions, key=lambda k: k['proba'], reverse=True)[:25]
  print(sorted_stock_predictions)
  send_stock_newsletter(sorted_stock_predictions)