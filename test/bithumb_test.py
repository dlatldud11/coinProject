from coin.bithumb_trader import place_order, chance_order, is_order_failed, get_uuid_order, get_ticker
from log.logger import log_trade, init_log_file
from coin.execute.finalize_trade_async import finalize_trade_async
import json
import asyncio
from coin.execute.execute_batch import run_fill_checker

# !!!!!!! 이 테스트는 실제 주문을 발생시킵니다. 주의해서 사용하세요 !!!!!!!
# 주문테스트
# result = place_order("buy", "KRW-XRP", "5000", 0)
# print(f"🟢 매수 요청 결과: {result}")
# order_uuid = result["uuid"]

# 잔고테스트
# result = chance_order("KRW-BTC")

# volume = result['ask_account']['balance']
# avg_buy_price = result['ask_account']['avg_buy_price']

# print(f"잔고: {volume} ")
# print(f"잔고: {avg_buy_price}")
# print(f"잔고: {type(avg_buy_price)}")
# # 매도테스트
# result = place_order("sell", "KRW-XRP", 0, volume)
# print(f"🔴 매도 요청 결과: {result}")
# order_uuid = result["uuid"]

# # 사용 예시
# if is_order_failed(result):
#     # 실패 시 처리 로직
#     print("주문 실패:")
#     pass
# else:
#     # 성공 시 처리 로직
#     print("주문 성공:")
#     pass

# 개별주문정보
# result = get_uuid_order("C0106000001242288850")
# print(f"주문 정보: {json.dumps(result, indent=2, ensure_ascii=False)}")
# print(result["trades"][0]["price"])


# 현재가 조회 테스트
# result = get_ticker("KRW-BTC")
# # print(f"현재가: {json.dumps(result, indent=2, ensure_ascii=False)}")
# print(f"현재가: {result[0]["trade_price"]} 원")
# print(f"type: {type(result[0]["trade_price"])} 원")

# async def test_async():
#   # 체결정보 확인 테스트
#   # asyncio.run(finalize_trade_async(...))

#   buy_price, total_profit, trade_count = await finalize_trade_async(
#       uuid="C0106000001242740312",
#       trade_type="SELL",
#       sell_price=0,
#       buy_price=2980,
#       total_profit=0,
#       trade_count=0
#   )
  
if __name__ == "__main__":
    # asyncio.run(test_async())
    asyncio.run(run_fill_checker("250619_KRW-XRP_trade.csv"))


# filename = init_log_file("KRW-BTC")
# print(f"거래 로그 파일: {filename}")