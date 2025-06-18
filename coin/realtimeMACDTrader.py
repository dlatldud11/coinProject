import time
import requests
from datetime import datetime, timedelta

# 📌 MACD 계산 함수
def calculate_macd(prices, short=12, long=26, signal=9):
    def ema(values, period):
        ema_values = []
        k = 2 / (period + 1)
        for i, value in enumerate(values):
            if i == 0:
                ema_values.append(value)
            else:
                ema_values.append(value * k + ema_values[i-1] * (1 - k))
        return ema_values

    short_ema = ema(prices, short)
    long_ema = ema(prices, long)
    macd_line = [s - l for s, l in zip(short_ema[-len(long_ema):], long_ema)]
    signal_line = ema(macd_line, signal)
    return macd_line[-1], signal_line[-1]

# 📌 RSI 계산 함수
def calculate_rsi(prices, period=14):
    gains = []
    losses = []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        if delta > 0:
            gains.append(delta)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-delta)

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(prices) - 1):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# 📌 빗썸 200건 캔들 조회 API
BITHUMB_API = 'https://api.bithumb.com/v1/candles/minutes/1?market='

def fetch_candles(market="KRW-BTC"):
    response = requests.get(BITHUMB_API + f"{market}&count=200")
    data = response.json()
    close_prices = [float(candle["trade_price"]) for candle in reversed(data)]
    timestamps = [candle["candle_date_time_kst"] for candle in reversed(data)]
    
    return close_prices, timestamps

# 📌 정각 + 3초 대기
def wait_until_3_sec():
    while True:
        now = datetime.now()
        if now.second < 3:
            target = now.replace(second=3, microsecond=0)
        else:
            target = (now + timedelta(minutes=1)).replace(second=3, microsecond=0)
        sleep_time = (target - now).total_seconds()
        print(f"⏳ 다음 3초 시점까지 {sleep_time:.2f}초 대기 중...")
        time.sleep(sleep_time)
        break

# 📌 자동 매매 루프
def run_auto_trading():
    in_position = False
    buy_price = 0.0
    total_profit = 0.0
    trade_count = 0

    while True:
        wait_until_3_sec()

        close_prices, timestamps = fetch_candles()
        if len(close_prices) < 27:
            print("⚠️ 캐들 수 부족. 다음 루프 대기.")
            continue

        used_prices = close_prices[:-1]  # 가장 최근 캐들은 제외 (미확정)
        used_timestamps = timestamps[:-1]  # 가장 최근 캐들은 제외 (미확정)
        latest_confirmed_close = used_prices[-1]
        latest_timestamp = used_timestamps[-1]
        
        print(f"📅 {latest_timestamp}")
        
        macd, signal = calculate_macd(used_prices, 5, 13, 4)
        rsi = calculate_rsi(used_prices, 9)

        prev_macd, prev_signal = calculate_macd(used_prices[:-1], 5, 13, 4)
        prev_diff = prev_macd - prev_signal
        curr_diff = macd - signal

        print(f"[📈] MACD: {macd:.2f}, Signal: {signal:.2f}, RSI: {rsi:.2f} latest_confirmed_close: {latest_confirmed_close:.2f}")

        # 매수 조건
        if not in_position and prev_diff < 0 and curr_diff > 0 and rsi < 40: #30
            buy_price = latest_confirmed_close
            in_position = True
            print(f"🟢 매수! 가격: {buy_price}")

        # 매도 조건
        elif in_position and prev_diff > 0 and curr_diff < 0 and rsi > 60: #70
            sell_price = latest_confirmed_close
            profit = sell_price - buy_price
            profit_rate = (profit / buy_price) * 100
            total_profit += profit
            trade_count += 1
            in_position = False
            print(f"🔴 매도! 가격: {sell_price} | 수익: {profit:.0f}원 ({profit_rate:.2f}%)")
            print(f"📊 누적 수익: {total_profit:.0f}원 | 거래 수: {trade_count}회")

# ✅ 실행
run_auto_trading()