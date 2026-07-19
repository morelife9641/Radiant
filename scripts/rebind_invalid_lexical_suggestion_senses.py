#!/usr/bin/env python3
"""Rebind only stale lexical-suggestion sense IDs after a sense repair."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
SUGGESTIONS_PATH = ROOT / "tmp/cloud_import_ielts_content_words/word_lexical_suggestions.json"
REPORT_PATH = ROOT / "tmp/cloud_import_ielts_content_words/rebind_invalid_lexical_suggestion_senses_report.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n", encoding="utf-8")


def main() -> None:
    spec = importlib.util.spec_from_file_location("binder", ROOT / "scripts/auto_bind_lexical_suggestion_senses.py")
    assert spec and spec.loader
    binder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(binder)

    words = read_jsonl(WORDS_PATH)
    suggestions = read_jsonl(SUGGESTIONS_PATH)
    words_by_id = {str(row.get("_id") or ""): row for row in words}
    changes: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for item in suggestions:
        scope = item.get("senseScope") if isinstance(item.get("senseScope"), dict) else {}
        old_id = str(scope.get("fromSenseId") or "")
        word_id = str(item.get("wordId") or "")
        word_doc = words_by_id.get(word_id)
        valid = {str(sense.get("senseId") or "") for sense in (word_doc or {}).get("senses") or []}
        if not old_id or old_id in valid:
            continue
        if not word_doc:
            unresolved.append({"id": item.get("_id"), "reason": "missing_word", "wordId": word_id})
            continue
        new_id, score, method = binder.choose_sense(item, word_doc, words_by_id)
        if not new_id:
            unresolved.append({"id": item.get("_id"), "reason": method, "oldSenseId": old_id})
            continue
        scope["fromSenseId"] = new_id
        item["senseScope"] = scope
        changes.append({"id": item.get("_id"), "word": item.get("word"), "targetWord": item.get("targetWord"), "oldSenseId": old_id, "newSenseId": new_id, "method": method, "score": score})

    write_jsonl(SUGGESTIONS_PATH, suggestions)
    REPORT_PATH.write_text(json.dumps({"changedCount": len(changes), "unresolvedCount": len(unresolved), "changes": changes, "unresolved": unresolved}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"changed: {len(changes)}")
    print(f"unresolved: {len(unresolved)}")


if __name__ == "__main__":
    main()
