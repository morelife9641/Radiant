#!/usr/bin/env python3
"""Migrate word_relations senseScope IDs after words.senses normalization."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
RELATIONS_PATH = ROOT / "tmp/cloud_import_ielts_content_words/word_relations.json"
REPORT_PATH = ROOT / "tmp/cloud_import_ielts_content_words/migrate_word_relation_sense_ids_report.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def normalize_pos(pos: str) -> str:
    value = str(pos or "").lower().strip().rstrip(".")
    return {"adj": "a", "vt": "v", "vi": "v"}.get(value, value)


def pos_from_old_sense_id(sense_id: str) -> str:
    match = re.search(r"_(adj|adv|prep|conj|pron|excl|vt|vi|n|v|a)_\d+$", str(sense_id or ""))
    return normalize_pos(match.group(1)) if match else ""


def choose_new_sense_id(word_doc: dict[str, Any] | None, old_sense_id: str) -> str:
    if not word_doc:
        return ""
    senses = word_doc.get("senses") or []
    valid = {str(sense.get("senseId") or "") for sense in senses}
    if old_sense_id in valid:
        return old_sense_id
    wanted_pos = pos_from_old_sense_id(old_sense_id)
    if wanted_pos:
        matching = [
            str(sense.get("senseId") or "")
            for sense in senses
            if normalize_pos(str(sense.get("pos") or "")) == wanted_pos
        ]
        matching = [item for item in matching if item]
        if len(matching) == 1:
            return matching[0]
    if str(old_sense_id or "").endswith("_sense_01") and len(senses) == 1:
        return str(senses[0].get("senseId") or "")
    return ""


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    relations = read_jsonl(RELATIONS_PATH)
    words_by_id = {row.get("_id"): row for row in words}
    changes: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for relation in relations:
        scope = relation.get("senseScope") if isinstance(relation.get("senseScope"), dict) else {}
        if not isinstance(scope, dict):
            continue
        relation_id_before = str(relation.get("_id") or "")
        for side in ("from", "to"):
            word_id = str(relation.get(f"{side}WordId") or "")
            key = f"{side}SenseId"
            old_sense_id = str(scope.get(key) or "")
            if not old_sense_id:
                continue
            new_sense_id = choose_new_sense_id(words_by_id.get(word_id), old_sense_id)
            if not new_sense_id:
                unresolved.append(
                    {
                        "id": relation.get("_id"),
                        "side": side,
                        "wordId": word_id,
                        "word": relation.get(f"{side}Word"),
                        "oldSenseId": old_sense_id,
                    }
                )
                continue
            if new_sense_id != old_sense_id:
                scope[key] = new_sense_id
                if relation.get("_id"):
                    relation["_id"] = str(relation["_id"]).replace(old_sense_id, new_sense_id)
                changes.append(
                    {
                        "idBefore": relation_id_before,
                        "idAfter": relation.get("_id"),
                        "side": side,
                        "wordId": word_id,
                        "word": relation.get(f"{side}Word"),
                        "oldSenseId": old_sense_id,
                        "newSenseId": new_sense_id,
                    }
                )
        if scope.get("pos"):
            scope["pos"] = normalize_pos(str(scope.get("pos") or ""))
        relation["senseScope"] = scope

    write_jsonl(RELATIONS_PATH, relations)
    REPORT_PATH.write_text(
        json.dumps({"changedCount": len(changes), "unresolvedCount": len(unresolved), "changes": changes, "unresolved": unresolved}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"changed: {len(changes)}")
    print(f"unresolved: {len(unresolved)}")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
