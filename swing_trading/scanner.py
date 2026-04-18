import time
from dataclasses import dataclass

import pandas as pd

from stock.base import StockDataProvider
from swing_trading.trend import TrendDetector, TrendResult, TrendType

_RATE_LIMIT_INTERVAL = 1.05  # 60req/分 を超えないよう約1秒間隔


@dataclass(frozen=True)
class ScanResult:
    """スキャン結果の1銘柄分。"""
    code: str
    name: str
    price: float
    trend: TrendType
    consecutive_days: int


class TrendScanner:
    """指定市場の全銘柄を対象にトレンドスキャンを行う。"""

    def __init__(self, provider: StockDataProvider):
        self._provider = provider
        self._detector = TrendDetector(provider)

    def scan(
        self,
        market: str,
        start,
        end,
        max_price: float = 3000.0,
        min_consecutive_days: int = 5,
    ) -> pd.DataFrame:
        """指定市場の銘柄をスキャンし、トレンドあり・株価条件を満たす銘柄を返す。

        Args:
            market: 市場名（例: "Prime"）
            start: 分析開始日
            end: 分析終了日
            max_price: 株価上限（sma5 で代理判定）
            min_consecutive_days: トレンド認定に必要な最低連続日数

        Returns:
            columns: Code, 企業名, 現在株価, トレンド, 連続日数
        """
        codes_and_names = self._provider.get_listed_codes(market)
        results: list[ScanResult] = []

        for i, (code, name) in enumerate(codes_and_names):
            if i > 0:
                time.sleep(_RATE_LIMIT_INTERVAL)

            result: TrendResult = self._detector.detect(
                code, start, end, min_consecutive_days
            )

            if result.trend == TrendType.NO_TREND:
                continue
            if result.sma5 > max_price:
                continue

            results.append(ScanResult(
                code=code,
                name=name,
                price=result.sma5,
                trend=result.trend,
                consecutive_days=result.consecutive_days,
            ))

        return _to_dataframe(results)


def _to_dataframe(results: list[ScanResult]) -> pd.DataFrame:
    if not results:
        return pd.DataFrame(columns=["Code", "企業名", "現在株価(SMA5)", "トレンド", "連続日数"])

    rows = [
        {
            "Code": r.code,
            "企業名": r.name,
            "現在株価(SMA5)": r.price,
            "トレンド": r.trend.value,
            "連続日数": r.consecutive_days,
        }
        for r in results
    ]
    return pd.DataFrame(rows)
