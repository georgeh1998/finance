import pandas as pd
from backtesting import Strategy

from backtest.strategy import calc_buy_size


def BB_MIDDLE(values, n):
    """ボリンジャーバンド中央線（SMA）を計算する。"""
    return pd.Series(values).rolling(n).mean()


def BB_UPPER(values, n, k):
    """ボリンジャーバンド上バンドを計算する。"""
    s = pd.Series(values)
    return s.rolling(n).mean() + s.rolling(n).std() * k


def BB_LOWER(values, n, k):
    """ボリンジャーバンド下バンドを計算する。"""
    s = pd.Series(values)
    return s.rolling(n).mean() - s.rolling(n).std() * k


class BollingerStrategy(Strategy):
    """ボリンジャーバンド逆張り戦略。

    終値が下バンド以下で買い、上バンド以上で売り。
    """

    bb_period = 20
    bb_std = 2.0

    def init(self):
        close = self.data.Close
        self.bb_middle = self.I(BB_MIDDLE, close, self.bb_period, name="BB Middle")
        self.bb_upper = self.I(BB_UPPER, close, self.bb_period, self.bb_std, name="BB Upper")
        self.bb_lower = self.I(BB_LOWER, close, self.bb_period, self.bb_std, name="BB Lower")

    def next(self):
        price = self.data.Close[-1]
        if not self.position:
            if price <= self.bb_lower[-1]:
                size = calc_buy_size(self.equity, price)
                if size > 0:
                    self.buy(size=size)
        else:
            if price >= self.bb_upper[-1]:
                self.position.close()
