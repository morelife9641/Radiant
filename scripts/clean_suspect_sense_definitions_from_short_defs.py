#!/usr/bin/env python3
"""Clean obviously noisy sense definitions using curated short definitions."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDBOOK_PATH = DATA_DIR / "wordbook_words.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "sense_definition_quality_report.json"

BAD_EN_RE = re.compile(
    r"one in front|bottle containing half|loot or money|right angles to the trunk|"
    r"congregation|versicle|priest|minister|radioactive isotope",
    re.I,
)
DOMAIN_ZH_RE = re.compile(r"\s*\[[^\]]+\]\s*")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def is_suspect_en(value: Any) -> bool:
    text = str(value or "").strip()
    if not text:
        return True
    if BAD_EN_RE.search(text):
        return True
    if re.search(r"\b(n|v|adj|adv|vt|vi)\. ", text, re.I):
        return True
    if text.count("；") >= 1 or text.count("\n") >= 1:
        return True
    if len(text) > 170:
        return True
    return False


def is_suspect_zh(value: Any) -> bool:
    text = str(value or "").strip()
    return bool(DOMAIN_ZH_RE.search(text)) or not text


def clean_zh(value: Any) -> str:
    text = str(value or "").strip()
    text = DOMAIN_ZH_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ；;，,")


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    wordbook_ids = {row["wordId"] for row in read_jsonl(WORDBOOK_PATH)}
    learning_by_id = {row["wordId"]: row for row in read_jsonl(LEARNING_PATH)}

    replaced = []
    zh_cleaned = []
    remaining = []

    for word in words:
        word_id = word.get("_id")
        if word_id not in wordbook_ids:
            continue
        learning = learning_by_id.get(word_id) or {}
        short_en = str(learning.get("shortDefinitionEn") or "").strip()
        short_zh = str(learning.get("shortDefinitionZh") or "").strip()
        short_is_curated = str(learning.get("shortDefinitionStatus") or "").startswith("curated_")
        senses = word.get("senses") or []

        for sense in senses:
            before_zh = str(sense.get("definitionZh") or "")
            cleaned = clean_zh(before_zh)
            if cleaned and cleaned != before_zh:
                sense["definitionZh"] = cleaned
                zh_cleaned.append({"wordId": word_id, "word": word.get("word"), "senseId": sense.get("senseId")})

        if len(senses) == 1 and short_is_curated and short_en and short_zh:
            sense = senses[0]
            if is_suspect_en(sense.get("definitionEn")) or is_suspect_zh(sense.get("definitionZh")):
                sense["definitionEn"] = short_en
                sense["definitionZh"] = short_zh
                replaced.append({"wordId": word_id, "word": word.get("word"), "senseId": sense.get("senseId"), "reason": "single_sense_from_short_definition"})
            continue

        for sense in senses:
            if is_suspect_en(sense.get("definitionEn")) and not (
                short_is_curated and short_en and BAD_EN_RE.search(str(sense.get("definitionEn") or ""))
            ):
                remaining.append(
                    {
                        "wordId": word_id,
                        "word": word.get("word"),
                        "senseId": sense.get("senseId"),
                        "pos": sense.get("pos"),
                        "translation": sense.get("translation"),
                        "definitionEn": sense.get("definitionEn"),
                        "reason": "needs_manual_sense_definition_review",
                    }
                )
            elif BAD_EN_RE.search(str(sense.get("definitionEn") or "")) and short_is_curated and short_en and short_zh:
                sense["definitionEn"] = short_en
                sense["definitionZh"] = short_zh
                replaced.append({"wordId": word_id, "word": word.get("word"), "senseId": sense.get("senseId"), "reason": "known_bad_phrase_from_short_definition"})

    write_jsonl(WORDS_PATH, words)
    report = {
        "replacedCount": len(replaced),
        "zhCleanedCount": len(zh_cleaned),
        "remainingManualReviewCount": len(remaining),
        "replaced": replaced,
        "zhCleanedSample": zh_cleaned[:200],
        "remainingManualReview": remaining[:500],
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("replacedCount", "zhCleanedCount", "remainingManualReviewCount")}, ensure_ascii=False, indent=2))
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
