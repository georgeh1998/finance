import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover

from backtest.strategy import calc_buy_size


def SMA(values, n):
    """単純移動平均を計算する。"""
    return pd.Series(values).rolling(n).mean()


class SmaCrossStrategy(Strategy):
    """移動平均クロス戦略。

    短期SMAが長期SMAを上抜けたら買い（ゴールデンクロス）、
    長期SMAが短期SMAを上抜けたらポジションクローズ（デッドクロス）。
    """

    short_window = 25
    long_window = 75

    def init(self):
        close = self.data.Close
        self.sma_short = self.I(SMA, close, self.short_window, name=f"SMA({self.short_window})")
        self.sma_long = self.I(SMA, close, self.long_window, name=f"SMA({self.long_window})")

    def next(self):
        if crossover(self.sma_short, self.sma_long):
            size = calc_buy_size(self.equity, self.data.Close[-1])
            if size > 0:
                self.buy(size=size)
        elif crossover(self.sma_long, self.sma_short):
            self.position.close()
