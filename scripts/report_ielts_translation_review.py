#!/usr/bin/env python3
"""Create a focused review queue for IELTS machine translations."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LINES_PATH = ROOT / "tmp/cloud_import_ielts_content_words/content_lines.json"
OUT_PATH = ROOT / "tmp/cloud_import_ielts_content_words/translation_review_queue.json"


def main() -> None:
    rows = [json.loads(line) for line in LINES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    queue = []
    for row in rows:
        translation = row.get("translationZh") or ""
        letters = len(re.findall(r"[A-Za-z]", translation))
        language_chars = len(re.findall(r"[A-Za-z\u3400-\u9fff]", translation)) or 1
        flags = []
        if not re.search(r"[\u3400-\u9fff]", translation):
            flags.append("no_chinese_characters")
        second_pass_complete = row.get("translationMeta", {}).get("secondPassStatus") == "completed"
        if letters / language_chars > 0.45 and not second_pass_complete:
            flags.append("high_english_residue")
        if len(translation.strip()) < 5 and len(row.get("text") or "") > 30:
            flags.append("suspiciously_short")
        source_status = row.get("sourceReview", {}).get("status")
        if source_status == "needs_source_verification" or (row.get("sourceNote") and not source_status):
            flags.append("source_text_issue")
        if flags:
            queue.append({
                "lineId": row["_id"],
                "topicId": row["topicId"],
                "articleTitle": row["articleTitle"],
                "text": row["text"],
                "translationZh": translation,
                "flags": flags,
                "reviewStatus": "pending_human_review",
            })
    OUT_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"reviewQueue": len(queue), "output": str(OUT_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
