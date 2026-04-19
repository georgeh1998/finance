import datetime

from stock import JQuantsProvider
from swing_trading.scanner import TrendScanner

_RESULT_MD = "scan_result.md"


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
        min_volume=500_000,
    )

    print(df.to_markdown(index=False))
    print(f"\n合計: {len(df)} 銘柄")

    df["Code"] = df["Code"].str[:-1]

    with open(_RESULT_MD, "w") as f:
        f.write(f"## スキャン結果 ({end})\n\n")
        f.write(df.to_markdown(index=False))
        f.write(f"\n\n合計: {len(df)} 銘柄\n")


if __name__ == "__main__":
    main()
