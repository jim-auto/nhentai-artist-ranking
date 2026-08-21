from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "favorites-ranking.json"
API = "https://nhentai.net/api/v2"
USER_AGENT = "nhentai-artist-ranking/1.0 (metadata research; contact via GitHub)"


def get_json(path: str) -> dict:
    for attempt in range(7):
        result = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "30", "-A", USER_AGENT,
             "-H", "Accept: application/json", "-w", "\n%{http_code}", API + path],
            capture_output=True, check=False,
        )
        body, status = result.stdout.rsplit(b"\n", 1)
        if status == b"200":
            return json.loads(body)
        if status != b"429" or attempt == 6:
            raise RuntimeError(f"API request failed ({status.decode(errors='replace')}): {path}")
        else:
            wait = min(120, 10 * (2 ** attempt))
            print(f"rate limited; waiting {wait}s", flush=True)
            time.sleep(wait)


def main() -> None:
    limit = int(os.environ.get("ARTIST_LIMIT", "100"))
    delay = float(os.environ.get("REQUEST_DELAY", "1.0"))
    cache_path = ROOT / "data" / "favorites-cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    tags = get_json("/tags/artist?page=1")
    artists = tags["result"][:limit]
    rows = []
    requests = 1
    for index, artist in enumerate(artists, 1):
        if str(artist["id"]) in cache:
            cached = cache[str(artist["id"])]
            cached["artist_url"] = "https://nhentai.net" + artist["url"]
            rows.append(cached)
            print(f"[{index}/{len(artists)}] {artist['name']}: cached", flush=True)
            continue
        if index > 1:
            time.sleep(delay)
        favorites = []
        pages = get_json(f"/galleries/tagged?tag_id={artist['id']}&sort=popular&page=1")
        requests += 1
        for gallery in pages.get("result", []):
            favorites.append(int(gallery.get("num_favorites") or 0))
        # Only the first page is sampled: sort=popular places the 25 most-favorited
        # galleries first, keeping the public update job small and polite.
        favorites.sort(reverse=True)
        total = sum(favorites)
        median = favorites[len(favorites) // 2] if favorites else 0
        row = {
            "artist": artist["name"], "tag_id": artist["id"], "artist_url": "https://nhentai.net" + artist["url"],
            "galleries": len(favorites), "favorites": total,
            "median_favorites": median, "top_favorites": favorites[0] if favorites else 0,
        }
        rows.append(row)
        cache[str(artist["id"])] = row
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"[{index}/{len(artists)}] {artist['name']}: {len(favorites)} galleries", flush=True)
    rows.sort(key=lambda x: (-x["favorites"], -x["median_favorites"], x["artist"].lower()))
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "https://nhentai.net/api/v2",
        "metric_note": "artistタグ掲載数上位を対象に、sort=popularで返る上位25作品のnum_favoritesを合計。全作品の完全合計ではありません。",
        "coverage": {"artist_limit": limit, "artist_tags_total": tags.get("total"), "api_requests": requests},
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
