import pandas as pd
import yfinance as yf

from backtest.datasource.base import DataSource


class YFinanceDataSource(DataSource):
    """yfinance を使った株価データソース。"""

    REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

    def fetch(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            raise ValueError(f"No data found for symbol: {symbol}")

        df = df[self.REQUIRED_COLUMNS]
        df.index = df.index.tz_localize(None)
        return df
