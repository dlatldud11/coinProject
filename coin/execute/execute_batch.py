import asyncio
import csv
import os
from datetime import datetime
from coin.bithumb_trader import place_order, chance_order, get_uuid_order, is_order_failed, get_ticker, fetch_candles

# 체결 확인 및 수익률 계산 로직
async def run_fill_checker(csv_file):
  # print(f"[체결확인] 실행됨 - csv_file: {csv_file}")
  
  while True:
      print("[체결확인] 체결 확인 배치 실행 중...")

      if not os.path.exists(csv_file):
        # print("[체결확인] CSV 파일 없음. 1분 후 재시도.")
        await asyncio.sleep(60)
        continue
      
      # print("[체결확인] CSV 파일 발견. 처리 시작.")
      rows = []
      updated = False

      # CSV 파일 로드
      with open(csv_file, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

      for i, row in enumerate(rows):
        if row["price"]:  # 이미 처리된 항목은 건너뜀
            continue

        uuid = row["uuid"]
        order_type = row["type"]

        # 체결 정보 조회
        detail = get_uuid_order(uuid)
        
        if not detail or "trades" not in detail or len(detail["trades"]) == 0:
          print("❌ 체결 정보 없음")
          continue
        
        total_price = 0.0
        total_volume = 0.0
        total_amounts = 0.0
        
        for trade in detail["trades"]:
          total_price += float(trade["price"]) * float(trade["volume"])
          total_volume += float(trade["volume"])
          total_amounts += float(trade["funds"])

        if total_volume == 0:
          print("❌ 체결 수량이 0")
          continue

        executed_price = total_price / total_volume
        rows[i]["price"] = executed_price
        rows[i]["volume"] = total_volume
        rows[i]["amounts"] = total_amounts

        # 직전 거래 정보 찾기
        prev_index = i - 1
        while prev_index >= 0 and not rows[prev_index]["price"]:
            prev_index -= 1

        prev_amounts = float(rows[prev_index]["amounts"]) if prev_index >= 0 else 0
        total_profit = float(rows[prev_index]["total_profit"]) if prev_index >= 0 else 0
        trade_count = int(rows[prev_index]["trade_count"]) if prev_index >= 0 else 0

        if order_type == "BUY":
          # 매수는 누적만 업데이트
          rows[i]["total_profit"] = total_profit
          rows[i]["trade_count"] = trade_count
        elif order_type == "SELL":
          profit = total_amounts - prev_amounts
          profit_rate = (profit / prev_amounts) * 100 if prev_amounts != 0 else 0
          total_profit += profit
          trade_count += 1

          rows[i]["profit"] = profit
          rows[i]["profit_rate"] = profit_rate
          rows[i]["total_profit"] = total_profit
          rows[i]["trade_count"] = trade_count

        updated = True

      # 변경사항 반영
      if updated:
        with open(csv_file, mode="w", newline="") as f:
          writer = csv.DictWriter(f, fieldnames=rows[0].keys())
          writer.writeheader()
          writer.writerows(rows)
        print("[체결확인] CSV 파일 업데이트 완료 ✅")

      await asyncio.sleep(60)  # 1분마다 실행
