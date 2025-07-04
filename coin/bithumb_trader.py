##############################빗썸샘플
# Python 3
# pip3 installl pyJwt
import jwt 
import uuid
import hashlib
import time
from urllib.parse import urlencode
import requests
import json
from dotenv import load_dotenv
import os
from requests.exceptions import RequestException

load_dotenv()

accessKey = os.getenv("BITHUMB_API_KEY") #발급받은 API KEY
secretKey = os.getenv("BITHUMB_API_SECRET") #발급받은 SECRET KEY
apiUrl = 'https://api.bithumb.com'


# 매수/매도 주문 함수
def place_order(type, market, price, volume=0):
  # Set API parameters
  # requestBody = dict( market='KRW-BTC', side='bid', volume=0.001, price=84000000, ord_type='limit' )
  if type == 'BUY': #매수
    requestBody = dict( market=market, side='bid', price=price, ord_type='price')
  elif type == 'SELL': #매도
    requestBody = dict( market=market, side='ask', volume=volume, ord_type='market')

  # print(f"주문 요청: {requestBody}")
  
  # Generate access token
  query = urlencode(requestBody).encode()
  hash = hashlib.sha512()
  hash.update(query)
  query_hash = hash.hexdigest()
  payload = {
      'access_key': accessKey,
      'nonce': str(uuid.uuid4()),
      'timestamp': round(time.time() * 1000), 
      'query_hash': query_hash,
      'query_hash_alg': 'SHA512',
  }   
  jwt_token = jwt.encode(payload, secretKey)
  authorization_token = 'Bearer {}'.format(jwt_token)
  headers = {
    'Authorization': authorization_token,
    'Content-Type': 'application/json'
  }

  try:
      # Call API
      response = requests.post(apiUrl + '/v1/orders', data=json.dumps(requestBody), headers=headers)
      # handle to success or fail
      print(response.status_code)
      # print(response.json())
      return response.json()
  except Exception as err:
      # handle exception
      print(f"주문 요청: {requestBody}")
      print(err)

# 주문가능정보
def chance_order(market):
  
  # print("accessKey", accessKey)
  # print("secretKey", secretKey)
  # Set API parameters
  param = dict( market=market )

  # Generate access token
  query = urlencode(param).encode()
  hash = hashlib.sha512()
  hash.update(query)
  query_hash = hash.hexdigest()
  payload = {
      'access_key': accessKey,
      'nonce': str(uuid.uuid4()),
      'timestamp': round(time.time() * 1000), 
      'query_hash': query_hash,
      'query_hash_alg': 'SHA512',
  }   
  jwt_token = jwt.encode(payload, secretKey)
  authorization_token = 'Bearer {}'.format(jwt_token)
  headers = {
    'Authorization': authorization_token
  }

  try:
      # Call API
      response = requests.get(apiUrl + '/v1/orders/chance', params=param, headers=headers)
      # handle to success or fail
      # print(response.status_code)
      # print(response.json())
      return response.json()
  except Exception as err:
      # handle exception
      print(err)
      
      
###
# 개별주문정보
def get_uuid_order(uuidStr):
  # Set API parameters
  param = dict( uuid=uuidStr )

  # Generate access token
  query = urlencode(param).encode()
  hash = hashlib.sha512()
  hash.update(query)
  query_hash = hash.hexdigest()
  payload = {
      'access_key': accessKey,
      'nonce': str(uuid.uuid4()),
      'timestamp': round(time.time() * 1000), 
      'query_hash': query_hash,
      'query_hash_alg': 'SHA512',
  }   
  jwt_token = jwt.encode(payload, secretKey)
  authorization_token = 'Bearer {}'.format(jwt_token)
  headers = {
    'Authorization': authorization_token
  }

  try:
      # Call API
      response = requests.get(apiUrl + '/v1/order', params=param, headers=headers)
      # handle to success or fail
      print(response.status_code)
      # print(response.json())
      return response.json()
  except Exception as err:
      # handle exception
      print(err)

###      
      
def is_order_failed(response):
    if 'error' in response:
        error_name = response['error'].get('name')
        error_msg = response['error'].get('message')
        print(f"[실패] {error_name} - {error_msg}")
        return True
    return False


# 현재가 조회
def get_ticker(merket):
  
  url = f"https://api.bithumb.com/v1/ticker?markets={merket}"
  headers = {"accept": "application/json"}
  response = requests.get(url, headers=headers)

  print(response.text)
  return  response.json()      


# 5분봉 캔들 데이터 조회
def fetch_candles(market="KRW-BTC", retry=3, delay=5):
    url = f"https://api.bithumb.com/v1/candles/minutes/5?market={market}&count=200"
    
    for attempt in range(retry):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            high_prices = [float(c["high_price"]) for c in reversed(data)]
            low_prices = [float(c["low_price"]) for c in reversed(data)]
            close_prices = [float(c["trade_price"]) for c in reversed(data)]
            timestamps = [c["candle_date_time_kst"] for c in reversed(data)]
            
            return high_prices, low_prices, close_prices, timestamps
        
        except RequestException as e:
            print(f"[{attempt+1}/{retry}] 네트워크 오류 발생: {e}")
            time.sleep(delay)
    
    raise ConnectionError("캔들 데이터를 가져오는 데 실패했습니다.")
