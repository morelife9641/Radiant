#!/usr/bin/env python3
"""Add high-confidence word-family/root related words to IELTS learning content."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "word_family_related_words_report.json"


WORD_FAMILY_REFINEMENTS: dict[str, dict[str, Any]] = {
    "hypothesis": {
        "segments": [
            {
                "form": "hypo-",
                "type": "prefix",
                "meaningZh": "在下；不足；假设性的",
                "origin": "Greek",
                "noteZh": "这里可理解为放在论证之下、作为待检验基础的命题。",
            },
            {
                "form": "thesis",
                "type": "root",
                "meaningZh": "放置；命题；论点",
                "origin": "Greek",
            },
        ],
        "explanationZh": "hypothesis 可理解为 hypo-（在下）+ thesis（命题、放置），即作为论证基础、等待证据检验的假说。",
        "relatedWords": [
            {
                "word": "hypothetical",
                "pos": "adj",
                "translationZh": "假设的；假定的",
                "connectionZh": "hypothesis 的形容词形式，属于同一词族。",
            },
            {
                "word": "hypothesise",
                "pos": "v",
                "translationZh": "假设；提出假说",
                "connectionZh": "hypothesis 的动词形式，英式拼写；美式常作 hypothesize。",
            },
            {
                "word": "synthesis",
                "pos": "n",
                "translationZh": "综合；合成",
                "connectionZh": "与 hypothesis 共享 thesis（放置；命题）这一构词成分，但不是近义词，也不属于形近易混。",
            },
            {
                "word": "thesis",
                "pos": "n",
                "translationZh": "论文；论点；命题",
                "connectionZh": "hypothesis 中的核心成分，表示命题或论点。",
            },
            {
                "word": "antithesis",
                "pos": "n",
                "translationZh": "对立面；对偶；反题",
                "connectionZh": "anti- + thesis，表示与某一论点相对立的命题。",
            },
        ],
    },
    "synthesis": {
        "segments": [
            {
                "form": "syn- / sym-",
                "type": "prefix",
                "meaningZh": "共同；一起",
                "origin": "Greek",
                "noteZh": "syn- 在某些字母前会发生形式变化，如 sym-。",
            },
            {
                "form": "thesis",
                "type": "root",
                "meaningZh": "放置；命题；论点",
                "origin": "Greek",
            },
        ],
        "explanationZh": "synthesis 可理解为 syn-（一起）+ thesis（放置），即把不同部分放在一起形成综合或合成。",
        "relatedWords": [
            {
                "word": "synthetic",
                "pos": "adj",
                "translationZh": "合成的；人造的",
                "connectionZh": "synthesis 的同族形容词，常用于材料、化学或理论语境。",
            },
            {
                "word": "synthesise",
                "pos": "v",
                "translationZh": "综合；合成",
                "connectionZh": "synthesis 的动词形式，英式拼写；美式常作 synthesize。",
            },
            {
                "word": "hypothesis",
                "pos": "n",
                "translationZh": "假设；假说",
                "connectionZh": "与 synthesis 共享 thesis（放置；命题）这一构词成分，但含义已分化。",
            },
            {
                "word": "thesis",
                "pos": "n",
                "translationZh": "论文；论点；命题",
                "connectionZh": "synthesis 中的核心成分，表示放置或命题。",
            },
            {
                "word": "antithesis",
                "pos": "n",
                "translationZh": "对立面；对偶；反题",
                "connectionZh": "同样包含 thesis，适合作为词根扩展学习。",
            },
        ],
    },
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def word_id_maps() -> tuple[dict[str, str], set[str]]:
    wordbook = read_jsonl(DATA_DIR / "wordbook_words.json")
    global_words = read_jsonl(WORDS_PATH)
    word_ids = {row["word"].lower(): row["wordId"] for row in wordbook}
    global_ids = {
        str(row.get("normalized") or row.get("word") or "").lower(): row["_id"]
        for row in global_words
        if row.get("_id")
    }
    word_ids.update({k: v for k, v in global_ids.items() if k not in word_ids})
    wordbook_words = {row["word"].lower() for row in wordbook}
    return word_ids, wordbook_words


def merge_related(existing: list[dict[str, Any]], additions: list[dict[str, Any]], word_ids: dict[str, str], wordbook_words: set[str]) -> tuple[list[dict[str, Any]], int]:
    by_word = {str(item.get("word") or "").lower(): item for item in existing if item.get("word")}
    added = 0
    for item in additions:
        word = item["word"]
        key = word.lower()
        next_item = dict(item)
        if key in word_ids:
            next_item["wordId"] = word_ids[key]
            next_item["clickable"] = True
            next_item["referenceStatus"] = "in_wordbook" if key in wordbook_words else "global_word_doc"
        else:
            next_item["clickable"] = False
            next_item["referenceStatus"] = "text_only_missing_word_doc"
        if key in by_word:
            by_word[key].update({k: v for k, v in next_item.items() if v not in (None, "", [])})
        else:
            existing.append(next_item)
            by_word[key] = next_item
            added += 1
    return existing, added


def main() -> None:
    rows = read_jsonl(LEARNING_PATH)
    by_word = {row["word"]: row for row in rows}
    word_ids, wordbook_words = word_id_maps()
    stats = {"wordsUpdated": 0, "segmentsReplaced": 0, "relatedWordsAdded": 0}

    for word, spec in WORD_FAMILY_REFINEMENTS.items():
        row = by_word.get(word)
        if not row:
            continue
        morphology = row.setdefault("morphology", {})
        morphology["segments"] = spec["segments"]
        morphology["explanationZh"] = spec["explanationZh"]
        stats["segmentsReplaced"] += 1
        related, added = merge_related(
            morphology.setdefault("relatedWords", []),
            spec["relatedWords"],
            word_ids,
            wordbook_words,
        )
        morphology["relatedWords"] = related
        stats["relatedWordsAdded"] += added
        provenance = row.setdefault("provenance", {})
        refinements = provenance.setdefault("refinements", [])
        if "word_family_root_related_words" not in refinements:
            refinements.append("word_family_root_related_words")
        stats["wordsUpdated"] += 1

    write_jsonl(LEARNING_PATH, rows)
    REPORT_PATH.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
