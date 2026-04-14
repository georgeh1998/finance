import argparse

from backtest.datasource.yfinance_source import YFinanceDataSource
from backtest.engine import BacktestEngine
from backtest.strategy.bollinger import BollingerStrategy
from backtest.strategy.sma_cross import SmaCrossStrategy

STRATEGIES = {
    "sma_cross": SmaCrossStrategy,
    "bollinger": BollingerStrategy,
}


def main():
    parser = argparse.ArgumentParser(description="株式バックテストツール")
    parser.add_argument("--symbol", required=True, help="銘柄コード（例: 7203.T）")
    parser.add_argument("--period", default="1y", help="取得期間（デフォルト: 1y）")
    parser.add_argument("--strategy", choices=STRATEGIES.keys(), default="sma_cross",
                        help="戦略（デフォルト: sma_cross）")
    parser.add_argument("--short", type=int, default=25, help="短期SMA日数（デフォルト: 25）[sma_cross用]")
    parser.add_argument("--long", type=int, default=75, help="長期SMA日数（デフォルト: 75）[sma_cross用]")
    parser.add_argument("--bb-period", type=int, default=20,
                        help="ボリンジャーバンド期間（デフォルト: 20）[bollinger用]")
    parser.add_argument("--bb-std", type=float, default=2.0,
                        help="ボリンジャーバンド標準偏差倍率（デフォルト: 2.0）[bollinger用]")
    parser.add_argument("--cash", type=float, default=1_000_000, help="初期資金（デフォルト: 1000000）")
    parser.add_argument("--commission", type=float, default=0.001, help="手数料率（デフォルト: 0.001）")
    parser.add_argument("--chart", default=None, help="チャートHTML出力先（指定しなければブラウザで表示）")
    args = parser.parse_args()

    strategy_class = STRATEGIES[args.strategy]

    datasource = YFinanceDataSource()
    engine = BacktestEngine(
        datasource=datasource,
        strategy_class=strategy_class,
        cash=args.cash,
        commission=args.commission,
    )

    if args.strategy == "sma_cross":
        strategy_desc = f"SMA({args.short}, {args.long})"
        strategy_params = dict(short_window=args.short, long_window=args.long)
    else:
        strategy_desc = f"BB(period={args.bb_period}, std={args.bb_std})"
        strategy_params = dict(bb_period=args.bb_period, bb_std=args.bb_std)

    print(f"=== バックテスト: {args.symbol} ===")
    print(f"期間: {args.period} / 戦略: {args.strategy} / {strategy_desc} / 資金: {args.cash:,.0f}円\n")

    result = engine.run(
        args.symbol,
        period=args.period,
        **strategy_params,
    )

    print("--- 結果サマリー ---")
    print(result.summary())

    print(f"\n--- 取引履歴 ({len(result.trades)}件) ---")
    if len(result.trades) > 0:
        display_cols = ["Size", "EntryTime", "ExitTime", "EntryPrice", "ExitPrice", "PnL", "ReturnPct"]
        available = [c for c in display_cols if c in result.trades.columns]
        print(result.trades[available].to_string())

    if args.chart:
        engine.plot(filename=args.chart)
        print(f"\nチャートを保存しました: {args.chart}")
    else:
        print("\nチャートをブラウザで表示します...")
        engine.plot()


if __name__ == "__main__":
    main()
