# finance プロジェクト

## Python 環境

- 仮想環境がなければ作成する: `python3 -m venv .venv`
- パッケージ操作は `.venv/bin/pip3` を使う
- コマンド実行は `.venv/bin/python3` を使う

## テスト

```bash
.venv/bin/python3 -m pytest                              # 全テスト実行
.venv/bin/python3 -m pytest stock/tests/                  # モジュール単位
.venv/bin/python3 -m pytest stock/tests/test_weekly_bars.py  # ファイル単位
.venv/bin/python3 -m pytest -k "test_single_week"         # 特定テストのみ
```
