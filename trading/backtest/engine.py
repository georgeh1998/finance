from dataclasses import dataclass

import pandas as pd
from backtesting import Backtest, Strategy

from backtest.datasource.base import DataSource


@dataclass
class BacktestResult:
    """バックテスト結果を格納するデータクラス。"""

    stats: pd.Series
    trades: pd.DataFrame
    equity_curve: pd.DataFrame

    def summary(self) -> str:
        """主要な統計情報を文字列で返す。"""
        keys = [
            "Start", "End", "Duration",
            "Return [%]", "Buy & Hold Return [%]",
            "Max. Drawdown [%]",
            "# Trades", "Win Rate [%]",
            "Best Trade [%]", "Worst Trade [%]",
            "Avg. Trade [%]",
            "Sharpe Ratio",
            "Equity Final [$]",
        ]
        lines = []
        for key in keys:
            if key in self.stats.index:
                lines.append(f"{key}: {self.stats[key]}")
        return "\n".join(lines)


class BacktestEngine:
    """バックテスト実行エンジン。データ取得→実行→結果整形を管理する。"""

    def __init__(
        self,
        datasource: DataSource,
        strategy_class: type,
        cash: float = 1_000_000,
        commission: float = 0.001,
    ):
        self._datasource = datasource
        self._strategy_class = strategy_class
        self._cash = cash
        self._commission = commission
        self._bt = None

    def run(self, symbol: str, period: str = "1y", **strategy_params) -> BacktestResult:
        df = self._datasource.fetch(symbol, period)
        self._bt = Backtest(
            df,
            self._strategy_class,
            cash=self._cash,
            commission=self._commission,
            finalize_trades=True,
        )
        stats = self._bt.run(**strategy_params)
        return BacktestResult(
            stats=stats,
            trades=stats["_trades"],
            equity_curve=stats["_equity_curve"],
        )

    def plot(self, filename: str = None):
        if self._bt is None:
            raise RuntimeError("run() を先に実行してください")
        self._bt.plot(filename=filename, open_browser=False)
