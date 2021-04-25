import base64
import json
import os
import sys
from dotenv import load_dotenv
load_dotenv()
etoro_token_file = 'etoro-token.txt'

def get_token():
  return os.environ['ETORO_TOKEN']

def update_token(token):
  with open(etoro_token_file, 'w') as f:
    f.truncate(0)
    f.write(token)

def get_access_token():
  token = get_token()
  data = base64.b64decode(token)
  data = data.decode("UTF-8")
  data = json.loads(data)
  access_token = data['stsData']['accessToken']
  return access_token