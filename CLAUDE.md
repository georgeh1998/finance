# finance プロジェクト

## Python 環境

- Python コマンドは必ず `python3` / `pip3` を使う（`python` / `pip` は使わない）
- パッケージ管理は `pip3` を使う
- 仮想環境を使う場合は `python3 -m venv` で作成する

## よく使うコマンド

```bash
# パッケージ情報の確認
pip3 index versions <package>

# パッケージのインストール
pip3 install <package>
pip3 install -r requirements.txt

# パッケージのダウンロード（オフライン用）
pip3 download <package>

# インストール済みパッケージの確認
pip3 list
pip3 show <package>
```
