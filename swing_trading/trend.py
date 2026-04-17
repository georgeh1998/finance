import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Union, overload

import pandas as pd

from stock import StockDataProvider


class TrendType(Enum):
    """トレンド種別。"""
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    NO_TREND = "no_trend"


@dataclass(frozen=True)
class TrendResult:
    """トレンド判定結果。"""
    code: str
    trend: TrendType
    consecutive_days: int
    evaluated_date: datetime.date
    sma5: float
    sma20: float
    sma60: float


def _is_uptrend_row(df: pd.DataFrame) -> pd.Series:
    """各行で SMA5 > SMA20 > SMA60 が成立しているかを返す。"""
    return (df["SMA5"] > df["SMA20"]) & (df["SMA20"] > df["SMA60"])


def _is_downtrend_row(df: pd.DataFrame) -> pd.Series:
    """各行で SMA60 > SMA20 > SMA5 が成立しているかを返す。"""
    return (df["SMA60"] > df["SMA20"]) & (df["SMA20"] > df["SMA5"])


def _count_consecutive_from_tail(series: pd.Series) -> int:
    """末尾から連続して True である日数をカウントする。"""
    count = 0
    for v in series.values[::-1]:
        if v:
            count += 1
        else:
            break
    return count


class TrendDetector:
    """SMA並び順によるトレンド検出器。"""

    def __init__(self, provider: StockDataProvider):
        self._provider = provider

    @overload
    def detect(self, code: str, start, end, min_consecutive_days: int = 5) -> TrendResult: ...
    @overload
    def detect(self, code: list, start, end, min_consecutive_days: int = 5) -> list: ...

    def detect(
        self,
        code: Union[str, list],
        start,
        end,
        min_consecutive_days: int = 5,
    ) -> Union[TrendResult, list]:
        """銘柄のトレンドを判定する。str なら単一結果、list なら一括結果を返す。"""
        if isinstance(code, list):
            return self.detect_batch(code, start, end, min_consecutive_days)

        df = self._provider.get_moving_averages(
            code, start, end, windows=(5, 20, 60)
        )
        df = df.dropna()

        if df.empty:
            return TrendResult(
                code=code,
                trend=TrendType.NO_TREND,
                consecutive_days=0,
                evaluated_date=datetime.date.today(),
                sma5=float("nan"),
                sma20=float("nan"),
                sma60=float("nan"),
            )

        last_row = df.iloc[-1]
        evaluated_date = df.index[-1].date()

        up_count = _count_consecutive_from_tail(_is_uptrend_row(df))
        if up_count >= min_consecutive_days:
            return TrendResult(
                code=code,
                trend=TrendType.UPTREND,
                consecutive_days=up_count,
                evaluated_date=evaluated_date,
                sma5=last_row["SMA5"],
                sma20=last_row["SMA20"],
                sma60=last_row["SMA60"],
            )

        down_count = _count_consecutive_from_tail(_is_downtrend_row(df))
        if down_count >= min_consecutive_days:
            return TrendResult(
                code=code,
                trend=TrendType.DOWNTREND,
                consecutive_days=down_count,
                evaluated_date=evaluated_date,
                sma5=last_row["SMA5"],
                sma20=last_row["SMA20"],
                sma60=last_row["SMA60"],
            )

        return TrendResult(
            code=code,
            trend=TrendType.NO_TREND,
            consecutive_days=max(up_count, down_count),
            evaluated_date=evaluated_date,
            sma5=last_row["SMA5"],
            sma20=last_row["SMA20"],
            sma60=last_row["SMA60"],
        )

    def detect_batch(
        self,
        codes: list,
        start,
        end,
        min_consecutive_days: int = 5,
    ) -> list:
        """複数銘柄のトレンドを一括判定する。"""
        if isinstance(codes, str):
            raise TypeError(
                f"codes must be list[str], not str. Use detect('{codes}', ...) instead."
            )
        return [
            self.detect(code, start, end, min_consecutive_days)
            for code in codes
        ]
