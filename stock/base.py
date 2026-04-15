from abc import ABC, abstractmethod
import pandas as pd


class StockDataProvider(ABC):
    """株価データ取得プロバイダの抽象基底クラス。"""

    @abstractmethod
    def get_daily_bars(self, code: str, start, end) -> pd.DataFrame:
        """日足OHLCVAを取得する。

        Returns:
            index: 時刻なしのDatetimeIndex
            columns: Open, High, Low, Close, Volume, Amount
        """
        raise NotImplementedError

    def get_weekly_bars(self, code: str, start, end) -> pd.DataFrame:
        """週足OHLCVAを取得する（金曜日区切り）。"""
        daily = self.get_daily_bars(code, start, end)
        weekly = daily.resample('W-FRI').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum',
            'Amount': 'sum',
        })
        return weekly.dropna(how='all')
