import requests
import pandas as pd
from datetime import datetime, timedelta
from time import sleep

# === 설정 ===
symbol = "XRP"
interval = 5  # 5분봉
market = f"KRW-{symbol}"
limit_per_call = 200
api_url = f"https://api.bithumb.com/v1/candles/minutes/{interval}"

# 수집 기간: 2025년 6월 1일 00:00 ~ 6월 30일 23:55
start_date = datetime(2025, 6, 1)
end_date = datetime(2025, 6, 30, 23, 55)

# 요청 타임스탬프 리스트 생성 (역순으로)
timestamps = []
current = end_date
while current >= start_date:
    timestamps.append(current.strftime("%Y-%m-%d %H:%M:%S"))
    current -= timedelta(minutes=interval * limit_per_call)

# 데이터 수집
all_data = []

for ts in timestamps:
    params = {
        "market": market,
        "count": limit_per_call,
        "to": ts
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        # data = response.json().get("data", [])
        data = response.json()
        for item in data:
            all_data.append({
                "timestamp": item["candle_date_time_kst"],
                "open": float(item["opening_price"]),
                "high": float(item["high_price"]),
                "low": float(item["low_price"]),
                "close": float(item["trade_price"]),
                "volume": float(item["candle_acc_trade_volume"])
            })
        print(f"✅ {ts} 까지 수집 완료")
    except Exception as e:
        print(f"❌ 에러 발생 ({ts}): {e}")
        break
    sleep(0.3)  # 과도한 요청 방지

# 데이터 정리 및 저장
df = pd.DataFrame(all_data)
df = df.drop_duplicates(subset=["timestamp"])
print(df)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

filename = f"bithumb_{symbol}_5min_2025_06.csv"
df.to_csv(filename, index=False)
print(f"\n📁 저장 완료: {filename}")
