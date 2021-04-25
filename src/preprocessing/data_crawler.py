from yahoo_api import YahooApi
from data_preparator import DataPreparator
from stock_predictor import StockPredictor
from sklearn.utils import resample
from etoro_api import EtoroApi
import pandas as pd
import time
import sys
from yahoo_finance_api2 import share
from file_name import file_name, periods, take_profit, period_type, frequency_type, stop_loss, frequency, intervals_to_profit

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

      # Find negative entries where prediction to buy was highest -> True Negative entries to train model better
      # true_negatives = negative.copy()
      # model_filename = f'./models/{file_name}.sav'
      # stock_predictor = StockPredictor(model_filename=model_filename, proba=0.6)
      # predicted_data = true_negatives.copy()
      # predicted_data["prediction"] = 0.00
      # for index, stock in predicted_data.iterrows():
      #     predicted_data.loc[index:index]["prediction"] = stock_predictor.should_buy(true_negatives.loc[index:index], get_proba=True)
      # # Sort by predicted value -> Higher => more likely to buy
      # sorted_predicted_data = predicted_data.sort_values(by='prediction', ascending=False)
      # del sorted_predicted_data["prediction"]
      # negative = sorted_predicted_data[0:len(positive)+1]

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
      path = f'data/{file_name}.csv'
      print(self.balanced_data.head())
      self.balanced_data.to_csv(path, mode='a',sep=';', float_format='%.2f', index=False, header=None)
