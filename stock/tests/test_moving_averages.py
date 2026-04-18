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


def _make_daily(closes: list[float], start: str = "2026-01-05") -> pd.DataFrame:
    """終値リストから日足DataFrameを生成する（営業日ベース）。"""
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


class TestMovingAverages:
    def test_default_windows(self):
        """デフォルト(5,20,60)のカラムが返ること。"""
        daily = _make_daily([100.0] * 60)
        result = FakeProvider(daily).get_moving_averages("7203", "2026-01-05", "2026-03-31")

        assert "Close" in result.columns
        assert "SMA5" in result.columns
        assert "SMA20" in result.columns
        assert "SMA60" in result.columns
        assert len(result) == 60

    def test_custom_windows(self):
        """カスタム期間を指定できること。"""
        daily = _make_daily([100.0] * 30)
        result = FakeProvider(daily).get_moving_averages(
            "7203", "2026-01-05", "2026-02-15", windows=(3, 10)
        )

        assert "SMA3" in result.columns
        assert "SMA10" in result.columns
        assert "SMA5" not in result.columns

    def test_sma5_calculation(self):
        """SMA5が正しく計算されること。"""
        closes = [100.0, 102.0, 104.0, 106.0, 108.0, 110.0, 112.0]
        daily = _make_daily(closes)
        result = FakeProvider(daily).get_moving_averages(
            "7203", "2026-01-05", "2026-01-13", windows=(5,)
        )

        # 最初の4日はNaN
        assert result["SMA5"].isna().sum() == 4
        # 5日目: (100+102+104+106+108) / 5 = 104.0
        assert result["SMA5"].iloc[4] == pytest.approx(104.0)
        # 6日目: (102+104+106+108+110) / 5 = 106.0
        assert result["SMA5"].iloc[5] == pytest.approx(106.0)
        # 7日目: (104+106+108+110+112) / 5 = 108.0
        assert result["SMA5"].iloc[6] == pytest.approx(108.0)

    def test_sma20_calculation(self):
        """SMA20が正しく計算されること。"""
        closes = list(range(1, 26))  # 1〜25
        daily = _make_daily([float(c) for c in closes])
        result = FakeProvider(daily).get_moving_averages(
            "7203", "2026-01-05", "2026-02-06", windows=(20,)
        )

        # 最初の19日はNaN
        assert result["SMA20"].isna().sum() == 19
        # 20日目: (1+2+...+20) / 20 = 10.5
        assert result["SMA20"].iloc[19] == pytest.approx(10.5)
        # 25日目: (6+7+...+25) / 20 = 15.5
        assert result["SMA20"].iloc[24] == pytest.approx(15.5)

    def test_constant_price(self):
        """一定価格ならSMAも同じ値になること。"""
        daily = _make_daily([500.0] * 60)
        result = FakeProvider(daily).get_moving_averages("7203", "2026-01-05", "2026-03-31")

        # NaN以外はすべて500.0
        for col in ["SMA5", "SMA20", "SMA60"]:
            non_nan = result[col].dropna()
            assert (non_nan == 500.0).all()

    def test_index_matches_daily(self):
        """戻り値のインデックスが日足と一致すること。"""
        daily = _make_daily([100.0] * 10)
        result = FakeProvider(daily).get_moving_averages(
            "7203", "2026-01-05", "2026-01-16", windows=(5,)
        )

        pd.testing.assert_index_equal(result.index, daily.index)

    def test_close_column_unchanged(self):
        """Close列が元の日足と同一であること。"""
        closes = [100.0, 105.0, 98.0, 110.0, 107.0]
        daily = _make_daily(closes)
        result = FakeProvider(daily).get_moving_averages(
            "7203", "2026-01-05", "2026-01-09", windows=(3,)
        )

        pd.testing.assert_series_equal(result["Close"], daily["Close"])
