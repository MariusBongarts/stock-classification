from api.yahoo_api import YahooApi
from preprocessing.data_preparator import DataPreparator
from sklearn.utils import resample
from api.etoro_api import EtoroApi
import pandas as pd
import time
import sys
from yahoo_finance_api2 import share
from misc.file_name import file_name, periods, take_profit, period_type, frequency_type, stop_loss, frequency, intervals_to_profit

# Override in case environment variables are passed
try:
    intervals_to_profit = intervals_to_profit if sys.argv[1] is None else int(sys.argv[1])
except:
    pass

print(f'Intervals to profit: {intervals_to_profit}')

class DataCrawler:
  '''This class uses the yahoo_api class to crawl stock data and saves it to .csv file.
  Takes the most active yahoo stocks.
  '''

  crawled_stocks = []
  yahoo_api = YahooApi()
  etoro_api = EtoroApi()
  data_preparator = DataPreparator()

  found_positive_data = False

  def start(self):
    # most_active_stocks = self.yahoo_api.get_most_active_stocks()
    all_stocks = self.etoro_api.get_stocks(get_all=True)["SymbolFull"]

    for stock in all_stocks:
      if (stock not in self.crawled_stocks):
        # stock_data = self.etoro_api.get_stock_data(stock, rows=rows, interval=interval)
        stock_data = self.yahoo_api.get_stock_data(stock, periods=periods, take_profit=take_profit, intervals_to_profit=intervals_to_profit, period_type=period_type, frequency_type=frequency_type, frequency=frequency)
        if ((stock_data is None) or (not len(stock_data))):
          print(f'No data found for stock: {stock}')
          continue
        print(f'Found {len(stock_data)} rows of data for stock: {stock}')
        self.df = self.data_preparator.prepare(stock_data, intervals_to_profit=intervals_to_profit, take_profit=take_profit, stop_loss=stop_loss)
        self.balance_data()

        if self.found_positive_data:
          self.crawled_stocks.append(stock)

        self.write_data_to_file()

  def balance_data(self):
    # Balance the data of the current file
    positive = self.df[self.df["profit"] == 1]
    print(f'Found {len(positive)} rows with profit')
    if (len(positive)):
      self.found_positive_data = True
      negative = self.df[self.df["profit"] == 0]

      downsampled = resample(negative,
                                replace=True,  # sample with replacement
                                # match number in minority class
                                n_samples=len(positive))  # reproducible results
      # combine minority and downsampled majority
      self.balanced_data = pd.concat([positive, downsampled])

  # Writes balanced data to file if positive rows were found
  def write_data_to_file(self):
    if (self.found_positive_data):
      self.found_positive_data = False
      path = f'./preprocessing/data/{file_name}.csv'
      print(self.balanced_data.head())
      self.balanced_data.to_csv(path, mode='a',sep=';', float_format='%.2f', index=False, header=None)
