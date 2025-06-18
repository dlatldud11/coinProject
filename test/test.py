import pandas as pd
import numpy as np
from ta.trend import MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from datetime import datetime
from tabulate import tabulate

# CSV 데이터 로드 (5분봉, 컬럼: timestamp, open, high, low, close, volume)
df = pd.read_csv("bithumb_XRP_5min_2025_06.csv")  # ← 파일명 수정
df["timestamp"] = pd.to_datetime(df["timestamp"])
df.set_index("timestamp", inplace=True)

# === 지표 계산 ===
# MACD(2, 4, 2)
macd = MACD(df["close"], window_slow=2, window_fast=4, window_sign=2)
df["macd"] = macd.macd()
df["macd_signal"] = macd.macd_signal()

# RSI(14)
rsi = RSIIndicator(df["close"], window=14)
df["rsi"] = rsi.rsi()

# Stochastic %K and %D
stoch = StochasticOscillator(df["high"], df["low"], df["close"], window=14, smooth_window=3)
df["stoch_k"] = stoch.stoch()
df["stoch_d"] = stoch.stoch_signal()

# === 매매 로직 적용 ===
initial_cash = 1_000_000
cash = initial_cash
btc = 0
trade_log = []

for i in range(1, len(df)):
    
    row = df.iloc[i]
    prev_row = df.iloc[i - 1]

    # 골든크로스 (MACD + RSI + 스토캐스틱)
    buy_signal = (
        prev_row["macd"] < prev_row["macd_signal"] and
        row["macd"] > row["macd_signal"] and
        row["rsi"] > 50 and
        row["stoch_k"] < 20
    )

    # 데드크로스 (MACD + RSI + 스토캐스틱)
    sell_signal = (
        prev_row["macd"] > prev_row["macd_signal"] and
        row["macd"] < row["macd_signal"] and
        row["rsi"] < 50 and
        row["stoch_k"] > 70
    )

    price = row["close"]
    timestamp = row.name.strftime("%Y-%m-%d %H:%M")

    if buy_signal and cash > 0:
        btc = cash / price
        trade_log.append([timestamp, "BUY", price, btc, -cash, 0])
        cash = 0

    elif sell_signal and btc > 0:
        cash = btc * price
        trade_log.append([timestamp, "SELL", price, btc, cash, cash])
        btc = 0

# === 결과 출력 ===
result_df = pd.DataFrame(trade_log, columns=["timestamp", "type", "price", "amount", "total", "cumulative"])
final_value = cash if cash > 0 else btc * df["close"].iloc[-1]
profit = final_value - initial_cash
profit_rate = profit / initial_cash * 100

print("\n📈 거래 로그:")
print(tabulate(result_df, headers='keys', tablefmt='pretty', showindex=False))

print(f"\n💰 최종 자산: ₩{final_value:,.0f}")
print(f"📊 수익: ₩{profit:,.0f} | 수익률: {profit_rate:.2f}%")

# CSV 저장
result_df.to_csv("simulation_result.csv", index=False)
print("\n📁 결과가 'simulation_result.csv'로 저장되었습니다.")
