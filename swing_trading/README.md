# swing_trading

スイングトレード向けのトレンドスキャンモジュール。

## モジュール構成

| ファイル | 役割 |
|---|---|
| `trend.py` | 個別銘柄のトレンド判定（`TrendDetector`） |
| `scanner.py` | 市場全体をスキャンしてトレンド銘柄を抽出（`TrendScanner`） |
| `how_to_use_scanner.py` | `TrendScanner` の使い方サンプル |

---

## TrendScanner の使い方

### 基本的な使い方

```python
import datetime
from stock import JQuantsProvider
from swing_trading.scanner import TrendScanner

provider = JQuantsProvider()
scanner = TrendScanner(provider)

end = datetime.date.today()
start = end - datetime.timedelta(days=120)

df = scanner.scan(
    market="Prime",          # 対象市場（例: "Prime", "Standard", "Growth"）
    start=start,             # 分析開始日
    end=end,                 # 分析終了日
    max_price=3000.0,        # 株価上限（SMA5 で代理判定）
    min_consecutive_days=5,  # トレンド認定に必要な最低連続日数
)

print(df.to_string(index=False))
print(f"合計: {len(df)} 銘柄")
```

### 戻り値の DataFrame

| 列名 | 内容 |
|---|---|
| `Code` | 銘柄コード |
| `企業名` | 企業名 |
| `現在株価(SMA5)` | 直近 SMA5 の値 |
| `トレンド` | `上昇` / `下降` |
| `連続日数` | トレンドが継続している日数 |

### パラメータ詳細

| パラメータ | デフォルト | 説明 |
|---|---|---|
| `market` | — | 対象市場名 |
| `start` | — | 分析開始日（`datetime.date`） |
| `end` | — | 分析終了日（`datetime.date`） |
| `max_price` | `3000.0` | この金額を超える銘柄は除外 |
| `min_consecutive_days` | `5` | これ未満の連続日数の銘柄は除外 |

---

## scan_market.py のスキャン条件

`scan_market.py` を実行すると、以下の条件で東証プライム銘柄を絞り込み `scan_result.md` に書き出す。

| 条件 | 値 | 説明 |
|---|---|---|
| 市場 | Prime | 東証プライム市場 |
| 分析期間 | 直近120日 | 当日から遡って120日分の株価を使用 |
| 株価上限 | 3000円以下 | SMA5 が 3000 円を超える銘柄は除外 |
| 最低連続日数 | 5日以上 | uptrend / downtrend が 5 日以上継続している銘柄のみ抽出 |

---

## サンプルスクリプトの実行

```bash
# プロジェクトルートから実行する（モジュール形式）
.venv/bin/python3 -m swing_trading.how_to_use_scanner
```

> パス形式（`python3 swing_trading/how_to_use_scanner.py`）だと `stock` パッケージの import に失敗するため、必ずモジュール形式で実行してください。
