#!/usr/bin/env python3
"""Add conservative derived/base related words for newdocs-added words."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
WORDBOOK_PATH = DATA_DIR / "wordbook_words.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "newdocs_related_words_report.json"

PREFIXES = ["re", "un", "in", "im", "dis", "de", "pre", "post", "inter", "sub", "super", "over", "under", "anti", "auto", "bio", "micro", "multi", "non"]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def first_sense(word: dict[str, Any]) -> dict[str, Any]:
    senses = word.get("senses") or []
    return senses[0] if senses else {}


def candidate_related(word: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    lower = word.lower()
    if " " in lower or "-" in lower:
        return out
    for prefix in PREFIXES:
        if lower.startswith(prefix) and len(lower) - len(prefix) >= 4:
            out.append((lower[len(prefix):], f"{word} 去掉前缀 {prefix}- 后得到的基础词。"))

    suffix_rules = [
        ("ability", [("able", "名词 -ability 与形容词 -able 对应。")]),
        ("ibility", [("ible", "名词 -ibility 与形容词 -ible 对应。")]),
        ("ation", [("ate", "名词 -ation 常与动词 -ate 对应。"), ("e", "名词 -ation 可能对应更短的动词形式。"), ("", "名词 -ation 去后缀后的词干。")]),
        ("tion", [("e", "名词 -tion 可能对应动词基础形式。"), ("", "名词 -tion 去后缀后的词干。")]),
        ("sion", [("d", "名词 -sion 可能对应以 d 结尾的动词。"), ("t", "名词 -sion 可能对应以 t 结尾的动词。"), ("", "名词 -sion 去后缀后的词干。")]),
        ("ment", [("", "名词 -ment 常由动词构成。")]),
        ("ness", [("", "名词 -ness 常由形容词构成。")]),
        ("ity", [("", "名词 -ity 表示性质或状态。"), ("e", "名词 -ity 可能对应以 e 结尾的形容词。")]),
        ("able", [("", "形容词 -able 可能由动词构成。"), ("e", "形容词 -able 可能对应以 e 结尾的动词。")]),
        ("ible", [("", "形容词 -ible 可能由动词构成。"), ("e", "形容词 -ible 可能对应以 e 结尾的动词。")]),
        ("ive", [("", "形容词 -ive 常表示倾向或性质。"), ("e", "形容词 -ive 可能对应以 e 结尾的动词。")]),
        ("ous", [("", "形容词 -ous 表示具有某种性质。")]),
        ("al", [("", "形容词/名词 -al 表示相关性质或行为。")]),
        ("er", [("", "名词 -er 常表示做某事的人或物。")]),
        ("or", [("", "名词 -or 常表示做某事的人或物。")]),
        ("ist", [("ism", "名词 -ist 与 -ism 常构成主义/从业者关系。")]),
        ("ism", [("ist", "名词 -ism 与 -ist 常构成主义/从业者关系。")]),
        ("y", [("", "形容词 -y 可能由名词构成。")]),
    ]
    for suffix, replacements in suffix_rules:
        if lower.endswith(suffix) and len(lower) - len(suffix) >= 4:
            stem = lower[: -len(suffix)]
            for replacement, note in replacements:
                out.append((stem + replacement, note))
    return out


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    words_by_norm = {str(row.get("normalized") or row.get("word") or "").lower(): row for row in words}
    wordbook = read_jsonl(WORDBOOK_PATH)
    wordbook_norms = {row["normalized"].lower() for row in wordbook}
    new_word_ids = {row["wordId"] for row in wordbook if (row.get("order") or 0) > 1352}
    learning = read_jsonl(LEARNING_PATH)
    added_by_word: dict[str, list[str]] = {}

    for row in learning:
        if row.get("wordId") not in new_word_ids:
            continue
        word = str(row.get("normalized") or row.get("word") or "").lower()
        morphology = row.setdefault("morphology", {})
        related = morphology.setdefault("relatedWords", [])
        existing = {str(item.get("word") or "").lower() for item in related}
        for candidate, note in candidate_related(word):
            if candidate == word or candidate in existing:
                continue
            candidate_doc = words_by_norm.get(candidate)
            if not candidate_doc:
                continue
            sense = first_sense(candidate_doc)
            item = {
                "wordId": candidate_doc["_id"],
                "word": candidate_doc.get("word") or candidate,
                "pos": sense.get("pos") or "",
                "translationZh": sense.get("translation") or "",
                "connectionZh": note,
                "clickable": True,
                "referenceStatus": "in_wordbook" if candidate in wordbook_norms else "global_word_doc",
                "status": "draft",
                "reviewStatus": "auto_enriched_pending_review",
            }
            related.append(item)
            existing.add(candidate)
            added_by_word.setdefault(word, []).append(candidate)
            if len(added_by_word[word]) >= 5:
                break

    write_jsonl(LEARNING_PATH, learning)
    report = {
        "wordsUpdated": len(added_by_word),
        "relatedWordsAdded": sum(len(items) for items in added_by_word.values()),
        "addedByWord": added_by_word,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("wordsUpdated", "relatedWordsAdded")}, ensure_ascii=False, indent=2))
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
