import pandas as pd
import pytest

from stock.base import StockDataProvider
from swing_trading.scanner import TrendScanner, _to_dataframe, ScanResult
from swing_trading.trend import TrendType


class FakeProvider(StockDataProvider):
    """テスト用プロバイダ。銘柄リストと日足データを差し替え可能。"""

    def __init__(self, listed: list[tuple[str, str]], daily: pd.DataFrame):
        self._listed = listed
        self._daily = daily

    def get_listed_codes(self, market: str) -> list[tuple[str, str]]:
        return self._listed

    def get_daily_bars(self, code: str, start, end) -> pd.DataFrame:
        return self._daily


def _make_daily(closes: list[float], start: str = "2026-01-05") -> pd.DataFrame:
    dates = pd.bdate_range(start, periods=len(closes))
    return pd.DataFrame(
        {
            "Open": closes,
            "High": closes,
            "Low": closes,
            "Close": closes,
            "Volume": [1000] * len(closes),
            "Amount": [5000] * len(closes),
        },
        index=dates,
    )


UPTREND_CLOSES = [float(100 + i) for i in range(70)]
DOWNTREND_CLOSES = [float(200 - i) for i in range(70)]
FLAT_CLOSES = [500.0] * 70


class TestTrendScannerBasic:
    def test_uptrend_stock_appears(self):
        """上昇トレンド銘柄がスキャン結果に含まれること。"""
        provider = FakeProvider(
            listed=[("7203", "トヨタ自動車")],
            daily=_make_daily(UPTREND_CLOSES),
        )
        scanner = TrendScanner(provider)
        df = scanner.scan("Prime", "2026-01-05", "2026-04-15")

        assert len(df) == 1
        assert df.iloc[0]["Code"] == "7203"
        assert df.iloc[0]["トレンド"] == TrendType.UPTREND.value

    def test_downtrend_stock_appears(self):
        """下降トレンド銘柄がスキャン結果に含まれること。"""
        provider = FakeProvider(
            listed=[("6758", "ソニー")],
            daily=_make_daily(DOWNTREND_CLOSES),
        )
        scanner = TrendScanner(provider)
        df = scanner.scan("Prime", "2026-01-05", "2026-04-15")

        assert len(df) == 1
        assert df.iloc[0]["トレンド"] == TrendType.DOWNTREND.value

    def test_no_trend_stock_excluded(self):
        """トレンドなし銘柄はスキャン結果に含まれないこと。"""
        provider = FakeProvider(
            listed=[("9984", "ソフトバンク")],
            daily=_make_daily(FLAT_CLOSES),
        )
        scanner = TrendScanner(provider)
        df = scanner.scan("Prime", "2026-01-05", "2026-04-15")

        assert len(df) == 0

    def test_empty_result_has_correct_columns(self):
        """結果が空でも正しいカラムのDataFrameが返ること。"""
        provider = FakeProvider(listed=[], daily=_make_daily(FLAT_CLOSES))
        scanner = TrendScanner(provider)
        df = scanner.scan("Prime", "2026-01-05", "2026-04-15")

        assert list(df.columns) == ["Code", "企業名", "現在株価(SMA5)", "トレンド", "連続日数"]
        assert len(df) == 0


class TestPriceFilter:
    def test_stock_above_max_price_excluded(self):
        """sma5 が max_price を超える銘柄は除外されること。"""
        # 終値が3001円になるようなデータ（上昇トレンド）
        closes = [float(3001 + i) for i in range(70)]
        provider = FakeProvider(
            listed=[("7203", "トヨタ自動車")],
            daily=_make_daily(closes),
        )
        scanner = TrendScanner(provider)
        df = scanner.scan("Prime", "2026-01-05", "2026-04-15", max_price=3000.0)

        assert len(df) == 0

    def test_stock_at_max_price_included(self):
        """sma5 が max_price ちょうどの銘柄は含まれること。"""
        # sma5 ≈ 最後の5日間の平均。終値が全て2999円なら sma5 = 2999
        closes = [2999.0] * 70
        # ただし flat だとトレンドなしになるため、下降トレンドデータで3000円以下にする
        closes = [float(3060 - i) for i in range(70)]  # 3060 → 2991 (上昇 reversed)
        provider = FakeProvider(
            listed=[("7203", "トヨタ自動車")],
            daily=_make_daily(closes),
        )
        scanner = TrendScanner(provider)
        df = scanner.scan("Prime", "2026-01-05", "2026-04-15", max_price=3000.0)

        assert len(df) == 1

    def test_custom_max_price(self):
        """max_price を変更するとフィルタ基準が変わること。"""
        closes = [float(1500 + i) for i in range(70)]
        provider = FakeProvider(
            listed=[("7203", "トヨタ自動車")],
            daily=_make_daily(closes),
        )
        scanner = TrendScanner(provider)

        df_strict = scanner.scan("Prime", "2026-01-05", "2026-04-15", max_price=1000.0)
        df_loose = scanner.scan("Prime", "2026-01-05", "2026-04-15", max_price=2000.0)

        assert len(df_strict) == 0
        assert len(df_loose) == 1


class TestMultipleStocks:
    def test_mixed_stocks_filtered_correctly(self):
        """上昇・下降・トレンドなし混在時に正しくフィルタされること。"""

        class MixedProvider(StockDataProvider):
            STOCKS = {
                "7203": _make_daily(UPTREND_CLOSES),
                "6758": _make_daily(DOWNTREND_CLOSES),
                "9984": _make_daily(FLAT_CLOSES),
            }

            def get_listed_codes(self, market):
                return [("7203", "トヨタ"), ("6758", "ソニー"), ("9984", "ソフトバンク")]

            def get_daily_bars(self, code, start, end):
                return self.STOCKS[code]

        scanner = TrendScanner(MixedProvider())
        df = scanner.scan("Prime", "2026-01-05", "2026-04-15")

        assert len(df) == 2
        codes = list(df["Code"])
        assert "7203" in codes
        assert "6758" in codes
        assert "9984" not in codes

    def test_result_dataframe_columns(self):
        """結果DataFrameが正しいカラム構成を持つこと。"""
        provider = FakeProvider(
            listed=[("7203", "トヨタ自動車")],
            daily=_make_daily(UPTREND_CLOSES),
        )
        scanner = TrendScanner(provider)
        df = scanner.scan("Prime", "2026-01-05", "2026-04-15")

        assert "Code" in df.columns
        assert "企業名" in df.columns
        assert "現在株価(SMA5)" in df.columns
        assert "トレンド" in df.columns
        assert "連続日数" in df.columns


class TestToDataframe:
    def test_empty_list(self):
        """空リストから空DataFrameが生成されること。"""
        df = _to_dataframe([])
        assert len(df) == 0
        assert "Code" in df.columns

    def test_single_result(self):
        """単一ScanResultが正しくDataFrameに変換されること。"""
        result = ScanResult(
            code="7203",
            name="トヨタ自動車",
            price=2500.0,
            trend=TrendType.UPTREND,
            consecutive_days=10,
        )
        df = _to_dataframe([result])

        assert len(df) == 1
        assert df.iloc[0]["Code"] == "7203"
        assert df.iloc[0]["企業名"] == "トヨタ自動車"
        assert df.iloc[0]["現在株価(SMA5)"] == 2500.0
        assert df.iloc[0]["トレンド"] == "uptrend"
        assert df.iloc[0]["連続日数"] == 10
