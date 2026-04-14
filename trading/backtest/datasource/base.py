from abc import ABC, abstractmethod

import pandas as pd


class DataSource(ABC):
    @abstractmethod
    def fetch(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """OHLCV データを取得する。

        Returns:
            カラムが Open, High, Low, Close, Volume の DataFrame。
            インデックスは DatetimeIndex（タイムゾーンなし）。
        """
        ...
