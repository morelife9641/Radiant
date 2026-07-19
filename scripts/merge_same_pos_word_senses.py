#!/usr/bin/env python3
"""Merge same-POS senses while keeping different grammatical POS separate."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
SUGGESTIONS_PATH = ROOT / "tmp/cloud_import_ielts_content_words/word_lexical_suggestions.json"
RELATIONS_PATH = ROOT / "tmp/cloud_import_ielts_content_words/word_relations.json"
REPORT_PATH = ROOT / "tmp/cloud_import_ielts_content_words/merge_same_pos_word_senses_report.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n", encoding="utf-8")


def join_unique(values: list[Any]) -> str:
    parts: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in parts:
            parts.append(text)
    return "；".join(parts)


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    suggestions = read_jsonl(SUGGESTIONS_PATH)
    relations = read_jsonl(RELATIONS_PATH)
    remap: dict[tuple[str, str], str] = {}
    merged: list[dict[str, Any]] = []

    for word in words:
        senses = word.get("senses") or []
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        ordered_pos: list[str] = []
        for sense in senses:
            pos = str(sense.get("pos") or "")
            if pos not in groups:
                ordered_pos.append(pos)
            groups[pos].append(sense)

        next_senses: list[dict[str, Any]] = []
        for pos in ordered_pos:
            group = groups[pos]
            primary = dict(group[0])
            if len(group) == 1:
                next_senses.append(primary)
                continue
            primary["translation"] = join_unique([item.get("translation") for item in group])
            primary["definitionEn"] = join_unique([item.get("definitionEn") for item in group])
            primary["definitionZh"] = join_unique([item.get("definitionZh") for item in group])
            primary_id = str(primary.get("senseId") or "")
            for item in group[1:]:
                old_id = str(item.get("senseId") or "")
                if old_id and primary_id:
                    remap[(str(word.get("_id") or ""), old_id)] = primary_id
            next_senses.append(primary)
            merged.append({
                "wordId": word.get("_id"),
                "word": word.get("word"),
                "pos": pos,
                "keptSenseId": primary_id,
                "mergedSenseIds": [item.get("senseId") for item in group[1:]],
            })
        word["senses"] = next_senses

    suggestion_changes = 0
    for item in suggestions:
        scope = item.get("senseScope") if isinstance(item.get("senseScope"), dict) else {}
        key = (str(item.get("wordId") or ""), str(scope.get("fromSenseId") or ""))
        if key in remap:
            scope["fromSenseId"] = remap[key]
            item["senseScope"] = scope
            suggestion_changes += 1

    relation_changes = 0
    for item in relations:
        scope = item.get("senseScope") if isinstance(item.get("senseScope"), dict) else {}
        for side in ("from", "to"):
            key_name = f"{side}SenseId"
            key = (str(item.get(f"{side}WordId") or ""), str(scope.get(key_name) or ""))
            if key not in remap:
                continue
            old_id = key[1]
            new_id = remap[key]
            scope[key_name] = new_id
            if item.get("_id"):
                item["_id"] = str(item["_id"]).replace(old_id, new_id)
            relation_changes += 1
        item["senseScope"] = scope

    write_jsonl(WORDS_PATH, words)
    write_jsonl(SUGGESTIONS_PATH, suggestions)
    write_jsonl(RELATIONS_PATH, relations)
    REPORT_PATH.write_text(json.dumps({
        "mergedGroupCount": len(merged),
        "mergedSenseCount": len(remap),
        "lexicalSuggestionChanges": suggestion_changes,
        "relationChanges": relation_changes,
        "merged": merged,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mergedGroups": len(merged), "mergedSenses": len(remap), "suggestions": suggestion_changes, "relations": relation_changes}, ensure_ascii=False))


if __name__ == "__main__":
    main()
