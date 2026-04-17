from stock import JQuantsProvider


def main():
    provider = JQuantsProvider()
    df = provider.get_daily_bars(
        code='7203',
        start='2026-03-01',
        end='2026-04-17',
    )
    print(df)


if __name__ == '__main__':
    main()
