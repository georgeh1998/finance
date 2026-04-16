# finance プロジェクト

## Python 環境

- 作業開始時は仮想環境を有効化する: `source .venv/bin/activate`
- 仮想環境がなければ作成する: `python3 -m venv .venv`
- パッケージ操作は `pip3` を使う
- コマンド実行は `python3` を使う

## テスト

```bash
python3 -m pytest                              # 全テスト実行
python3 -m pytest stock/tests/                  # モジュール単位
python3 -m pytest stock/tests/test_weekly_bars.py  # ファイル単位
python3 -m pytest -k "test_single_week"         # 特定テストのみ
```
