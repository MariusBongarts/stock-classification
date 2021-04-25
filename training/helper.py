
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from misc.file_name import file_name
pd.options.mode.chained_assignment = None
import pickle
import os
from datetime import datetime

def get_data():
  df = pd.read_csv(f'./preprocessing/data/{file_name}.csv', sep=';', encoding='utf-8')
  return df

def get_train_test_data(test_size=0.33, random_state=2502, scale_data=False, df=None):
  df = get_data() if df is None else df
  print('Data:', len(df))

  df.drop_duplicates(subset=None, keep='first', inplace=False)

  X = df
  y = df['profit']
  X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=test_size, random_state=random_state)

  X_train.drop("profit", axis = 1, inplace=True)

  results_target = X_test["profit"]
  X_test.drop("profit", axis = 1, inplace=True)

  print('Training data : ', len(X_train))
  print('Testdata: ', len(X_test))
  return X_train, X_test, y_train, y_test, results_target

def save_model(model, file_name=f'models/{file_name}.sav'):
  pickle.dump(model, open(file_name, 'wb'))