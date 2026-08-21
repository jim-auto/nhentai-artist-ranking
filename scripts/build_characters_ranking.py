from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from build_favorites_ranking import get_json, summarize

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "characters-ranking.json"


def main() -> None:
    limit = int(os.environ.get("CHARACTER_LIMIT", "100"))
    delay = float(os.environ.get("REQUEST_DELAY", "1.0"))
    cache_path = ROOT / "data" / "characters-cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    detail_path = ROOT / "data" / "gallery-tags-cache.json"
    detail_cache = json.loads(detail_path.read_text(encoding="utf-8")) if detail_path.exists() else {}
    tags = get_json("/tags/character?page=1")
    characters = tags["result"][:limit]
    rows = []
    requests = 1
    for index, character in enumerate(characters, 1):
        key = str(character["id"])
        if key in cache and cache[key].get("tag_sampled"):
            row = cache[key]
            rows.append(row)
            print(f"[{index}/{len(characters)}] {character['name']}: cached", flush=True)
            continue
        if index > 1:
            time.sleep(delay)
        pages = get_json(f"/galleries/tagged?tag_id={character['id']}&sort=popular&page=1")
        requests += 1
        favorites, top_tags, detail_requests = summarize(pages.get("result", []), detail_cache)
        requests += detail_requests
        row = {
            "character": character["name"], "tag_id": character["id"],
            "character_url": "https://nhentai.net" + character["url"],
            "galleries": len(favorites), "favorites": sum(favorites),
            "median_favorites": favorites[len(favorites) // 2] if favorites else 0,
            "top_favorites": favorites[0] if favorites else 0, "top_tags": top_tags,
            "tag_sampled": True,
        }
        rows.append(row)
        cache[key] = row
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        detail_path.write_text(json.dumps(detail_cache, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"[{index}/{len(characters)}] {character['name']}: {len(favorites)} galleries", flush=True)
    rows.sort(key=lambda x: (-x["favorites"], -x["median_favorites"], x["character"].lower()))
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "source": "https://nhentai.net/api/v2",
        "metric_note": "characterタグ掲載数上位を対象に、sort=popularで返る上位25作品のnum_favoritesを合計。主要タグは人気上位2作品の詳細に含まれるtag型タグ。",
        "coverage": {"character_limit": limit, "character_tags_total": tags.get("total"), "api_requests": requests},
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
