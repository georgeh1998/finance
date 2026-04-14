# Claude Code 設定

## プロジェクト概要

Python製の株式バックテストツール。日本株（個別株）を対象に、移動平均クロス戦略でバックテストを実行する。
yfinance でデータ取得、Backtesting.py でバックテスト実行。データソース・ストラテジーは差し替え可能な設計。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## テスト

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

## 実行

```bash
source .venv/bin/activate
python main.py --symbol 7203.T --period 1y
python main.py --symbol 7203.T --period 2y --short 10 --long 50 --chart result.html
```

## ファイル操作

- `.claude` フォルダ内のファイルを操作する際は、Bash の `echo` や `cat` ではなく、必ず `Edit` または `Write` ツールを使うこと。
