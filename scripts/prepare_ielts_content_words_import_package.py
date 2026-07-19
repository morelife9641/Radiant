#!/usr/bin/env python3
"""Validate and package the IELTS content wordbook data for cloud import."""

from __future__ import annotations

import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
PACKAGE_DIR = DATA_DIR / "import_package"

COLLECTION_FILES = [
    "words.ielts_content_words.json",
    "wordbooks.json",
    "wordbook_words.json",
    "content_topics.json",
    "content_lines.json",
    "content_line_words.json",
    "word_learning_content.json",
    "word_relation_groups.json",
    "word_relations.json",
    "word_lexical_suggestions.json",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def assert_unique(rows: list[dict[str, Any]], label: str) -> None:
    ids = [row.get("_id") for row in rows]
    dupes = [value for value, count in Counter(ids).items() if count > 1]
    if dupes:
        raise RuntimeError(f"{label} duplicate _id: {dupes[:10]}")


def sense_ids_by_word(words: list[dict[str, Any]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for word in words:
        out[word["_id"]] = {
            str(sense.get("senseId"))
            for sense in word.get("senses") or []
            if sense.get("senseId")
        }
    return out


def validate_sense_ref(word_id: str | None, sense_id: str | None, senses: dict[str, set[str]], label: str) -> None:
    if not word_id or not sense_id:
        return
    if sense_id not in senses.get(word_id, set()):
        raise RuntimeError(f"invalid sense ref in {label}: {word_id}.{sense_id}")


def main() -> None:
    words_all = read_jsonl(WORDS_PATH)
    words_by_id = {row["_id"]: row for row in words_all}
    senses = sense_ids_by_word(words_all)

    rows_by_file = {
        "wordbooks.json": read_jsonl(DATA_DIR / "wordbooks.json"),
        "wordbook_words.json": read_jsonl(DATA_DIR / "wordbook_words.json"),
        "content_topics.json": read_jsonl(DATA_DIR / "content_topics.json"),
        "content_lines.json": read_jsonl(DATA_DIR / "content_lines.json"),
        "content_line_words.json": read_jsonl(DATA_DIR / "content_line_words.json"),
        "word_learning_content.json": read_jsonl(DATA_DIR / "word_learning_content.json"),
        "word_relation_groups.json": read_jsonl(DATA_DIR / "word_relation_groups.json"),
        "word_relations.json": read_jsonl(DATA_DIR / "word_relations.json"),
        "word_lexical_suggestions.json": read_jsonl(DATA_DIR / "word_lexical_suggestions.json"),
    }
    for name, rows in rows_by_file.items():
        assert_unique(rows, name)

    wordbook_word_ids = {row["wordId"] for row in rows_by_file["wordbook_words.json"]}
    topic_ids = {row["_id"] for row in rows_by_file["content_topics.json"]}
    line_ids = {row["_id"] for row in rows_by_file["content_lines.json"]}

    missing_words = sorted(word_id for word_id in wordbook_word_ids if word_id not in words_by_id)
    if missing_words:
        raise RuntimeError(f"wordbook_words references missing words: {missing_words[:10]}")

    orders = [row.get("order") for row in rows_by_file["wordbook_words.json"]]
    if orders != list(range(1, len(orders) + 1)):
        raise RuntimeError("wordbook_words.order is not contiguous")

    for row in rows_by_file["wordbook_words.json"]:
        if row.get("_id") != f"{row.get('bookId')}:{row.get('wordId')}":
            raise RuntimeError(f"invalid wordbook_words _id: {row.get('_id')}")
        stats = row.get("sourceStats") or {}
        if stats.get("firstTopicId") not in topic_ids or stats.get("primaryLineId") not in line_ids:
            raise RuntimeError(f"invalid wordbook_words sourceStats: {row.get('_id')}")

    learning_ids = {row["wordId"] for row in rows_by_file["word_learning_content.json"]}
    if learning_ids != wordbook_word_ids:
        raise RuntimeError("word_learning_content.wordId set does not match wordbook_words")
    for row in rows_by_file["word_learning_content.json"]:
        if row.get("status") not in {"draft", "published", "archived"}:
            raise RuntimeError(f"invalid word_learning_content.status: {row.get('_id')} {row.get('status')}")
        if not row.get("contentStage"):
            raise RuntimeError(f"missing word_learning_content.contentStage: {row.get('_id')}")
        core_sense = row.get("coreSense") or {}
        core_en = str(core_sense.get("en") or "").strip()
        core_zh = str(core_sense.get("zh") or "").strip()
        if not core_en or not core_zh or core_sense.get("scope") != "word":
            raise RuntimeError(f"invalid word-level coreSense: {row.get('_id')}")
        if "\n" in core_en or "\n" in core_zh or len(re.findall(r"[.!?](?:\s|$)", core_en)) > 1:
            raise RuntimeError(f"coreSense must be one display sentence: {row.get('_id')}")

    for row in rows_by_file["content_lines.json"]:
        if row.get("topicId") not in topic_ids:
            raise RuntimeError(f"content_lines missing topic: {row.get('_id')}")

    for row in rows_by_file["content_line_words.json"]:
        if row.get("topicId") not in topic_ids or row.get("lineId") not in line_ids:
            raise RuntimeError(f"content_line_words invalid topic/line ref: {row.get('_id')}")
        if row.get("wordId") not in words_by_id:
            raise RuntimeError(f"content_line_words invalid word ref: {row.get('_id')}")

    for row in rows_by_file["word_relations.json"]:
        from_id = row.get("fromWordId")
        to_id = row.get("toWordId")
        if from_id not in words_by_id or to_id not in words_by_id:
            raise RuntimeError(f"word_relations invalid word ref: {row.get('_id')}")
        scope = row.get("senseScope") or {}
        validate_sense_ref(from_id, scope.get("fromSenseId"), senses, row.get("_id", "word_relations"))
        validate_sense_ref(to_id, scope.get("toSenseId"), senses, row.get("_id", "word_relations"))

    for row in rows_by_file["word_lexical_suggestions.json"]:
        word_id = row.get("wordId")
        target_id = row.get("targetWordId")
        if word_id not in words_by_id:
            raise RuntimeError(f"word_lexical_suggestions invalid word ref: {row.get('_id')}")
        if target_id and target_id not in words_by_id:
            raise RuntimeError(f"word_lexical_suggestions invalid target ref: {row.get('_id')}")
        scope = row.get("senseScope") or {}
        validate_sense_ref(word_id, scope.get("fromSenseId"), senses, row.get("_id", "word_lexical_suggestions"))

    words_subset = [words_by_id[word_id] for word_id in sorted(wordbook_word_ids)]

    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(PACKAGE_DIR / "words.ielts_content_words.json", words_subset)
    shutil.copy2(WORDS_PATH, PACKAGE_DIR / "words.full_snapshot.json")
    for name in COLLECTION_FILES:
        if name == "words.ielts_content_words.json":
            continue
        shutil.copy2(DATA_DIR / name, PACKAGE_DIR / name)

    summary = {
        "packageDir": str(PACKAGE_DIR),
        "collections": {
            "words.ielts_content_words": len(words_subset),
            **{name.removesuffix(".json"): len(rows) for name, rows in rows_by_file.items()},
        },
        "lineStatus": dict(Counter(row.get("status") for row in rows_by_file["content_lines.json"])),
        "translationStatus": dict(Counter(row.get("translationStatus") for row in rows_by_file["content_lines.json"])),
        "learningStatus": dict(Counter(row.get("status") for row in rows_by_file["word_learning_content.json"])),
        "learningStage": dict(Counter(row.get("contentStage") for row in rows_by_file["word_learning_content.json"])),
        "relationStatus": dict(Counter(row.get("status") for row in rows_by_file["word_relations.json"])),
        "suggestionStatus": dict(Counter(row.get("status") for row in rows_by_file["word_lexical_suggestions.json"])),
    }
    (PACKAGE_DIR / "manifest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    collections = summary["collections"]
    readme = [
        "# IELTS Content Words Import Package",
        "",
        "## 当前状态",
        "",
        "- 结构校验已通过：无重复 `_id`，核心外键和 `senseScope` 均闭环。",
        f"- `words.ielts_content_words`：{collections['words.ielts_content_words']} 条。",
        f"- `wordbook_words`：{collections['wordbook_words']} 条。",
        f"- `content_topics`：{collections['content_topics']} 条。",
        f"- `content_lines`：{collections['content_lines']} 条；状态 `{summary['lineStatus']}`；翻译状态 `{summary['translationStatus']}`。",
        f"- `content_line_words`：{collections['content_line_words']} 条。",
        f"- `word_learning_content`：{collections['word_learning_content']} 条；状态 `{summary['learningStatus']}`；阶段 `{summary['learningStage']}`。",
        f"- `word_relations`：{collections['word_relations']} 条；状态 `{summary['relationStatus']}`，适合联调；正式精品露出前再精选发布。",
        f"- `word_lexical_suggestions`：{collections['word_lexical_suggestions']} 条；状态 `{summary['suggestionStatus']}`，若线上暂不展示 AI 候选，可先不导入。",
        "",
        "## 仍需注意",
        "",
        "- `line_ants_16` 原文疑似缺宾语：`...about the presence.`。当前保留在数据中，正式发布前建议回 PDF 或可靠来源确认。",
        "- `pending_machine_translation` 的新增 newdocs 原句尚未人工翻译/审核；可先导入联调，正式展示中文前再处理。",
        "",
        "## 建议导入顺序",
        "",
        "1. `words.ielts_content_words.json`",
        "2. `wordbooks.json`",
        "3. `wordbook_words.json`",
        "4. `content_topics.json`",
        "5. `content_lines.json`",
        "6. `content_line_words.json`",
        "7. `word_learning_content.json`",
        "8. `word_relation_groups.json`",
        "9. `word_relations.json`",
        "10. `word_lexical_suggestions.json`（若线上暂不展示 AI 候选，可先不导入）",
        "",
        "`words.full_snapshot.json` 是当前全局词库快照，优先用于备份或回滚，不建议直接整库覆盖。",
        "",
    ]
    (PACKAGE_DIR / "README.md").write_text("\n".join(readme), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
