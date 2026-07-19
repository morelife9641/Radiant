#!/usr/bin/env python3
"""Audit words.senses structure for the IELTS content import."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
SUGGESTIONS_PATH = ROOT / "tmp/cloud_import_ielts_content_words/word_lexical_suggestions.json"
RELATIONS_PATH = ROOT / "tmp/cloud_import_ielts_content_words/word_relations.json"
REPORT_PATH = ROOT / "tmp/cloud_import_ielts_content_words/word_sense_structure_audit.json"

POS_MARKER_RE = re.compile(r"\b(adj|adv|prep|conj|pron|excl|vt|vi|n|v|a)(?:\./|/)?\.?\s+", re.I)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize_pos(pos: Any) -> str:
    value = str(pos or "").lower().strip().rstrip(".")
    return {"adj": "a", "vt": "v", "vi": "v"}.get(value, value)


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    suggestions = read_jsonl(SUGGESTIONS_PATH)
    relations = read_jsonl(RELATIONS_PATH)
    words_by_id = {row.get("_id"): row for row in words}
    valid_sense_ids = {
        row.get("_id"): {str(sense.get("senseId") or "") for sense in row.get("senses") or []}
        for row in words
    }

    issues: dict[str, list[dict[str, Any]]] = {
        "missingSenses": [],
        "missingSenseId": [],
        "duplicateSenseId": [],
        "missingPos": [],
        "emptyTranslation": [],
        "translationStillHasPosMarker": [],
        "definitionLooksLikeBrokenVtViMarker": [],
        "lexicalSuggestionInvalidSenseId": [],
        "wordRelationInvalidSenseId": [],
    }

    pos_counts: Counter[str] = Counter()
    multi_sense_count = 0

    for row in words:
        word_id = str(row.get("_id") or "")
        senses = row.get("senses") or []
        if not senses:
            issues["missingSenses"].append({"wordId": word_id, "word": row.get("word")})
            continue
        if len(senses) > 1:
            multi_sense_count += 1
        seen: set[str] = set()
        for sense in senses:
            sense_id = str(sense.get("senseId") or "")
            pos = normalize_pos(sense.get("pos"))
            pos_counts[pos or "(empty)"] += 1
            translation = str(sense.get("translation") or "").strip()
            definition_zh = str(sense.get("definitionZh") or "")
            if not sense_id:
                issues["missingSenseId"].append({"wordId": word_id, "word": row.get("word"), "pos": sense.get("pos")})
            elif sense_id in seen:
                issues["duplicateSenseId"].append({"wordId": word_id, "word": row.get("word"), "senseId": sense_id})
            seen.add(sense_id)
            if not pos:
                issues["missingPos"].append({"wordId": word_id, "word": row.get("word"), "senseId": sense_id})
            if not translation:
                issues["emptyTranslation"].append({"wordId": word_id, "word": row.get("word"), "senseId": sense_id, "pos": sense.get("pos")})
            if POS_MARKER_RE.search(translation):
                issues["translationStillHasPosMarker"].append(
                    {
                        "wordId": word_id,
                        "word": row.get("word"),
                        "senseId": sense_id,
                        "pos": sense.get("pos"),
                        "translation": translation,
                    }
                )
            if re.search(r"(^|[；;]\s*)(i|t)\.\s*", definition_zh):
                issues["definitionLooksLikeBrokenVtViMarker"].append(
                    {
                        "wordId": word_id,
                        "word": row.get("word"),
                        "senseId": sense_id,
                        "pos": sense.get("pos"),
                        "definitionZh": definition_zh[:200],
                    }
                )

    for item in suggestions:
        word_id = str(item.get("wordId") or "")
        scope = item.get("senseScope") if isinstance(item.get("senseScope"), dict) else {}
        sense_id = str(scope.get("fromSenseId") or "")
        if not sense_id:
            continue
        if word_id not in words_by_id or sense_id not in valid_sense_ids.get(word_id, set()):
            issues["lexicalSuggestionInvalidSenseId"].append(
                {
                    "id": item.get("_id"),
                    "wordId": word_id,
                    "word": item.get("word"),
                    "targetWord": item.get("targetWord"),
                    "fromSenseId": sense_id,
                }
            )

    for item in relations:
        scope = item.get("senseScope") if isinstance(item.get("senseScope"), dict) else {}
        checks = [
            ("from", str(item.get("fromWordId") or ""), str(scope.get("fromSenseId") or "")),
            ("to", str(item.get("toWordId") or ""), str(scope.get("toSenseId") or "")),
        ]
        for side, word_id, sense_id in checks:
            if not sense_id:
                continue
            if word_id not in words_by_id or sense_id not in valid_sense_ids.get(word_id, set()):
                issues["wordRelationInvalidSenseId"].append(
                    {
                        "id": item.get("_id"),
                        "side": side,
                        "wordId": word_id,
                        "word": item.get(f"{side}Word"),
                        "senseId": sense_id,
                        "relationType": item.get("relationType"),
                    }
                )

    report = {
        "wordCount": len(words),
        "senseCount": sum(len(row.get("senses") or []) for row in words),
        "multiSenseWordCount": multi_sense_count,
        "posCounts": dict(pos_counts),
        "issueCounts": {key: len(value) for key, value in issues.items()},
        "issues": issues,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("wordCount", "senseCount", "multiSenseWordCount", "issueCounts")}, ensure_ascii=False, indent=2))
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
