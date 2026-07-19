#!/usr/bin/env python3
"""Fill missing IELTS content_lines translations with the local Argos en-zh model."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from argostranslate import translate


ROOT = Path(__file__).resolve().parent.parent
LINES_PATH = ROOT / "tmp/cloud_import_ielts_content_words/content_lines.json"
CHECKPOINT_PATH = LINES_PATH.with_suffix(".translation-checkpoint.json")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def normalize_zh_punctuation(value: str) -> str:
    value = re.sub(r"(?<!\d),(?!\d)", "，", value)
    value = value.replace(";", "；").replace(":", "：").replace("?", "？").replace("!", "！")
    value = re.sub(r"\.(?=\s*(?:$|[\u4e00-\u9fff“”]))", "。", value)
    return value.strip()


def main() -> None:
    rows = load_jsonl(LINES_PATH)
    pending_indexes = [index for index, row in enumerate(rows) if not str(row.get("translationZh") or "").strip()]
    translator = translate.get_translation_from_codes("en", "zh")
    if translator is None:
        raise RuntimeError("Argos en-zh model is not installed")

    translated = 0
    for index in pending_indexes:
        row = rows[index]
        value = translator.translate(row["text"]).strip()
        if not value:
            raise RuntimeError(f"empty translation returned for {row['_id']}")
        row["translationZh"] = normalize_zh_punctuation(value)
        row["translationStatus"] = "machine_translated_pending_human_review"
        row["translationMeta"] = {
            "provider": "argos-translate",
            "model": "translate-en_zh-1_9",
            "sourceLanguage": "en",
            "targetLanguage": "zh",
            "reviewStatus": "pending_human_review",
        }
        translated += 1
        if translated % 25 == 0:
            write_jsonl(CHECKPOINT_PATH, rows)
            print(f"translated {translated}/{len(pending_indexes)}", flush=True)

    for row in rows:
        row["translationZh"] = normalize_zh_punctuation(str(row.get("translationZh") or ""))
        if not str(row.get("translationZh") or "").strip():
            raise RuntimeError(f"translation still empty: {row['_id']}")
        if row.get("translationStatus") == "draft_human_review" and "translationMeta" not in row:
            row["translationMeta"] = {
                "provider": "editorial-draft",
                "sourceLanguage": "en",
                "targetLanguage": "zh",
                "reviewStatus": "pending_human_review",
            }

    write_jsonl(CHECKPOINT_PATH, rows)
    os.replace(CHECKPOINT_PATH, LINES_PATH)
    print(json.dumps({
        "totalLines": len(rows),
        "newlyTranslated": translated,
        "remainingEmpty": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
