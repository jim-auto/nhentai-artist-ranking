from __future__ import annotations

import csv
import json
import math
import os
import re
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "ranking.json"
BASE = "https://raw.githubusercontent.com/van-geaux/unofficial-nhentai-api/main/by_month/"


def months() -> list[str]:
    # The source repository currently starts at 2014-06.
    return [f"{year:04d}-{month:02d}" for year in range(2014, datetime.now().year + 1)
            for month in range(1, 13) if not (year == 2014 and month < 6)
            and (year, month) <= (datetime.now().year, datetime.now().month)]


def download_sources() -> list[Path]:
    RAW.mkdir(parents=True, exist_ok=True)
    paths = []
    for month in months():
        path = RAW / f"{month}.csv"
        if not path.exists():
            print(f"download {month}")
            urllib.request.urlretrieve(BASE + path.name, path)
        paths.append(path)
    return paths


def split_artists(value: str) -> list[str]:
    value = (value or "").strip()
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


def main() -> None:
    paths = download_sources()
    now = datetime.now(timezone.utc)
    cutoff = now.timestamp() - 365 * 24 * 60 * 60
    stats = defaultdict(lambda: {"galleries": 0, "pages": 0, "recent": 0})
    source_rows = 0
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as fp:
            for row in csv.DictReader(fp):
                source_rows += 1
                try:
                    pages = max(0, int(row.get("PAGES") or 0))
                except ValueError:
                    pages = 0
                try:
                    uploaded = datetime.strptime(row.get("UPLOAD_DATE", ""), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
                except ValueError:
                    uploaded = 0
                for artist in split_artists(row.get("ARTIST", "")):
                    item = stats[artist]
                    item["galleries"] += 1
                    item["pages"] += pages
                    if uploaded >= cutoff:
                        item["recent"] += 1
    # Log-scaled secondary signals prevent very prolific artists from dominating every dimension.
    rows = []
    for artist, item in stats.items():
        score = (100 * math.log1p(item["galleries"])
                 + 8 * math.log1p(item["pages"])
                 + 20 * math.log1p(item["recent"]))
        rows.append({"artist": artist, **item, "score": round(score, 2)})
    rows.sort(key=lambda x: (-x["galleries"], -x["recent"], x["artist"].lower()))
    payload = {
        "generated_at": now.isoformat(),
        "source": "https://github.com/van-geaux/unofficial-nhentai-api",
        "coverage": {"months": len(paths), "source_rows": source_rows, "artists": len(rows)},
        "metric_note": "作品数を主軸にした掲載規模ランキング。favorites/views に基づく利用者人気ランキングではありません。",
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT} ({len(rows)} artists, {source_rows} rows)")


if __name__ == "__main__":
    main()

