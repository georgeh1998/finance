#!/usr/bin/env python3
"""
IRBank PDFダウンローダー
使用方法: python3 pdf-download.py <PDF URL> <保存先パス>
許可ドメイン: f.irbank.net のみ
"""

import sys
import urllib.request
import urllib.parse
import os

ALLOWED_DOMAIN = "f.irbank.net"


def download_pdf(url: str, output_path: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc != ALLOWED_DOMAIN:
        print(f"エラー: 許可されていないドメインです: {parsed.netloc}", file=sys.stderr)
        print(f"許可ドメイン: {ALLOWED_DOMAIN}", file=sys.stderr)
        sys.exit(1)

    if not url.endswith(".pdf"):
        print(f"エラー: PDFファイルのURLではありません: {url}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"ダウンロード中: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response:
        with open(output_path, "wb") as f:
            f.write(response.read())

    size_kb = os.path.getsize(output_path) // 1024
    print(f"保存完了: {output_path} ({size_kb} KB)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python3 pdf-download.py <URL> <保存先パス>", file=sys.stderr)
        sys.exit(1)

    download_pdf(sys.argv[1], sys.argv[2])
