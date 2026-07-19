#!/usr/bin/env python3
"""Add five sample short English definitions for review."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
LEARNING_PATH = ROOT / "tmp/cloud_import_ielts_content_words/word_learning_content.json"

SAMPLES = {
    "realm": "A field, area, or sphere of activity or knowledge.",
    "in accordance with": "In agreement with a rule, request, or standard.",
    "refresh": "To make someone or something feel new, active, or energetic again.",
    "consumption": "The act or amount of using, eating, drinking, or buying something.",
    "association": "A connection between people, ideas, events, or things.",
}


def main() -> None:
    rows = [json.loads(line) for line in LEARNING_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    updated = []
    for row in rows:
        key = str(row.get("normalized") or row.get("word") or "").lower()
        if key in SAMPLES:
            row["shortDefinitionEn"] = SAMPLES[key]
            provenance = row.setdefault("provenance", {})
            refinements = provenance.setdefault("refinements", [])
            if "sample_short_definition_en" not in refinements:
                refinements.append("sample_short_definition_en")
            updated.append(key)
    LEARNING_PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(json.dumps({"updated": updated, "count": len(updated)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
