import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy

from backtest.strategy.sma_cross import SmaCrossStrategy


def make_sample_data(n=500):
    """テスト用のOHLCVデータを生成する。複数の上昇→下降サイクルでクロスが確実に発生する。"""
    np.random.seed(42)
    dates = pd.bdate_range("2023-01-01", periods=n)
    # 複数サイクル（上昇→下降を繰り返す）
    cycle_len = n // 4
    trend = np.concatenate([
        np.linspace(1000, 1500, cycle_len),
        np.linspace(1500, 1000, cycle_len),
        np.linspace(1000, 1600, cycle_len),
        np.linspace(1600, 900, n - 3 * cycle_len),
    ])
    noise = np.random.normal(0, 10, n)
    close = trend + noise
    return pd.DataFrame({
        "Open": close - np.random.uniform(0, 5, n),
        "High": close + np.random.uniform(0, 10, n),
        "Low": close - np.random.uniform(0, 10, n),
        "Close": close,
        "Volume": np.random.randint(100000, 1000000, n),
    }, index=dates)


class TestSmaCrossStrategy:
    def test_inherits_backtesting_strategy(self):
        assert issubclass(SmaCrossStrategy, Strategy)

    def test_default_parameters(self):
        assert SmaCrossStrategy.short_window == 25
        assert SmaCrossStrategy.long_window == 75

    def test_runs_backtest_without_error(self):
        df = make_sample_data()
        bt = Backtest(df, SmaCrossStrategy, cash=1_000_000)
        stats = bt.run()
        assert stats is not None

    def test_custom_parameters(self):
        df = make_sample_data()
        bt = Backtest(df, SmaCrossStrategy, cash=1_000_000)
        stats = bt.run(short_window=10, long_window=50)
        assert stats is not None

    def test_generates_trades(self):
        df = make_sample_data()
        bt = Backtest(df, SmaCrossStrategy, cash=1_000_000)
        stats = bt.run()
        assert stats["# Trades"] > 0

    def test_stats_contain_return(self):
        df = make_sample_data()
        bt = Backtest(df, SmaCrossStrategy, cash=1_000_000)
        stats = bt.run()
        assert "Return [%]" in stats.index

    def test_trades_dataframe_available(self):
        df = make_sample_data()
        bt = Backtest(df, SmaCrossStrategy, cash=1_000_000)
        stats = bt.run()
        trades = stats["_trades"]
        assert isinstance(trades, pd.DataFrame)
        assert len(trades) > 0
