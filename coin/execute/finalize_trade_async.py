import asyncio
from coin.bithumb_trader import get_uuid_order
from log.logger import log_trade

async def finalize_trade_async(uuid, trade_type, sell_price, buy_price, total_profit, trade_count):
    """
    주문 UUID를 이용해 체결 가격 평균을 계산하고, 수익률을 기록 (비동기 버전)

    :param uuid: 주문 UUID
    :param trade_type: "BUY" or "SELL"
    :param sell_price: 예상 매도가 (BUY 시 0으로 입력)
    :param buy_price: 매수가
    :param total_profit: 누적 수익
    :param trade_count: 거래 횟수
    """
    print(f"⏳ {trade_type} 체결 확인 대기 중... UUID: {uuid}")
    await asyncio.sleep(60)  # 비동기적으로 1분 대기

    order_result = get_uuid_order(uuid)
    if not order_result or "trades" not in order_result or len(order_result["trades"]) == 0:
        print("❌ 체결 정보 없음")
        return buy_price, total_profit, trade_count

    # 평균 체결가 계산
    total_price = 0.0
    total_volume = 0.0
    for trade in order_result["trades"]:
        total_price += float(trade["price"]) * float(trade["volume"])
        total_volume += float(trade["volume"])

    if total_volume == 0:
        print("❌ 체결 수량이 0")
        return buy_price, total_profit, trade_count

    executed_price = total_price / total_volume
    timestamp = order_result.get("created_at", "Unknown Time")

    if trade_type == "BUY":
        buy_price = executed_price
        print(f"🟢 실제 매수가: {buy_price:.2f}원 (총 수량: {total_volume})")
        log_trade(timestamp, "BUY", buy_price, 0, 0, total_profit, trade_count)

    elif trade_type == "SELL":
        sell_price = executed_price
        profit = sell_price - buy_price
        profit_rate = (profit / buy_price) * 100
        total_profit += profit
        trade_count += 1
        print(f"🔴 실제 매도가: {sell_price:.2f}원 (총 수량: {total_volume})")
        print(f"💰 수익: {profit:.2f}원 ({profit_rate:.2f}%)")
        print(f"📊 누적 수익: {total_profit:.2f}원 | 거래 수: {trade_count}회")
        log_trade(timestamp, "SELL", sell_price, profit, profit_rate, total_profit, trade_count)

    return buy_price, total_profit, trade_count
