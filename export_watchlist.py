"""
GitHubのスキャン結果IssueからTradingViewウォッチリスト用TXTを生成する。
出力形式: TSE:1234 をカンマ区切りで1行に並べる

使い方:
  .venv/bin/python3 export_watchlist.py [issue番号] [出力ファイル] [オプション]

オプション:
  --trend uptrend|downtrend   トレンドで絞り込む
  --min-price 1000            最低株価
  --max-price 2000            最高株価

例:
  .venv/bin/python3 export_watchlist.py 3 watchlist.txt --trend uptrend --max-price 2000
"""

import argparse
import json
import re
import subprocess
import sys


def fetch_issue_body(issue_number: int, repo: str) -> str:
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number), "--repo", repo, "--json", "body"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)["body"]


def parse_rows(body: str) -> list[dict]:
    rows = []
    for line in body.splitlines():
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) < 5:
            continue
        code = cells[0]
        if not re.fullmatch(r"[0-9A-Z]+", code) or code.lower() == "code":
            continue
        try:
            price = float(cells[2].replace(",", ""))
            trend = cells[4].strip()
        except (ValueError, IndexError):
            continue
        rows.append({"code": code, "price": price, "trend": trend})
    return rows


def to_tradingview_symbols(codes: list[str]) -> list[str]:
    return [f"TSE:{code}" for code in codes]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("issue", nargs="?", type=int, default=3)
    parser.add_argument("output", nargs="?", default="watchlist.txt")
    parser.add_argument("--trend", choices=["uptrend", "downtrend"])
    parser.add_argument("--min-price", type=float)
    parser.add_argument("--max-price", type=float)
    args = parser.parse_args()

    repo = "georgeh1998/finance"
    print(f"Issue #{args.issue} を取得中...")
    body = fetch_issue_body(args.issue, repo)

    rows = parse_rows(body)
    if not rows:
        print("銘柄が見つかりませんでした。")
        sys.exit(1)

    if args.trend:
        rows = [r for r in rows if r["trend"] == args.trend]
    if args.min_price is not None:
        rows = [r for r in rows if r["price"] >= args.min_price]
    if args.max_price is not None:
        rows = [r for r in rows if r["price"] <= args.max_price]

    if not rows:
        print("フィルタ条件に一致する銘柄がありませんでした。")
        sys.exit(1)

    symbols = to_tradingview_symbols([r["code"] for r in rows])
    print(f"{len(symbols)} 銘柄を取得しました。")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(",".join(symbols))

    print(f"{args.output} に書き出しました。")
    print(f"先頭5件: {symbols[:5]}")


if __name__ == "__main__":
    main()
