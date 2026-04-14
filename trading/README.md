# 株式バックテストツール

日本株（個別株）を対象としたバックテストツール。移動平均クロス戦略・ボリンジャーバンド戦略に対応。

## 特徴

- yfinance で日本株の日足データを取得
- Backtesting.py でバックテストを実行
- 結果サマリー（リターン、勝率、ドローダウン等）をコンソール出力
- 取引履歴の一覧表示
- 売買ポイント付きチャートをHTMLで可視化
- データソース・ストラテジーは差し替え可能な設計

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 使い方

```bash
source .venv/bin/activate

# 移動平均クロス戦略（デフォルト）
python main.py --symbol 7203.T --period 1y
python main.py --symbol 7203.T --period 2y --short 10 --long 50 --chart result.html

# ボリンジャーバンド戦略
python main.py --symbol 7203.T --period 1y --strategy bollinger
python main.py --symbol 7203.T --period 2y --strategy bollinger --bb-period 15 --bb-std 1.5 --chart result.html

# 初期資金・手数料率の変更
python main.py --symbol 6758.T --period 1y --cash 500000 --commission 0.005
```

### オプション一覧

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `--symbol` | (必須) | 銘柄コード（例: `7203.T`） |
| `--period` | `1y` | 取得期間（`3mo`, `6mo`, `1y`, `2y`, `5y` 等） |
| `--strategy` | `sma_cross` | 戦略（`sma_cross` / `bollinger`） |
| `--short` | `25` | 短期SMA日数 [sma_cross用] |
| `--long` | `75` | 長期SMA日数 [sma_cross用] |
| `--bb-period` | `20` | ボリンジャーバンド期間 [bollinger用] |
| `--bb-std` | `2.0` | ボリンジャーバンド標準偏差倍率 [bollinger用] |
| `--cash` | `1000000` | 初期資金（円） |
| `--commission` | `0.001` | 手数料率 |
| `--chart` | なし | チャートHTML出力先（省略時はブラウザで表示） |

### 銘柄コード例

| コード | 銘柄 |
|--------|------|
| `7203.T` | トヨタ自動車 |
| `6758.T` | ソニーグループ |
| `9984.T` | ソフトバンクグループ |
| `6861.T` | キーエンス |
| `8306.T` | 三菱UFJフィナンシャル・グループ |

## テスト

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

## プロジェクト構成

```
backtest/
  ├── datasource/
  │   ├── base.py              # DataSource 抽象クラス
  │   └── yfinance_source.py   # yfinance 実装
  ├── strategy/
  │   ├── sma_cross.py         # 移動平均クロス戦略
  │   └── bollinger.py         # ボリンジャーバンド戦略
  └── engine.py                # バックテスト実行エンジン
tests/
  ├── test_datasource.py
  ├── test_strategy.py
  ├── test_bollinger_strategy.py
  └── test_engine.py
main.py                        # CLI エントリポイント
requirements.txt
```
