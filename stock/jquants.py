import jquantsapi
import pandas as pd
from dotenv import load_dotenv

from .base import StockDataProvider


class JQuantsProvider(StockDataProvider):
    """J-Quants V2 APIによる株価取得プロバイダ。"""

    COLUMN_MAP = {
        'O': 'Open',
        'H': 'High',
        'L': 'Low',
        'C': 'Close',
        'Vo': 'Volume',
        'Va': 'Amount',
    }

    def __init__(self):
        load_dotenv()
        self._cli = jquantsapi.ClientV2()

    def get_listed_codes(self, market: str) -> list[tuple[str, str]]:
        df = self._cli.get_list()
        filtered = df[df["MktNmEn"] == market]
        return list(zip(filtered["Code"], filtered["CoName"]))

    def get_daily_bars(self, code: str, start, end) -> pd.DataFrame:
        from_dt = pd.Timestamp(start).strftime('%Y%m%d')
        to_dt = pd.Timestamp(end).strftime('%Y%m%d')
        df = self._cli.get_eq_bars_daily(
            code=code,
            from_yyyymmdd=from_dt,
            to_yyyymmdd=to_dt,
        )

        df = df.rename(columns=self.COLUMN_MAP)
        df = df.set_index('Date')
        df.index = df.index.normalize()

        cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount']
        return df[cols].sort_index()
