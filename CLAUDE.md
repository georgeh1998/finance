# finance プロジェクト

## Python 環境

- Python バージョン: 3.12
- 仮想環境がなければ作成する: `python3 -m venv .venv`
- パッケージ操作は `.venv/bin/pip3` を使う
- コマンド実行は `.venv/bin/python3` を使う

## スクリプト実行

パッケージを跨いだ import (例: `swing_trading` から `stock` を import) を含むスクリプトは、プロジェクトルートからモジュール形式で実行する。

```bash
# ⭕ モジュール形式 (ドット区切り、.py なし)
.venv/bin/python3 -m swing_trading.how_to_use_swing_trading

# ❌ パス形式だと他パッケージが import できずエラーになる
.venv/bin/python3 swing_trading/how_to_use_swing_trading.py
```

## テスト

```bash
.venv/bin/python3 -m pytest                              # 全テスト実行
.venv/bin/python3 -m pytest stock/tests/                  # モジュール単位
.venv/bin/python3 -m pytest stock/tests/test_weekly_bars.py  # ファイル単位
.venv/bin/python3 -m pytest -k "test_single_week"         # 特定テストのみ
```
