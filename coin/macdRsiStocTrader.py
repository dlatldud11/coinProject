import time
import asyncio
from datetime import datetime, timedelta
import json
from coin.bithumb_trader import place_order, chance_order, get_uuid_order, is_order_failed, get_ticker, fetch_candles
from log.logger import log_trade, init_log_file
from coin.execute.execute_batch import run_fill_checker

# EMA 계산
def ema(values, period):
    k = 2 / (period + 1)
    ema_values = [values[0]]
    for price in values[1:]:
        ema_values.append(price * k + ema_values[-1] * (1 - k))
    return ema_values

# MACD 계산
def calculate_macd(prices, short=5, long=13, signal=4):
    short_ema = ema(prices, short)
    long_ema = ema(prices, long)
    macd_line = [s - l for s, l in zip(short_ema[-len(long_ema):], long_ema)]
    signal_line = ema(macd_line, signal)
    return macd_line, signal_line

# RSI 계산
def calculate_rsi(prices, period=14):
    gains, losses = [], []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i-1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsi = []
    if avg_loss == 0:
        rsi.append(100)
    else:
        rs = avg_gain / avg_loss
        rsi.append(100 - (100 / (1 + rs)))

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))

    return rsi[-1]

# 스토캐스틱 %K 계산
def calculate_stochastic(highs, lows, closes, k_period=14, d_period=3):
    if len(closes) < k_period + d_period:
        return 0, 0

    k_values = []
    for i in range(len(closes) - k_period, len(closes)):
        high_slice = highs[i - k_period + 1:i + 1]
        low_slice = lows[i - k_period + 1:i + 1]
        current_close = closes[i]

        highest_high = max(high_slice)
        lowest_low = min(low_slice)

        if highest_high - lowest_low == 0:
            k = 0
        else:
            k = (current_close - lowest_low) / (highest_high - lowest_low) * 100
        k_values.append(k)

    d = sum(k_values[-d_period:]) / d_period
    return k_values[-1], d


# 정각 + 3초 대기
async def wait_until_minute_plus_3sec(interval=5):
    """
    interval (ex: 5분봉) 기준으로, 다음 봉이 생성된 후 2분 + 3초 뒤에 실행되도록 대기
    즉, 매 (5,10,15...) + 2분 + 3초 = 7,12,17,... 에 동작
    """
    while True:
        now = datetime.now()
        # 다음 5분봉이 생성될 정각 시간
        next_candle_minute = ((now.minute // interval) + 1) * interval
        next_candle_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=next_candle_minute)
        
        # 캔들 생성 후 2분 + 3초 뒤 타겟
        target = next_candle_time + timedelta(minutes=2, seconds=3)
        
        sleep_time = (target - now).total_seconds()
        if sleep_time <= 0:
            # 이미 시간이 지난 경우 한 번 더 계산
            continue
        
        print(f"⏳ 다음 {interval}분봉 캔들 생성 + 2분 3초 후까지 {sleep_time:.2f}초 대기 중... ({target})")
        await asyncio.sleep(sleep_time)
        break


# 자동매매 로직
async def run_auto_trading(market, csv_file):
    
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

        # 📌 매수 조건
        if (not in_position and 
            stochastic_k < 20 and
            macd_prev < signal_prev and macd_curr > signal_curr and 
            rsi < 50):
            
            trade_type = "BUY" # 매수
            result = place_order(trade_type, market, price, 0)
            
            # 주문성공확인
            if is_order_failed(result):
                # 실패 시 처리 로직
                print("매수주문 실패:")
                in_position = False
            else:
                # 성공 시 처리 로직
                print("매수주문 성공:")
                order_uuid = result["uuid"]
                in_position = True
                
                print(f"🟢 매수 요청 결과: {result}")
                order_timestamp = result.get("created_at", timestamp)
                log_trade(order_uuid, order_timestamp, "BUY", 0, 0, 0, 0, 0, 0, 0, csv_file)

        # 📌 매도 조건
        elif (in_position and 
              stochastic_k > 70 and 
              macd_prev > signal_prev and macd_curr < signal_curr and 
              rsi > 50):
            
            in_position = False # 매도 실패 시 잔액 문제일 수 있으므로 매수 다시 진행

            result = chance_order(market)
            volume = result['ask_account']['balance']
            trade_type = "SELL" # 매도
            result = place_order(trade_type, market, 0, volume)
            
            # 주문성공확인
            if is_order_failed(result):
                # 실패 시 처리 로직
                print("매도주문 실패:")
            else:
                # 성공 시 처리 로직
                print("매도주문 성공:")
                order_uuid = result["uuid"]
                
                print(f"🔴 매도 요청 결과: {result}")
                order_timestamp = result.get("created_at", timestamp)
                log_trade(order_uuid, order_timestamp, "SELL", 0, 0, 0, 0, 0, 0, 0, csv_file)

async def main():
    market = "KRW-XRP"  # 거래할 마켓
    filename = init_log_file(market)  # 거래 로그 파일 초기화
    await asyncio.gather(
        run_auto_trading(market, filename),  # 자동매매 로직
        run_fill_checker(filename)   # 체결 확인 배치
    )

# ✅ 실행
if __name__ == "__main__":
    asyncio.run(main())