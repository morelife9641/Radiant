#!/usr/bin/env python3
"""Curate the IELTS entry for split."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    learning = read_jsonl(LEARNING_PATH)
    changed: list[str] = []

    for row in words:
        if row.get("_id") != "word_split":
            continue
        row["senses"] = [
            {
                "pos": "v",
                "translation": "（使）分裂；裂开；分开；拆分",
                "definitionEn": "To divide something into parts, or to separate into different parts.",
                "definitionZh": "把某物分成几个部分，或使其分离成不同部分。",
                "collinsEn": "",
                "collinsZh": "",
                "synonyms": [],
                "antonyms": [],
                "gamingLink": None,
                "senseId": "split_v_01",
            },
            {
                "pos": "n",
                "translation": "分裂；分歧；裂口；划分",
                "definitionEn": "A division, disagreement, or separation between people or things.",
                "definitionZh": "人或事物之间的分裂、分歧或分离。",
                "collinsEn": "",
                "collinsZh": "",
                "synonyms": [],
                "antonyms": [],
                "gamingLink": None,
                "senseId": "split_n_01",
            },
            {
                "pos": "a",
                "translation": "分裂的；分开的；劈开的",
                "definitionEn": "Divided or separated into parts.",
                "definitionZh": "被分成几部分的；分开的。",
                "collinsEn": "",
                "collinsZh": "",
                "synonyms": [],
                "antonyms": [],
                "gamingLink": None,
                "senseId": "split_a_01",
            },
        ]
        changed.append("words.word_split")

    for row in learning:
        if row.get("_id") != "word_split":
            continue
        row["shortDefinitionEn"] = "To divide into parts or make people or things separate."
        row["shortDefinitionZh"] = "分成几部分，或使人或事物分开。"
        row["shortDefinitionStatus"] = "curated_manual_short_definition"
        row["shortDefinitionReview"] = {
            "status": "reviewed",
            "reviewMethod": "manual_core_sense_fix",
        }
        morphology = row.setdefault("morphology", {})
        morphology["segments"] = [
            {
                "form": "split",
                "type": "base",
                "meaningZh": "分开；分裂；拆分",
                "noteZh": "split 在 IELTS 语境中常表示分裂、分开或把整体拆成部分。",
            }
        ]
        morphology["explanationZh"] = "split 按整体词学习，核心意思是把一个整体分开或拆成几部分。"
        if "provenance" in row and isinstance(row["provenance"], dict):
            row["provenance"]["reviewStatus"] = "reviewed"
            row["provenance"]["shortDefinitionZhSource"] = "manual_core_sense_fix"
        changed.append("word_learning_content.word_split")

    write_jsonl(WORDS_PATH, words)
    write_jsonl(LEARNING_PATH, learning)
    print(json.dumps({"changed": changed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
