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
import math
from file_name import file_name, periods, take_profit, period_type, frequency_type, stop_loss, frequency, intervals_to_profit

class DataPreparator:
  '''This class gets a series of closing prices
  '''

  def prepare(self, df, intervals_to_profit=intervals_to_profit, take_profit=take_profit, stop_loss=stop_loss, only_last_row=False):
    try:
      # Store the original dataFrame
      self.df = df
      # If true, only the last row of the dataFrame will be prepared. Saves a copy of the dataFrame in the target variable
      self.target = self.df.copy().tail(1) if only_last_row else self.df.copy()

      # Calculate all sma´s (simple moving averages)
      self.calc_sma()

      # Calculates the momentums, based on the calculates sma´s
      self.calc_momentums()

      # Calculate the William r momentum
      self.target["williams_r"] = self.target.apply(lambda x: self.calc_william_r(x), axis=1)

      # Calculate the rsi (Relative Strength Index)
      self.target["rsi"] = self.target.apply(lambda x: self.calc_rsi(x), axis=1)
      self.target["rsi"] = round(self.target["rsi"])


      # Columns which are returned in the dataframe
      columns = ["Close", "momentum_2", "momentum_2_5","momentum_3_8", "momentum_5_10", "momentum_5_20","momentum_10_30", "williams_r", "rsi"]

      # Profit column gets added
      if (not only_last_row):
        self.calc_profit(intervals_to_profit, take_profit, stop_loss)
        # columns.insert(0, 'FromDate')
        columns.append('profit')

      return self.target[columns]
    except BaseException as e:
      print(e)
      return None

  def calc_profit(self, intervals_to_profit, take_profit, stop_loss):
    # Returns true, when `Close` goes up `take_profit` % in the next `intervals_to_profit` minutes and no value is under stop_loss
    self.target["profit"] = self.target.apply(lambda x:
    ((self.target.loc[x["rowIndex"]:(x["rowIndex"] + intervals_to_profit)]["Close"] > x["Close"] * take_profit).any()) &
    (not ((self.target.loc[x["rowIndex"]:(x["rowIndex"] + intervals_to_profit)]["Close"] < x["Close"] * (1 - (stop_loss - 1))).any()))
    if True else False, axis=1)

  def calc_sma(self):
    '''Calculates simple moving averages
    '''
    sma_s = [2, 3, 8, 5, 10, 20, 30]

    for sma in sma_s:
        try:
          if sma == 2:
            # We need this in the original dataFrame to calculate the rsi for the single target
            self.df[f'sma_{sma}'] = self.df.apply(lambda x: round(self.df.loc[x['rowIndex']-sma:x['rowIndex']]['Close'].mean(), 2), axis=1)
          self.target[f'sma_{sma}'] = self.target.apply(lambda x: round(self.df.loc[x['rowIndex']-sma:x['rowIndex']]['Close'].mean(), 2), axis=1)
        except Exception as e:
            print(str(e))

  def calc_momentums(self):
    '''Calculates the momentums, based on the simple moving averages
    '''

    self.target['momentum_2'] = (round(self.target["Close"] / self.target["sma_2"] * 100, 2) - 100)* 100
    # We need this in the original dataFrame to calculate the rsi for the single target
    self.df['momentum_2'] = (round(self.df["Close"] / self.df["sma_2"] * 100, 2) - 100)* 100
    self.target['momentum_2_5'] = (round(self.target["sma_2"] / self.target["sma_5"]* 100, 2) - 100)* 100
    self.target['momentum_3_8'] = (round(self.target["sma_3"] / self.target["sma_8"]* 100, 2) - 100)* 100
    self.target['momentum_5_10'] = (round(self.target["sma_5"] / self.target["sma_10"]* 100, 2) - 100)* 100
    self.target['momentum_5_20'] = (round(self.target["sma_5"] / self.target["sma_20"]* 100, 2) - 100)* 100
    self.target['momentum_10_30'] = (round(self.target["sma_10"] / self.target["sma_30"]* 100, 2) - 100)* 100

  # Calculate the William r momentum indicator
  # Die Nähe zu 0 gibt an, dass die Märkte überkauft sind (Werte zwischen 0 und −20). Durch die Wende des Signals nach unten entsteht ein Verkaufssignal. Werte zwischen −80 und −100 zeigen überverkaufte Situationen
  def calc_william_r(self, x):
    try:
      periods = 6
      max_high = self.df.loc[x["rowIndex"]-periods:x["rowIndex"]]['Close'].max()
      min_high = self.df.loc[x["rowIndex"]-periods:x["rowIndex"]]['Close'].min()
      close = x["Close"]
      williams_r = round((max_high - close) / (max_high - min_high) * 100, 2)
      if (not (math.isnan(williams_r) or math.isinf(williams_r))):
        return williams_r
      return 0
    except:
      return math.nan

  # Innerhalb der voreingestellten Periode werden zwei Summen gebildet.
  # Summe 1 enthält alle Kursveränderungen von Tagen mit steigendem Schlusskurs,
  # während Summe 2 all die Tage enthält, an denen der Schlusskurs unterhalb des Vortages war.
  # Werte von 0 – 30 als überverkaufter Markt, Werte zwischen 30 und 70 als normal und Werte zwischen 70 und 100 als überkaufter Markt angesehen werden
  def calc_rsi(self, x):
    try:
      periods = 10
      period = self.df.loc[x["rowIndex"]-periods:x["rowIndex"]]
      mean_positive = period[period["momentum_2"] > 0]["momentum_2"].mean() * 100
      mean_negative = period[period["momentum_2"] < 0]["momentum_2"].mean() * (-100)
      rsi = mean_positive / (mean_positive + mean_negative)
      if (not (math.isnan(rsi) or math.isinf(rsi))):
        return round(rsi * 100, 2)
      return 0
    except BaseException as e:
      return math.nan