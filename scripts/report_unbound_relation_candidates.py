#!/usr/bin/env python3
"""Report unbound synonym/semantic candidates from the generated review page."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
HTML_PATH = ROOT / "tmp/ielts_review_tool/ielts_word_inventory.html"
OUT_PATH = ROOT / "tmp/cloud_import_ielts_content_words/unbound_relation_candidates_report.json"


def embedded_rows() -> list[dict[str, Any]]:
    text = HTML_PATH.read_text(encoding="utf-8")
    start = text.index("const rows = ") + len("const rows = ")
    end = text.index(";\n    const summary", start)
    return json.loads(text[start:end])


def main() -> None:
    rows = embedded_rows()
    items: list[dict[str, Any]] = []
    counts = Counter()
    for row in rows:
        for group in row.get("synonymGroups") or []:
            if group.get("senseId"):
                continue
            for item in group.get("items") or []:
                counts[row["word"]] += 1
                items.append(
                    {
                        "word": row["word"],
                        "wordId": row["wordId"],
                        "targetWord": item.get("text"),
                        "sourceKind": item.get("sourceKind"),
                        "sourceId": item.get("sourceId"),
                        "senses": row.get("senses") or [],
                    }
                )
    report = {
        "wordCount": len(counts),
        "itemCount": len(items),
        "topWords": counts.most_common(100),
        "items": items,
    }
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"words: {len(counts)}")
    print(f"items: {len(items)}")
    print(OUT_PATH)


if __name__ == "__main__":
    main()
