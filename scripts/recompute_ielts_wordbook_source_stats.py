#!/usr/bin/env python3
"""Recompute IELTS wordbook sourceStats from content_line_words."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDBOOK_WORDS_PATH = DATA_DIR / "wordbook_words.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
LINES_PATH = DATA_DIR / "content_lines.json"
LINE_WORDS_PATH = DATA_DIR / "content_line_words.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    wordbook_words = read_jsonl(WORDBOOK_WORDS_PATH)
    learning_rows = read_jsonl(LEARNING_PATH)
    lines = read_jsonl(LINES_PATH)
    line_words = read_jsonl(LINE_WORDS_PATH)

    line_order = {row["_id"]: index for index, row in enumerate(lines)}
    links_by_word: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for link in line_words:
        links_by_word[str(link.get("wordId") or "")].append(link)

    changed = 0
    missing_links: list[str] = []
    stats_by_word: dict[str, dict[str, Any]] = {}

    for row in wordbook_words:
        word_id = row["wordId"]
        links = sorted(
            links_by_word.get(word_id, []),
            key=lambda item: (line_order.get(item.get("lineId"), 10**9), str(item.get("lineId") or "")),
        )
        if not links:
            missing_links.append(word_id)
            continue

        topic_ids: list[str] = []
        seen_topics: set[str] = set()
        for link in links:
            topic_id = str(link.get("topicId") or "")
            if topic_id and topic_id not in seen_topics:
                seen_topics.add(topic_id)
                topic_ids.append(topic_id)

        old_stats = row.get("sourceStats") if isinstance(row.get("sourceStats"), dict) else {}
        primary_line_id = old_stats.get("primaryLineId")
        if not any(link.get("lineId") == primary_line_id for link in links):
            primary_line_id = links[0].get("lineId")

        first_topic_id = old_stats.get("firstTopicId")
        if first_topic_id not in seen_topics:
            first_topic_id = links[0].get("topicId")

        next_stats = {
            **old_stats,
            "occurrenceCount": len(links),
            "articleCount": len(topic_ids),
            "firstTopicId": first_topic_id,
            "primaryLineId": primary_line_id,
            "topicIds": topic_ids,
        }
        if next_stats != old_stats:
            row["sourceStats"] = next_stats
            changed += 1
        stats_by_word[word_id] = next_stats

    learning_changed = 0
    for row in learning_rows:
        word_id = row.get("wordId")
        if word_id not in stats_by_word:
            continue
        if row.get("sourceStats") != stats_by_word[word_id]:
            row["sourceStats"] = stats_by_word[word_id]
            learning_changed += 1

    if missing_links:
        raise RuntimeError(f"wordbook_words without content_line_words links: {missing_links[:20]}")

    write_jsonl(WORDBOOK_WORDS_PATH, wordbook_words)
    write_jsonl(LEARNING_PATH, learning_rows)

    print(
        json.dumps(
            {
                "wordbookWords": len(wordbook_words),
                "wordbookStatsChanged": changed,
                "learningStatsChanged": learning_changed,
                "missingLinks": len(missing_links),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
