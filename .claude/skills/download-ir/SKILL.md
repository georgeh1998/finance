---
name: download-ir
description: IRBankから企業の四半期決算書PDFを自動ダウンロードするスキル。`/download-ir <証券コード>` または「7203の決算書をダウンロードして」「IRBankからPDFを取得して」など、決算書PDFの取得を求められたときに使う。Playwright MCPを使ってhttps://irbank.net をスクレイピングし、company/<証券コード>/ 配下に {決算年度}_{決算月}_{区分}.pdf 形式で保存する（例: 2026_3_q3.pdf、2025_12_q4.pdf）。
subagent: true
tools:
  - mcp__playwright__* (ブラウザ操作・スクレイピング)
  - Bash (Pythonスクリプトの実行のみ)
  - Write
  - Glob
---

# IRBank 決算書PDFダウンロードスキル

## 概要

Playwright MCPを使って `https://irbank.net/<証券コード>` から四半期・通期決算書のPDFリンクを取得し、
`company/<証券コード>/{決算年度}_{決算月}_{区分}.pdf` 形式で保存する。

**ファイル名の形式：** `{決算年度}_{決算月}_{区分}.pdf`
- 区分: `q1` / `q2` / `q3` / `q4`（通期）
- 例: `2026_3_q3.pdf`（3月決算）、`2025_12_q4.pdf`（12月決算）

**デフォルト**: ページに表示されているすべての件数（件数を指定した場合はその件数まで）

---

## Step 1: 保存先ディレクトリの準備

```bash
mkdir -p company/<証券コード>
```

---

## Step 1.5: ブラウザのウォームアップ（必須）

**最初のナビゲート前に必ずこのステップを実行する。**

ブラウザが閉じた状態だと最初の `browser_navigate` が `Target page, context or browser has been closed` エラーで失敗することがある。これを防ぐため、IRBankへのナビゲート前に `about:blank` へアクセスしてブラウザを起動する：

1. `mcp__playwright__browser_navigate` で `about:blank` を開く
2. エラーが出た場合も気にせず次に進む（ブラウザが起動していれば成功）

---

## Step 2: IRBankで決算書リストを取得

Playwright MCPツールを使って以下を行う：

1. `mcp__playwright__browser_navigate` で `https://irbank.net/<証券コード>` を開く
2. `mcp__playwright__browser_snapshot` でスナップショットを取得（ファイルに保存される）
3. スナップショットファイルのパスを確認し、以下のスクリプトで決算リストを抽出する：

```bash
python3 .claude/skills/download-ir/extract_ir_list.py <snapshot_file> [件数]
```

出力は TSV 形式（タブ区切り）：
```
2026_3_q3  3Q   /7458/140120260206550963  2026/02/09
2026_3_q2  2Q   /7458/140120251110593238  2025/11/10
...
```

**フィルタ条件：**
- 区分が `1Q` / `2Q` / `3Q` / `通期` / `2Q(中間)` のもののみ
- 修正・配当は除外
- 引数省略時はページに表示されているすべてを取得（引数で上限を指定可能）

---

## Step 3: 各決算書ページでPDF URLを取得

各エントリの href に対して：

1. `mcp__playwright__browser_navigate` で `https://irbank.net<href>` を開く
2. `mcp__playwright__browser_snapshot` でスナップショット取得（ファイルに保存される）
3. 以下のスクリプトで PDF URL を抽出する：

```bash
python3 .claude/skills/download-ir/extract_pdf_url.py <snapshot_file>
```

PDF URLのパターン：
```
https://f.irbank.net/pdf/YYYYMMDD/<文書ID>.pdf
```

---

## Step 4: PDFをダウンロード

PDF URLが取得できたら `pdf-download.py` でダウンロードする：

```bash
python3 .claude/skills/download-ir/pdf-download.py "<PDF URL>" "company/<証券コード>/<filename>.pdf"
```

**ファイル名はStep 2のTSV出力の1列目をそのまま使う：**
- `2026_3_q3` → `company/7458/2026_3_q3.pdf`

**既存ファイルの扱い：**
- すでに同名ファイルが存在する場合はスキップして「既存」と報告

---

## Step 5: 結果の報告

完了後、ユーザーに以下の形式で報告する：

```
ダウンロード完了: <企業名>（<証券コード>）

保存先: company/<証券コード>/

  2026_3_q3.pdf  3Q決算   (2026/02/09)
  2026_3_q2.pdf  2Q決算   (2025/11/10)
  2026_3_q1.pdf  1Q決算   (2025/08/07)
  2025_3_q4.pdf  通期決算  (2025/05/12)
  ...

合計: N件
```

---

## Step 6: ブラウザを閉じる（必須）

**スキル終了時に必ず実行する。**

`mcp__playwright__browser_close` を呼び出してブラウザを閉じる。
これにより次回実行時に「Target page, context or browser has been closed」エラーが発生しなくなる。

---

## エラーハンドリング

| エラー | 対処 |
|--------|------|
| `Target page, context or browser has been closed` | Step 1.5 のウォームアップが抜けていた可能性あり。`about:blank` にナビゲートしてから再試行。前回スキル終了時に `browser_close` を忘れた場合も同様 |
| 証券コードが存在しない（404等） | ユーザーに証券コードを確認 |
| PDFリンクが見つからない | そのエントリをスキップしてログに記録 |
| ダウンロード失敗 | 最大3回リトライ後スキップ |

---

## 使用例

```
/download-ir 7203       ← トヨタ（ページに表示されている全件）
/download-ir 9984       ← ソフトバンクG
/download-ir 7458 4     ← 第一興商（4件のみ）
```
