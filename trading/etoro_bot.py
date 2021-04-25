from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from auth.env import etoro_username, etoro_password, etoro_client_request_id
from auth.etoro_token_helper import get_token, update_token, get_access_token
import time
import requests
class EtoroBot:
    '''This EtoroBot bot handles trades and
    gets information about the current portfolio on https://www.etoro.com
    by using selenium
    '''

    def __init__(self, mode='demo'):
        self.retry = 0
        self.mode = mode

    def start_driver(self):
        if(self.mode == "demo"):
          self.switch_mode('demo')
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1600,900')
        options.add_argument('--disable-gpu')
        CHROMEDRIVER_PATH = './misc/chromedriver'
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
        self.wait = WebDriverWait(self.driver, 5)
        self.driver.get("https://www.etoro.com")
        self.set_auth_token(get_token())

    def set_auth_token(self, token):
        self.driver.execute_script(f'window.localStorage.setItem("loginData", "{token}")')

    def get_auth_token(self):
        return self.driver.execute_script(f'return window.localStorage.getItem("loginData")')

    # Navigates to a specific route and checks if user is still signed in.
    # Otherwise we try to sign_in again.
    def navigate(self, route):
        self.driver.get(route)
        if ('login' in self.driver.current_url and 'login' not in route):
            self.sign_in()


    def sign_in(self):
        self.navigate("https://www.etoro.com/de/login")
        username_input = self.get_element_by_automation_id('input', 'login-sts-username-input')
        username_input.send_keys(etoro_username)
        password_input = self.get_element_by_automation_id('input', 'login-sts-password-input')
        password_input.send_keys(etoro_password)
        sign_in_btn = self.get_element_by_automation_id('button', 'login-sts-btn-sign-in')
        sign_in_btn.click()
        time.sleep(3)
        self.set_auth_token(self.get_auth_token())
        if ('login' not in self.driver.current_url):
              print('Successfully signed in and refreshed auth_token')
        else:
          self.retry = self.retry + 1
          print('Sign in failed!')
          # Retry twice
          if (self.retry <= 2):
            self.sign_in()

    def get_balance(self):
        self.navigate("https://www.etoro.com/portfolio")
        balance_element = self.get_element_by_automation_id('span', 'account-balance-availible-unit-value')
        return self.convert_dollar_string(balance_element.text)

    def convert_dollar_string(self, dollar_string):
        return float(dollar_string.replace("$","").replace(",",""))

    def get_orders(self):
        self.navigate("https://www.etoro.com/portfolio/orders")
        order_symbol_elements = self.driver.find_elements_by_css_selector(self.get_css_selector('span', 'orders-table-body-cell-action-market-name', attribute_name='data-etoro-automation-id'))
        order_symbols = list(map(lambda x: x.text, order_symbol_elements))
        return order_symbols

    def get_portfolio(self):
        self.navigate("https://www.etoro.com/portfolio")
        portfolio_symbol_elements = self.driver.find_elements_by_css_selector(self.get_css_selector('div', 'portfolio-overview-table-body-cell-market-name', attribute_name='data-etoro-automation-id'))
        portfolio_symbols = list(map(lambda x: x.text, portfolio_symbol_elements))
        return portfolio_symbols

    def get_stock(self, stock_symbol):
        self.navigate(f'https://www.etoro.com/markets/{stock_symbol}')
        if (stock_symbol.lower() not in self.driver.current_url.lower()):
            print(f'Stock with symbol {stock_symbol} not found')
            raise ValueError(f'Stock with symbol {stock_symbol} not found.')
        return True

    def make_order(self, stock_symbol, instrument_id, amount, stop_loss_percentage=2, take_profit_percentage=2):
        try:
          # Get the id of the stock
          if (instrument_id > 0):
            response = self.make_order_api(instrument_id, amount, stock_symbol, stop_loss_percentage, take_profit_percentage)
            if (response.status_code != 200):
              print(f'API call to make order failed with status code: {response.status_code}')
              return False
          return True
        except Exception as e:
          print(str(e))
          return False

    def make_order_api(self, instrument_id, amount, stock_symbol, stop_loss_percentage=2, take_profit_percentage=2):
      access_token = get_access_token()
      headers = {
      'authority': 'www.etoro.com',
      'accounttype': 'Demo' if self.mode == 'demo' else 'regular',
      'authorization': f'{access_token}',
      'content-type': 'application/json;charset=UTF-8',
      'accept': 'application/json, text/plain, */*',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
      'x-csrf-token': 'BiUjU4Am-10P4yu4pPKrEw__',
      'applicationidentifier': 'ReToro',
      'applicationversion': '227.0.3',
      'origin': 'https://www.etoro.com',
      'sec-fetch-site': 'same-origin',
      'sec-fetch-mode': 'cors',
      'sec-fetch-dest': 'empty',
      'referer': f'https://www.etoro.com/markets/{stock_symbol.lower()}',
      'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
      }

      params = (
          ('client_request_id', etoro_client_request_id),
      )

      data = '{"InstrumentID":' + f'{instrument_id}' + ',"IsBuy":true,"Leverage":1,"StopLossPercentage":' + f'{stop_loss_percentage}' + ',"TakeProfitPercentage":' + f'{take_profit_percentage}' + ',"IsTslEnabled":false,"View_UnitMargin":2168.95,"View_MaxPositionUnits":700,"View_Units":0.02,"View_openByUnits":false,"IsDiscounted":true,"Amount":' + f'{amount}' + ',"View_Source_Application":"apps-markets-market-market.view-trade-button","View_Source_Location":"/markets/amzn","View_CurrentTradingMode":"REGULAR"}'
      response = requests.post('https://www.etoro.com/sapi/trade-demo/entry-orders', headers=headers, params=params, data=data)
      return response
