import pandas as pd

def adjust_price_based_on_profit(csv_path: str, base_price: float) -> float:
    """
    마지막 거래가 SELL이고 수익률(profit_rate)이 0 이상일 경우,
    base_price에 수익률을 반영하여 복리 효과를 적용한 가격을 반환합니다.

    :param csv_path: CSV 파일 경로
    :param base_price: 기준 가격 (예: 50000 원)
    :return: 수익률 반영된 가격
    """
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise ValueError(f"CSV 파일을 읽을 수 없습니다: {e}")

    if df.empty:
        # raise ValueError("CSV 파일에 데이터가 없습니다.")
        print("CSV 파일에 데이터가 없습니다.")
        return base_price

    last_row = df.iloc[-1]

    # 마지막 거래가 SELL이고, price가 존재하며, profit_rate가 음수가 아닌 경우
    if (
        last_row['type'] == 'SELL'
        and not pd.isna(last_row['price'])
        and last_row['profit_rate'] >= 0
    ):
        # 복리 적용: base_price * (1 + profit_rate)
        adjusted_price = base_price * (1 + (last_row['profit_rate'] * 0.01))  # profit_rate는 퍼센트로 가정
        return round(adjusted_price)

    # 조건이 맞지 않으면 원래 가격 반환
    return base_price
