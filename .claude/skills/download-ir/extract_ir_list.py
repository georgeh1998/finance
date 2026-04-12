#!/usr/bin/env python3
"""
IRBank トップページのスナップショットから決算発表資料リストを抽出するスクリプト

使用方法:
  python3 extract_ir_list.py <snapshot_file> [件数=8]

出力 (TSV形式):
  ファイル名\t区分\thref\t提出日
  例: 2026_3_q3\t3Q\t/7458/140120260206550963\t2026/02/09

ファイル名の形式: {決算年度}_{決算月}_{区分}
  例: 2026_3_q3, 2025_3_full

フィルタ: 1Q / 2Q / 3Q / 通期 のみ（修正・配当は除外）
"""

import re
import sys


VALID_CATEGORIES = {"1Q", "2Q", "3Q", "通期", "2Q(中間)"}

CATEGORY_SUFFIX = {
    "1Q": "q1",
    "2Q": "q2",
    "2Q(中間)": "q2",
    "3Q": "q3",
    "通期": "q4",
}


def fiscal_year(date_str: str, category: str, fiscal_month: int) -> int:
    """提出日(YYYY/MM/DD)・区分・決算月から決算年度を返す。
    - 通期: タイトルに記載の年をそのまま使う（rowの文字列から取得済み）
    - 四半期: 提出月が決算月以降→翌年度、決算月より前→同年度
      例(3月決算): 提出2025/08 → 2026年3月期、提出2026/02 → 2026年3月期
      例(12月決算): 提出2025/02 → 2025年12月期、提出2025/08 → 2025年12月期
    """
    year = int(date_str[:4])
    submit_month = int(date_str[5:7])
    if category == "通期":
        return year
    else:
        # 決算月の翌月以降に提出 → 翌年度
        return year if submit_month <= fiscal_month else year + 1


def make_filename(date_str: str, category: str, fiscal_month: int) -> str:
    """提出日・区分・決算月からファイル名（拡張子なし）を生成する。"""
    fy = fiscal_year(date_str, category, fiscal_month)
    suffix = CATEGORY_SUFFIX.get(category, category.lower())
    return f"{fy}_{fiscal_month}_{suffix}"


def extract_ir_list(snapshot_file: str, limit: int = 999) -> list[dict]:
    with open(snapshot_file) as f:
        text = f.read()

    results = []

    # 決算発表資料テーブルの行を解析
    # row "YYYY/MM/DD HH:MM 区分 タイトル" のパターンを探す
    row_pattern = re.compile(
        r'row\s+"(\d{4}/\d{2}/\d{2})\s+\d{2}:\d{2}\s+(1Q|2Q|3Q|通期|2Q\(中間\))\s+\d{4}年(\d{1,2})月期[^"]*"'
    )
    url_pattern = re.compile(r'/url:\s+(/\d+/\d+)')

    lines = text.split("\n")
    i = 0
    while i < len(lines) and len(results) < limit:
        line = lines[i]
        m = row_pattern.search(line)
        if m:
            date_str = m.group(1)   # YYYY/MM/DD
            category = m.group(2)
            fiscal_month = int(m.group(3))  # 決算月（例: 3, 12, 6）

            if category in VALID_CATEGORIES:
                filename = make_filename(date_str, category, fiscal_month)

                # 次の数行から href を探す
                href = None
                for j in range(i + 1, min(i + 10, len(lines))):
                    um = url_pattern.search(lines[j])
                    if um:
                        href = um.group(1)
                        break

                if href:
                    results.append({
                        "filename": filename,
                        "date": date_str,
                        "category": category,
                        "href": href,
                    })
        i += 1

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 extract_ir_list.py <snapshot_file> [件数]", file=sys.stderr)
        sys.exit(1)

    snapshot_file = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) >= 3 else 999

    entries = extract_ir_list(snapshot_file, limit)
    if not entries:
        print("決算発表資料が見つかりませんでした", file=sys.stderr)
        sys.exit(1)

    for e in entries:
        print(f"{e['filename']}\t{e['category']}\t{e['href']}\t{e['date']}")
