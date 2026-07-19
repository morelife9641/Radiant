#!/usr/bin/env python3
"""Append near-synonym suggestions for newdocs-added IELTS words without overwriting existing curation."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
SUGGESTIONS_PATH = DATA_DIR / "word_lexical_suggestions.json"
WORDBOOK_PATH = DATA_DIR / "wordbook_words.json"
REPORT_PATH = DATA_DIR / "newdocs_lexical_suggestions_append_report.json"


def import_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


BASE = import_script("lexical_base", ROOT / "scripts/enrich_ielts_lexical_suggestions.py")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def main() -> None:
    wordbook = read_jsonl(WORDBOOK_PATH)
    global_words = read_jsonl(WORDS_PATH)
    existing = read_jsonl(SUGGESTIONS_PATH)
    existing_ids = {row["_id"] for row in existing}

    wordbook_by_norm = {row["normalized"].lower(): row for row in wordbook}
    new_words = {row["normalized"].lower() for row in wordbook if (row.get("order") or 0) > 1352}
    words_by_norm = {row.get("normalized", row.get("word", "")).lower(): row for row in global_words}

    additions: dict[str, dict[str, Any]] = {}
    resemble_groups = BASE.parse_resemble_groups(BASE.ECDICT_PATH.with_name("resemble.txt"))
    for group in resemble_groups:
        if "这组词" not in (group.get("summaryZh") or ""):
            continue
        terms = [term for term in group["terms"] if term]
        new_terms = [term for term in terms if term in new_words]
        if not new_terms:
            continue
        for word in new_terms:
            for target in terms:
                if target == word:
                    continue
                note_word = group["notes"].get(word, "")
                note_target = group["notes"].get(target, "")
                relation = BASE.make_relation(
                    word=word,
                    target=target,
                    relation_type="near_synonym",
                    words_by_norm=words_by_norm,
                    wordbook_by_norm=wordbook_by_norm,
                    explanation_zh=(
                        f"{word}: {note_word or '与本组词语义接近，需结合语境区分。'}"
                        f"{target}: {note_target or '与本组词语义接近，需结合语境区分。'}"
                    ),
                    example_en=f"Compare \"{word}\" with \"{target}\" in this word family; the exact choice depends on context.",
                    example_zh=f"{word} 和 {target} 属于近义/同类表达，阅读中要根据具体语境区分。",
                    source=f"ecdict_resemble_newdocs:{group['sourceIndex']}",
                    strength=3,
                )
                relation["groupTitle"] = group["title"]
                relation["groupSummaryZh"] = group.get("summaryZh") or ""
                if relation["_id"] not in existing_ids:
                    additions[relation["_id"]] = relation

    for word, targets in BASE.CURATED_NEAR_SYNONYMS.items():
        if word not in new_words:
            continue
        for target in targets:
            relation = BASE.make_relation(
                word=word,
                target=target,
                relation_type="near_synonym",
                words_by_norm=words_by_norm,
                wordbook_by_norm=wordbook_by_norm,
                explanation_zh=f"{word} 与 {target} 在雅思阅读语境中可作为近义或同类表达参考；具体替换需看词性和上下文。",
                example_en=f"In context, \"{word}\" can be compared with \"{target}\", but the exact choice depends on grammar and meaning.",
                example_zh=f"在语境中，{word} 可与 {target} 对照学习，但是否能替换要看词性和上下文。",
                source="curated_gap_fill_newdocs",
                strength=4,
            )
            if relation["_id"] not in existing_ids:
                additions[relation["_id"]] = relation

    rows = sorted(existing + list(additions.values()), key=lambda item: (item.get("word") or "", item.get("relationType") or "", item.get("targetWord") or ""))
    write_jsonl(SUGGESTIONS_PATH, rows)
    report = {
        "newWordCount": len(new_words),
        "existingSuggestions": len(existing),
        "addedSuggestions": len(additions),
        "totalSuggestions": len(rows),
        "byRelationType": {},
        "sample": list(additions.values())[:50],
    }
    for row in additions.values():
        key = row.get("relationType") or "unknown"
        report["byRelationType"][key] = report["byRelationType"].get(key, 0) + 1
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("newWordCount", "existingSuggestions", "addedSuggestions", "totalSuggestions", "byRelationType")}, ensure_ascii=False, indent=2))
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
