import pandas as pd
import pytest

from backtest.datasource.base import DataSource
from backtest.datasource.yfinance_source import YFinanceDataSource


class TestYFinanceDataSource:
    """yfinance データソースのテスト。実際にAPIを叩く統合テスト。"""

    def setup_method(self):
        self.ds = YFinanceDataSource()

    def test_implements_datasource_interface(self):
        assert isinstance(self.ds, DataSource)

    def test_fetch_returns_dataframe(self):
        df = self.ds.fetch("7203.T", period="3mo")
        assert isinstance(df, pd.DataFrame)

    def test_fetch_has_required_columns(self):
        df = self.ds.fetch("7203.T", period="3mo")
        required = {"Open", "High", "Low", "Close", "Volume"}
        assert required.issubset(set(df.columns))

    def test_fetch_index_is_datetime(self):
        df = self.ds.fetch("7203.T", period="3mo")
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_fetch_index_has_no_timezone(self):
        df = self.ds.fetch("7203.T", period="3mo")
        assert df.index.tz is None

    def test_fetch_no_nan_in_ohlcv(self):
        df = self.ds.fetch("7203.T", period="3mo")
        ohlcv = df[["Open", "High", "Low", "Close", "Volume"]]
        assert not ohlcv.isnull().any().any()

    def test_fetch_has_data(self):
        df = self.ds.fetch("7203.T", period="3mo")
        assert len(df) > 0

    def test_fetch_invalid_symbol_raises(self):
        with pytest.raises(ValueError):
            self.ds.fetch("INVALID_SYMBOL_99999.T", period="1mo")
