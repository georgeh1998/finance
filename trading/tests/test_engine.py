import numpy as np
import pandas as pd
import pytest

from backtest.datasource.base import DataSource
from backtest.engine import BacktestEngine, BacktestResult
from backtest.strategy.sma_cross import SmaCrossStrategy


class FakeDataSource(DataSource):
    """テスト用のフェイクデータソース。"""

    def fetch(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        np.random.seed(42)
        n = 500
        dates = pd.bdate_range("2023-01-01", periods=n)
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


class TestBacktestEngine:
    def setup_method(self):
        self.engine = BacktestEngine(
            datasource=FakeDataSource(),
            strategy_class=SmaCrossStrategy,
            cash=1_000_000,
        )

    def test_run_returns_backtest_result(self):
        result = self.engine.run("TEST", period="1y")
        assert isinstance(result, BacktestResult)

    def test_result_has_stats(self):
        result = self.engine.run("TEST", period="1y")
        assert isinstance(result.stats, pd.Series)
        assert "Return [%]" in result.stats.index
        assert "# Trades" in result.stats.index
        assert "Win Rate [%]" in result.stats.index

    def test_result_has_trades(self):
        result = self.engine.run("TEST", period="1y")
        assert isinstance(result.trades, pd.DataFrame)
        assert len(result.trades) > 0

    def test_result_has_equity_curve(self):
        result = self.engine.run("TEST", period="1y")
        assert isinstance(result.equity_curve, pd.DataFrame)
        assert "Equity" in result.equity_curve.columns

    def test_run_with_custom_strategy_params(self):
        result = self.engine.run("TEST", period="1y", short_window=10, long_window=50)
        assert isinstance(result, BacktestResult)

    def test_run_with_commission(self):
        engine = BacktestEngine(
            datasource=FakeDataSource(),
            strategy_class=SmaCrossStrategy,
            cash=1_000_000,
            commission=0.005,
        )
        result = engine.run("TEST", period="1y")
        assert isinstance(result, BacktestResult)

    def test_plot_generates_html(self, tmp_path):
        result = self.engine.run("TEST", period="1y")
        filepath = tmp_path / "test_chart.html"
        self.engine.plot(filename=str(filepath))
        assert filepath.exists()
        assert filepath.stat().st_size > 0

    def test_result_summary(self):
        result = self.engine.run("TEST", period="1y")
        summary = result.summary()
        assert "Return [%]" in summary
        assert "# Trades" in summary
