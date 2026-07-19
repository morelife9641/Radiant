#!/usr/bin/env python3
"""Remap relation sense IDs after broad POS splits of remaining candidates."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
RELATIONS_PATH = DATA_DIR / "word_relations.json"
REPORT_PATH = DATA_DIR / "remaining_pos_split_relation_remap_report.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def old_pos_from_sense_id(sense_id: str) -> str:
    match = re.search(r"_(vt|vi|v|n|adj|a|adv|prep|conj|pron|sense)_\d+$", sense_id)
    if not match:
        return ""
    pos = match.group(1)
    return "a" if pos == "adj" else pos


def candidate_new_sense(word_doc: dict[str, Any], old_sense_id: str, scope_pos: str) -> str | None:
    senses = word_doc.get("senses") or []
    valid = {sense.get("senseId") for sense in senses}
    if old_sense_id in valid:
        return old_sense_id

    old_pos = old_pos_from_sense_id(old_sense_id)
    scope_pos = str(scope_pos or "").lower().replace("adj", "a").rstrip(".")
    desired = old_pos or scope_pos
    if desired == "sense":
        desired = scope_pos

    exact = [sense for sense in senses if str(sense.get("pos") or "").lower() == desired]
    if exact:
        return exact[0].get("senseId")

    if desired == "v":
        for pos in ("v", "vt", "vi"):
            match = [sense for sense in senses if str(sense.get("pos") or "").lower() == pos]
            if match:
                return match[0].get("senseId")
    if desired in {"vt", "vi"}:
        for pos in (desired, "v", "vt", "vi"):
            match = [sense for sense in senses if str(sense.get("pos") or "").lower() == pos]
            if match:
                return match[0].get("senseId")
    if desired == "a":
        match = [sense for sense in senses if str(sense.get("pos") or "").lower() in {"a", "adj"}]
        if match:
            return match[0].get("senseId")

    return senses[0].get("senseId") if senses else None


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    relations = read_jsonl(RELATIONS_PATH)
    words_by_id = {row["_id"]: row for row in words}
    valid = {row["_id"]: {sense.get("senseId") for sense in row.get("senses") or []} for row in words}
    updates: list[dict[str, str]] = []

    for rel in relations:
        scope = rel.get("senseScope")
        if not isinstance(scope, dict):
            continue
        for side in ("from", "to"):
            word_id = rel.get(f"{side}WordId")
            old = scope.get(f"{side}SenseId")
            if not word_id or not old or old in valid.get(word_id, set()):
                continue
            new = candidate_new_sense(words_by_id.get(word_id, {}), str(old), str(scope.get("pos") or ""))
            if not new:
                continue
            scope[f"{side}SenseId"] = new
            updates.append(
                {
                    "relationId": rel.get("_id", ""),
                    "wordId": str(word_id),
                    "word": str(rel.get(f"{side}Word") or ""),
                    "old": str(old),
                    "new": str(new),
                }
            )

    remaining_invalid = []
    for rel in relations:
        scope = rel.get("senseScope") or {}
        for side in ("from", "to"):
            word_id = rel.get(f"{side}WordId")
            sid = scope.get(f"{side}SenseId")
            if word_id in valid and sid and sid not in valid[word_id]:
                remaining_invalid.append({"relationId": rel.get("_id", ""), "wordId": word_id, "senseId": sid})

    write_jsonl(RELATIONS_PATH, relations)
    REPORT_PATH.write_text(
        json.dumps({"updatedCount": len(updates), "remainingInvalid": remaining_invalid, "updates": updates}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"updated relation scopes: {len(updates)}")
    print(f"remaining invalid: {len(remaining_invalid)}")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
