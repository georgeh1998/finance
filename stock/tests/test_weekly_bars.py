import pandas as pd
import pytest

from stock.base import StockDataProvider


class FakeProvider(StockDataProvider):
    """テスト用のプロバイダ。渡されたDataFrameをそのまま返す。"""

    def __init__(self, daily: pd.DataFrame):
        self._daily = daily

    def get_listed_codes(self, market):
        return []

    def get_daily_bars(self, code, start, end):
        return self._daily


def _make_daily(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    df.index = pd.to_datetime(df.pop("Date"))
    return df


class TestWeeklyBars:
    def test_single_week(self):
        """月〜金の通常週が正しく集約されること。"""
        daily = _make_daily([
            {"Date": "2026-04-13", "Open": 100, "High": 108, "Low": 100,  "Close": 105, "Volume": 1000, "Amount": 5000},
            {"Date": "2026-04-14", "Open": 105, "High": 110, "Low": 102, "Close": 103, "Volume": 1200, "Amount": 6000},
            {"Date": "2026-04-15", "Open": 103, "High": 109, "Low": 98, "Close": 107, "Volume": 800,  "Amount": 4000},
            {"Date": "2026-04-16", "Open": 107, "High": 115, "Low": 105, "Close": 110, "Volume": 1500, "Amount": 7000},
            {"Date": "2026-04-17", "Open": 110, "High": 112, "Low": 108, "Close": 113, "Volume": 900,  "Amount": 4500},
        ])
        weekly = FakeProvider(daily).get_weekly_bars("7203", "2026-04-13", "2026-04-17")

        assert len(weekly) == 1
        row = weekly.iloc[0]
        assert row["Open"] == 100      # first
        assert row["High"] == 115      # max
        assert row["Low"] == 98        # min
        assert row["Close"] == 113     # last
        assert row["Volume"] == 5400   # sum
        assert row["Amount"] == 26500  # sum

    def test_holiday_gap(self):
        """祝日(水曜)が欠損していても正しく集約されること。"""
        daily = _make_daily([
            {"Date": "2026-04-13", "Open": 100, "High": 108, "Low": 100,  "Close": 105, "Volume": 1000, "Amount": 5000},
            {"Date": "2026-04-14", "Open": 105, "High": 110, "Low": 102, "Close": 103, "Volume": 1200, "Amount": 6000},
            # 水曜 04-15 は祝日で欠損
            {"Date": "2026-04-16", "Open": 107, "High": 115, "Low": 105, "Close": 110, "Volume": 1500, "Amount": 7000},
            {"Date": "2026-04-17", "Open": 110, "High": 112, "Low": 108, "Close": 113, "Volume": 900,  "Amount": 4500},
        ])
        weekly = FakeProvider(daily).get_weekly_bars("7203", "2026-04-13", "2026-04-17")

        assert len(weekly) == 1
        row = weekly.iloc[0]
        assert row["Open"] == 100      # first
        assert row["High"] == 115      # max
        assert row["Low"] == 100       # min (水曜のLow=98が欠損のため100)
        assert row["Close"] == 113     # last
        assert row["Volume"] == 4600   # sum (水曜なし)
        assert row["Amount"] == 22500  # sum (水曜なし)

    def test_two_weeks(self):
        """2週間分のデータが週ごとに正しく分かれること。"""
        daily = _make_daily([
            # 第1週
            {"Date": "2026-04-13", "Open": 100, "High": 110, "Low": 95,  "Close": 108, "Volume": 1000, "Amount": 5000},
            {"Date": "2026-04-17", "Open": 108, "High": 115, "Low": 105, "Close": 112, "Volume": 2000, "Amount": 8000},
            # 第2週
            {"Date": "2026-04-20", "Open": 112, "High": 120, "Low": 110, "Close": 118, "Volume": 1500, "Amount": 7000},
            {"Date": "2026-04-24", "Open": 118, "High": 125, "Low": 115, "Close": 122, "Volume": 1800, "Amount": 9000},
        ])
        weekly = FakeProvider(daily).get_weekly_bars("7203", "2026-04-13", "2026-04-24")

        assert len(weekly) == 2
        w1 = weekly.iloc[0]
        assert w1["Open"] == 100
        assert w1["Close"] == 112

        w2 = weekly.iloc[1]
        assert w2["Open"] == 112
        assert w2["Close"] == 122
