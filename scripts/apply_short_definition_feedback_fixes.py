#!/usr/bin/env python3
"""Apply targeted short-definition fixes from human review comments."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDBOOK_WORDS_PATH = DATA_DIR / "wordbook_words.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "short_definition_human_feedback_fix_report.json"


FIXES_BY_ORDER: dict[int, str] = {
    101: "To make something smaller in amount, size, degree, or number.",
    108: "Existing or happening in the past, or holding a role before now.",
    109: "A group of people, animals, or plants living together in one place.",
    120: "A quality, feature, or possession that belongs to someone or something.",
    124: "To say firmly that something is true or must happen.",
    126: "To stay in the same place or condition, or to be left after others are gone.",
    127: "Already known, accepted, or provided in a particular situation.",
    131: "To fight against someone or something, especially a problem or danger.",
    143: "Related to the usual weather conditions of an area over a long time.",
    145: "Having a lot of money, goods, or resources.",
    147: "To train plants or animals so that people can use or live with them.",
    148: "The act of spreading information, ideas, or knowledge to many people.",
    149: "To talk with too much pride about what you have or can do.",
    152: "Existing in nature, or happening without being made or controlled by people.",
    153: "A condition or quality that makes success easier or gives someone a benefit.",
    154: "Certain or likely to happen, or tied and unable to move freely.",
    160: "To prefer, support, or help one person, idea, or choice more than another.",
    163: "Care taken to avoid danger, mistakes, or unwanted results.",
    164: "The state that someone or something is in, or a requirement that must be met.",
    165: "A series of actions, changes, or steps that lead to a result.",
    166: "Something more important than other things and dealt with first.",
    167: "Clearly different from something else, or easy to recognize.",
    168: "Good, useful, or showing agreement, confidence, or certainty.",
}


def read_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text[0] == "[":
        return json.loads(text)
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )


def main() -> None:
    wordbook_words = read_records(WORDBOOK_WORDS_PATH)
    learning_records = read_records(LEARNING_PATH)
    learning_by_id = {record.get("wordId"): record for record in learning_records}
    wordbook_by_order = {record.get("order"): record for record in wordbook_words}

    now = datetime.now(timezone.utc).isoformat()
    report: list[dict[str, Any]] = []

    for order, new_definition in FIXES_BY_ORDER.items():
        wordbook_record = wordbook_by_order.get(order)
        if not wordbook_record:
            report.append({"order": order, "status": "missing_wordbook_record"})
            continue
        word_id = wordbook_record.get("wordId")
        learning_record = learning_by_id.get(word_id)
        if not learning_record:
            report.append({"order": order, "wordId": word_id, "status": "missing_learning_record"})
            continue

        old_definition = learning_record.get("shortDefinitionEn")
        learning_record["shortDefinitionEn"] = new_definition
        learning_record["shortDefinitionStatus"] = "curated_manual_short_definition"
        learning_record["shortDefinitionReview"] = {
            "status": "revised_after_human_feedback",
            "labelZh": "已按人工批注修订",
            "reviewedAt": now,
            "reviewSource": "codex_manual_revision",
            "originalShortDefinitionEn": old_definition,
        }
        provenance = learning_record.setdefault("provenance", {})
        if isinstance(provenance, dict):
            provenance["shortDefinitionSource"] = "human_feedback_revision"
            provenance["reviewStatus"] = "short_definition_revised_after_human_feedback"
            provenance["reviewedAt"] = now

        report.append(
            {
                "order": order,
                "word": wordbook_record.get("word"),
                "wordId": word_id,
                "oldShortDefinitionEn": old_definition,
                "newShortDefinitionEn": new_definition,
                "status": "updated",
            }
        )

    write_jsonl(LEARNING_PATH, learning_records)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    updated = sum(1 for row in report if row.get("status") == "updated")
    print(json.dumps({"updated": updated, "report": str(REPORT_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
