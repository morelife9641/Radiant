#!/usr/bin/env python3
"""Clean auxiliary definitions after mixed-POS sense splitting."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
REPORT_PATH = ROOT / "tmp/cloud_import_ielts_content_words/clean_split_sense_auxiliary_definitions_report.json"

BAD_VT_VI_RE = re.compile(r"(?<![A-Za-z])([it])\.\s*")
POS_RE = re.compile(r"\b(adj|adv|prep|conj|pron|excl|vt|vi|n|v|a)(?:\./|/)?\.?\s*", re.I)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def clean_definition_zh(value: str) -> str:
    text = str(value or "")
    # Repair the previous vt/vi parsing bug where "vi." became "i." and
    # "vt." became "t."; after splitting, the marker itself adds no value.
    text = BAD_VT_VI_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip(" ;；")


def has_mismatched_pos_marker(value: str, pos: str) -> bool:
    text = str(value or "")
    markers = {m.group(1).lower() for m in POS_RE.finditer(text)}
    if not markers:
        return False
    normalized = {"adj": "a", "vt": "v", "vi": "v"}.get(pos, pos)
    normalized_markers = {{"adj": "a", "vt": "v", "vi": "v"}.get(item, item) for item in markers}
    return normalized not in normalized_markers


def main() -> None:
    rows = read_jsonl(WORDS_PATH)
    changed: list[dict[str, Any]] = []

    for row in rows:
        senses = row.get("senses") or []
        if len(senses) <= 1:
            continue
        for sense in senses:
            before = {
                "definitionEn": sense.get("definitionEn"),
                "definitionZh": sense.get("definitionZh"),
            }
            pos = str(sense.get("pos") or "").lower().strip()
            if has_mismatched_pos_marker(str(sense.get("definitionEn") or ""), pos):
                sense["definitionEn"] = ""
            if has_mismatched_pos_marker(str(sense.get("definitionZh") or ""), pos):
                sense["definitionZh"] = ""
            if sense.get("definitionZh"):
                sense["definitionZh"] = clean_definition_zh(str(sense.get("definitionZh") or ""))
            after = {
                "definitionEn": sense.get("definitionEn"),
                "definitionZh": sense.get("definitionZh"),
            }
            if before != after:
                changed.append(
                    {
                        "wordId": row.get("_id"),
                        "word": row.get("word"),
                        "senseId": sense.get("senseId"),
                        "pos": sense.get("pos"),
                        "before": before,
                        "after": after,
                    }
                )

    write_jsonl(WORDS_PATH, rows)
    REPORT_PATH.write_text(
        json.dumps({"changedCount": len(changed), "changed": changed}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"changed: {len(changed)}")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
