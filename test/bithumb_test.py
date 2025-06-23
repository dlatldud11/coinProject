from coin.bithumb_trader import place_order, chance_order, is_order_failed, get_uuid_order, get_ticker, fetch_candles
from coin.macdRsiStocTrader import wait_until_minute_plus_3sec, calculate_macd, calculate_rsi, calculate_stochastic
from log.logger import log_trade, init_log_file
import json
import asyncio
from coin.execute.execute_batch import run_fill_checker
from coin.execute.adjust_price import adjust_price_based_on_profit

# 자동매매 로직
async def run_auto_trading(market):
    
    in_position = False
    market = market  # 거래할 마켓
    
    # 잔고테스트
    result = chance_order(market)
    volume = result['ask_account']['balance']
    
    if float(volume) > 0:
        avg_buy_price = float(result['ask_account']['avg_buy_price']) # 잔고의 평균 매수가격
        print(f"잔고가 있습니다. 현재 잔고: {volume} {market} 잔고의 평균 매수가격: {avg_buy_price}")
        in_position = True
        
    price = "50000" # 매수 가격 (고정값)

    while True:
        await wait_until_minute_plus_3sec(interval=5)  # 5분봉 기준
        # wait_until_minute_plus_3sec(interval=1)  # 1분봉 기준

        high_prices, low_prices, close_prices, timestamps = fetch_candles(market)
        if len(close_prices) < 27:
            print("⚠️ 데이터 부족")
            continue

        high_used_prices = high_prices[:-1]  # 최신 캔들 제외
        low_used_prices = low_prices[:-1]  # 최신 캔들 제외
        close_used_prices = close_prices[:-1]  # 최신 캔들 제외
        latest_price = close_used_prices[-1]
        timestamp = timestamps[-2]

        macd_list, signal_list = calculate_macd(close_used_prices, 2, 4, 2)
        macd_prev, macd_curr = macd_list[-2], macd_list[-1]
        signal_prev, signal_curr = signal_list[-2], signal_list[-1]
        
        rsi = calculate_rsi(close_used_prices)
        stochastic_k, stochastic_d = calculate_stochastic(high_used_prices, low_used_prices, close_used_prices)

        print(f"📅 {timestamp} | PRICE: {latest_price:.2f} 📈 MACD: {macd_curr:.2f}, Signal: {signal_curr:.2f}, RSI: {rsi:.2f}, Stochastic %K: {stochastic_k:.2f}")


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
# result = get_uuid_order("C0106000001244342087")
# print(f"주문 정보: {json.dumps(result, indent=2, ensure_ascii=False)}")
# print(result["paid_fee"])


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
  
# if __name__ == "__main__":
#     market = "KRW-ETH"  # 거래할 마켓
    
#     # asyncio.run(run_fill_checker("250620_KRW-XRP_trade.csv"))   # 체결 확인 배치)
#     # price = adjust_price_based_on_profit("250620_KRW-XRP_trade.csv", 50000)
#     # print(f"조정된 가격: {price}")
    
#     # 잔고테스트
#     result = chance_order(market)
#     print(f"잔고테스트: {json.dumps(result, indent=2, ensure_ascii=False)}")
#     volume = result['ask_account']['balance']


# filename = init_log_file("KRW-ETH")
# print(f"거래 로그 파일: {filename}")

market, price = input().split()
    
if market is None:
    market = "KRW-ETH"  # 거래할 마켓
if price is None:
    price = "50000"    
else:
    price = int(price)
    
print(f"입력된 타입: {market} {price}")