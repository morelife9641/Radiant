#!/usr/bin/env python3
"""Report remaining IELTS wordbook entries whose single sense still mixes POS."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
WORDBOOK_WORDS_PATH = DATA_DIR / "wordbook_words.json"
REPORT_PATH = DATA_DIR / "remaining_mixed_pos_sense_candidates.json"

POS_RE = re.compile(r"\b(n|vt|vi|v|a|adj|adv|prep|conj|pron)\.", re.I)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalized_pos(pos: str) -> str:
    value = pos.lower()
    return "a" if value == "adj" else value


def main() -> None:
    wordbook_word_ids = {row["wordId"] for row in read_jsonl(WORDBOOK_WORDS_PATH)}
    rows = read_jsonl(WORDS_PATH)
    candidates: list[dict[str, Any]] = []

    for row in rows:
        if row["_id"] not in wordbook_word_ids:
            continue
        senses = row.get("senses") or []
        if len(senses) != 1:
            continue
        sense = senses[0]
        text = f"{sense.get('translation') or ''}\n{sense.get('definitionZh') or ''}"
        found: list[str] = []
        for match in POS_RE.finditer(text):
            pos = normalized_pos(match.group(1))
            if pos not in found:
                found.append(pos)
        if len(found) < 2:
            continue
        candidates.append(
            {
                "word": row["word"],
                "wordId": row["_id"],
                "currentSenseId": sense.get("senseId"),
                "detectedPos": found,
                "currentPos": sense.get("pos"),
                "translation": sense.get("translation"),
                "definitionZh": sense.get("definitionZh"),
            }
        )

    REPORT_PATH.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"remaining candidates: {len(candidates)}")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
