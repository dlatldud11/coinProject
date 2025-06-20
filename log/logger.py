import csv
import os
from datetime import datetime

# 초기 CSV 로그 파일 설정
HEADER = ["uuid", "timestamp", "type", "price", "volume", "amounts", "paid_fee", "profit", "profit_rate", "total_profit", "total_profit_rate", "trade_count"]

# 거래 로그 파일 초기화 (처음에 한번만 실행됨)
def init_log_file(market="KRW-BTC"):
    
    today = datetime.now().strftime("%y%m%d")
    filename = f"{today}_{market}_trade.csv"
    
    try:
        with open(filename, mode="x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
    except FileExistsError:
        pass  # 이미 존재하면 무시
    
    return filename

# 거래 로그 저장
def log_trade(uuid, timestamp, type_, price, volume, amounts, paid_fee, profit, profit_rate, total_profit, total_profit_rate, trade_count, filename="trade_log.csv"):
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([uuid, timestamp, type_, price, round(volume, 4), round(amounts, 4), round(paid_fee, 2), round(profit, 2)
                         , round(profit_rate, 2), round(total_profit, 2), round(total_profit_rate, 2), trade_count])

