import datetime

from stock import JQuantsProvider
from swing_trading.scanner import TrendScanner


def main():
    provider = JQuantsProvider()
    scanner = TrendScanner(provider)

    end = datetime.date.today()
    start = end - datetime.timedelta(days=120)

    df = scanner.scan(
        market="Prime",
        start=start,
        end=end,
        max_price=3000.0,
        min_consecutive_days=5,
    )

    print(df.to_csv(index=False))
    print(f"合計: {len(df)} 銘柄")


if __name__ == "__main__":
    main()
