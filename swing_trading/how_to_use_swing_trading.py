from stock import JQuantsProvider
from swing_trading import TrendDetector


def main():
    provider = JQuantsProvider()
    detector = TrendDetector(provider)

    result = detector.detect(
        code='7203',
        start='2026-01-01',
        end='2026-04-17',
    )
    print(result)


if __name__ == '__main__':
    main()
