import json, requests

# curl --request GET \
#      --url 'https://api.bithumb.com/v1/candles/minutes/1?market=KRW-BTC&count=1' \
#      --header 'accept: application/json'
url = "https://api.bithumb.com/v1/candles/minutes/1?market=KRW-XRP&count=1"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    # print(data)
    print(json.dumps(data, indent=4)) #데이터 이쁘게보이게하기

else:
    print("Request failed with status code:", response.status_code)