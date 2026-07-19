#!/usr/bin/env python3
"""Create and audit one display-ready core sense for every IELTS word.

`words.senses` remains the authoritative POS-level dictionary structure.  The
`coreSense` object in word_learning_content is deliberately different: it is
one learner-facing sentence per word, regardless of how many POS senses exist.
Legacy shortDefinitionEn/Zh fields are kept in sync for older clients.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "core_sense_audit_report.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def compact(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def one_english_sentence(value: Any) -> str:
    text = compact(value)
    # The curated source is already one sentence. This protects the canonical
    # field from accidental line breaks or multiple copied dictionary senses.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    text = next((part.strip() for part in parts if part.strip()), "")
    if text and text[-1] not in ".!?":
        text += "."
    return text


def one_chinese_sentence(value: Any) -> str:
    text = compact(value)
    # Do not split Chinese semicolons: they often express complementary facets
    # of one word-level concept. Newlines and repeated terminal sentences do not.
    parts = re.split(r"(?<=[。！？])\s+", text)
    return next((part.strip() for part in parts if part.strip()), "")


def main() -> None:
    rows = read_jsonl(LEARNING_PATH)
    changed = 0
    issues: list[dict[str, str]] = []
    status_counts: Counter[str] = Counter()

    for row in rows:
        existing = row.get("coreSense") if isinstance(row.get("coreSense"), dict) else {}
        # Treat the manually curated legacy short definition as source of truth.
        en = one_english_sentence(row.get("shortDefinitionEn") or existing.get("en"))
        zh = one_chinese_sentence(row.get("shortDefinitionZh") or existing.get("zh"))
        if not en or not zh:
            issues.append({"wordId": str(row.get("wordId") or row.get("_id") or ""), "word": str(row.get("word") or ""), "reason": "missing_core_sense"})
            continue

        short_status = str(row.get("shortDefinitionStatus") or "").strip()
        review = row.get("shortDefinitionReview") if isinstance(row.get("shortDefinitionReview"), dict) else {}
        review_status = str(review.get("status") or "").strip()
        core_status = "reviewed" if short_status.startswith("curated_") or short_status == "human_reviewed" or review_status == "reviewed" else "draft"
        core = {
            "en": en,
            "zh": zh,
            "scope": "word",
            "status": core_status,
            "source": "short_definition_curated_word_level",
        }
        if row.get("coreSense") != core:
            row["coreSense"] = core
            changed += 1
        # Keep existing client paths deterministic and equivalent to coreSense.
        if row.get("shortDefinitionEn") != en:
            row["shortDefinitionEn"] = en
            changed += 1
        if row.get("shortDefinitionZh") != zh:
            row["shortDefinitionZh"] = zh
            changed += 1
        status_counts[core_status] += 1

    if issues:
        sample = ", ".join(item["word"] or item["wordId"] for item in issues[:12])
        raise RuntimeError(f"coreSense incomplete for {len(issues)} rows: {sample}")

    write_jsonl(LEARNING_PATH, rows)
    report = {
        "wordCount": len(rows),
        "changedRowsOrFields": changed,
        "missingCoreSense": 0,
        "multiSentenceEnglish": sum(len(re.findall(r"[.!?](?:\s|$)", row["coreSense"]["en"])) > 1 for row in rows),
        "hasNewlines": sum("\n" in row["coreSense"]["en"] or "\n" in row["coreSense"]["zh"] for row in rows),
        "status": dict(status_counts),
        "contract": {
            "canonicalDisplayField": "word_learning_content.coreSense",
            "oneRecordPerWord": True,
            "oneSentencePerLanguage": True,
            "posLevelDefinitionsRemainIn": "words.senses[]",
        },
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
