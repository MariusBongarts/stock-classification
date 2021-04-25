from dotenv import load_dotenv
load_dotenv()
import os

etoro_username=os.environ['ETORO_USERNAME']
etoro_password=os.environ['ETORO_PASSWORD']
etoro_client_request_id=os.environ['ETORO_CLIENT_REQUEST_ID']