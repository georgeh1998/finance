def calc_buy_size(equity: float, price: float, unit: int = 100, max_size: int = 200) -> int:
    """買い株数を計算する。unit株単位で、max_sizeを上限とする。"""
    size = min(int(equity // price // unit) * unit, max_size)
    return size if size >= unit else 0
