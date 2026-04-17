import datetime

import pandas as pd
import pytest

from stock.base import StockDataProvider
from swing_trading.trend import (
    TrendDetector,
    TrendResult,
    TrendType,
    _count_consecutive_from_tail,
)


class FakeProvider(StockDataProvider):
    """テスト用のプロバイダ。渡されたDataFrameをそのまま返す。"""

    def __init__(self, daily: pd.DataFrame):
        self._daily = daily

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


class TestTrendDetection:
    def test_uptrend_detected(self):
        """単調増加データで上昇トレンドが検出されること。"""
        closes = [float(100 + i) for i in range(70)]
        daily = _make_daily(closes)
        detector = TrendDetector(FakeProvider(daily))
        result = detector.detect("7203", "2026-01-05", "2026-04-15")

        assert result.trend == TrendType.UPTREND
        assert result.consecutive_days >= 5
        assert result.code == "7203"

    def test_downtrend_detected(self):
        """単調減少データで下降トレンドが検出されること。"""
        closes = [float(200 - i) for i in range(70)]
        daily = _make_daily(closes)
        detector = TrendDetector(FakeProvider(daily))
        result = detector.detect("7203", "2026-01-05", "2026-04-15")

        assert result.trend == TrendType.DOWNTREND
        assert result.consecutive_days >= 5
        assert result.code == "7203"

    def test_no_trend_flat(self):
        """一定価格ではトレンドなしになること。"""
        closes = [500.0] * 70
        daily = _make_daily(closes)
        detector = TrendDetector(FakeProvider(daily))
        result = detector.detect("7203", "2026-01-05", "2026-04-15")

        assert result.trend == TrendType.NO_TREND
        assert result.consecutive_days == 0

    def test_no_trend_oscillating(self):
        """上下に振動するデータではトレンドなしになること。"""
        base = [500.0] * 60
        oscillating = [500.0 + (10 if i % 2 == 0 else -10) for i in range(10)]
        closes = base + oscillating
        daily = _make_daily(closes)
        detector = TrendDetector(FakeProvider(daily))
        result = detector.detect("7203", "2026-01-05", "2026-04-15")

        assert result.trend == TrendType.NO_TREND


class TestCountConsecutive:
    def test_all_true(self):
        """全て True なら全長が返ること。"""
        s = pd.Series([True, True, True, True, True])
        assert _count_consecutive_from_tail(s) == 5

    def test_all_false(self):
        """全て False なら 0 が返ること。"""
        s = pd.Series([False, False, False])
        assert _count_consecutive_from_tail(s) == 0

    def test_tail_consecutive(self):
        """末尾から連続する True のみカウントされること。"""
        s = pd.Series([False, False, True, True, True])
        assert _count_consecutive_from_tail(s) == 3

    def test_gap_in_middle(self):
        """途中に False があれば末尾からの連続のみカウント。"""
        s = pd.Series([True, True, False, True, True])
        assert _count_consecutive_from_tail(s) == 2

    def test_empty_series(self):
        """空 Series では 0 が返ること。"""
        s = pd.Series([], dtype=bool)
        assert _count_consecutive_from_tail(s) == 0


class TestConsecutiveDays:
    def test_exactly_n_days(self):
        """ちょうどN日連続で成立する場合はトレンド検出されること。"""
        s = pd.Series([True, True, True, True, True])
        assert _count_consecutive_from_tail(s) == 5

        s2 = pd.Series([False, False, True, True, True])
        assert _count_consecutive_from_tail(s2) == 3

    def test_n_minus_one_days(self):
        """N-1日のみの連続ではmin_consecutive_daysを満たさないこと。"""
        s = pd.Series([False, True, True, True, True])
        count = _count_consecutive_from_tail(s)
        assert count == 4
        assert count < 5


class TestBatchDetection:
    def test_multiple_codes(self):
        """detect_batch が全銘柄分の結果を返すこと。"""
        closes = [float(100 + i) for i in range(70)]
        daily = _make_daily(closes)
        detector = TrendDetector(FakeProvider(daily))
        codes = ["7203", "6758", "9984"]
        results = detector.detect_batch(codes, "2026-01-05", "2026-04-15")

        assert len(results) == 3
        assert [r.code for r in results] == codes
        for r in results:
            assert isinstance(r, TrendResult)

    def test_detect_with_list_returns_list(self):
        """detect() に list を渡すと一括結果が返ること。"""
        closes = [float(100 + i) for i in range(70)]
        daily = _make_daily(closes)
        detector = TrendDetector(FakeProvider(daily))
        results = detector.detect(["7203", "6758"], "2026-01-05", "2026-04-15")

        assert isinstance(results, list)
        assert len(results) == 2

    def test_detect_batch_rejects_str(self):
        """detect_batch() に str を渡すと TypeError になること。"""
        closes = [float(100 + i) for i in range(70)]
        daily = _make_daily(closes)
        detector = TrendDetector(FakeProvider(daily))

        with pytest.raises(TypeError):
            detector.detect_batch("7203", "2026-01-05", "2026-04-15")


class TestTrendResult:
    def test_result_fields(self):
        """結果オブジェクトの各フィールドが正しい型であること。"""
        closes = [float(100 + i) for i in range(70)]
        daily = _make_daily(closes)
        detector = TrendDetector(FakeProvider(daily))
        result = detector.detect("7203", "2026-01-05", "2026-04-15")

        assert isinstance(result.code, str)
        assert isinstance(result.trend, TrendType)
        assert isinstance(result.consecutive_days, int)
        assert isinstance(result.evaluated_date, datetime.date)
        assert isinstance(result.sma5, float)
        assert isinstance(result.sma20, float)
        assert isinstance(result.sma60, float)

    def test_result_is_frozen(self):
        """frozen=True で属性変更が FrozenInstanceError を送出すること。"""
        closes = [float(100 + i) for i in range(70)]
        daily = _make_daily(closes)
        detector = TrendDetector(FakeProvider(daily))
        result = detector.detect("7203", "2026-01-05", "2026-04-15")

        with pytest.raises(AttributeError):
            result.code = "9999"
