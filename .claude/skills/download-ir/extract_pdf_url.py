#!/usr/bin/env python3
"""
IRBank スナップショットファイルから PDF URL を抽出するスクリプト

使用方法:
  python3 extract_pdf_url.py <snapshot_file>

出力:
  PDF URLが見つかった場合: その URL を標準出力に出力
  見つからなかった場合: 空文字列を出力して終了コード 1
"""

import re
import sys


def extract_pdf_url(snapshot_file: str) -> str | None:
    with open(snapshot_file) as f:
        text = f.read()

    for line in text.split("\n"):
        if "f.irbank.net/pdf/" in line:
            m = re.search(r'https://f\.irbank\.net/pdf/\S+\.pdf', line)
            if m:
                return m.group(0)
    return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python3 extract_pdf_url.py <snapshot_file>", file=sys.stderr)
        sys.exit(1)

    url = extract_pdf_url(sys.argv[1])
    if url:
        print(url)
        sys.exit(0)
    else:
        sys.exit(1)
