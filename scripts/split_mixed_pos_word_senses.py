#!/usr/bin/env python3
"""Split mixed-POS word senses in the IELTS import words JSONL.

Some dictionary rows were imported as a single sense even though the
translation contains multiple POS blocks, for example:

    v. ...  n. ...

The review HTML can parse that at render time, but the database should store
those as separate words.senses entries so relations can bind to a real senseId.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
REPORT_PATH = ROOT / "tmp/cloud_import_ielts_content_words/split_mixed_pos_word_senses_report.json"

POS_RE = re.compile(r"(?<![A-Za-z])(?:adj|adv|prep|conj|pron|excl|vt|vi|n|v|a)(?:\./|/)?\.?\s*", re.I)
POS_MARKER_RE = re.compile(r"\b(adj|adv|prep|conj|pron|excl|vt|vi|n|v|a)(?:\./|/)?\.?\s*", re.I)
PRON_RE = re.compile(r"/[^/\n]+/")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\\n", " ")).strip()


def normalize_pos(pos: str) -> str:
    value = str(pos or "").lower().strip().rstrip(".")
    if value in {"adj"}:
        return "a"
    if value in {"vt", "vi"}:
        return "v"
    return value


def split_pos_blocks(text: str, default_pos: str) -> list[dict[str, str]]:
    cleaned = PRON_RE.sub(" ", clean_text(text))
    if not cleaned:
        return []
    matches = list(POS_MARKER_RE.finditer(cleaned))
    if not matches:
        return [{"pos": normalize_pos(default_pos), "text": cleaned}]

    out: list[dict[str, str]] = []
    leading = cleaned[: matches[0].start()].strip(" ;；,，")
    if leading:
        out.append({"pos": normalize_pos(default_pos), "text": leading})

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
        body = cleaned[start:end].strip(" ;；,，")
        if not body:
            continue
        out.append({"pos": normalize_pos(match.group(1)), "text": body})
    return out


def has_pos_markers(text: str) -> bool:
    return bool(POS_MARKER_RE.search(PRON_RE.sub(" ", clean_text(text))))


def merge_same_pos(blocks: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    index: dict[str, int] = {}
    for block in blocks:
        pos = normalize_pos(block.get("pos") or "")
        text = clean_text(block.get("text") or "")
        if not pos or not text:
            continue
        if pos in index:
            current = merged[index[pos]]["text"]
            if text not in current:
                merged[index[pos]]["text"] = f"{current}；{text}"
        else:
            index[pos] = len(merged)
            merged.append({"pos": pos, "text": text})
    return merged


def sense_id_for(word: str, pos: str, counts: Counter[str]) -> str:
    pos = normalize_pos(pos) or "sense"
    counts[pos] += 1
    normalized = re.sub(r"[^a-z0-9]+", "_", word.lower()).strip("_") or "word"
    return f"{normalized}_{pos}_{counts[pos]:02d}"


def should_split(sense: dict[str, Any]) -> bool:
    translation = clean_text(sense.get("translation"))
    if not translation:
        return False
    return bool(POS_MARKER_RE.search(PRON_RE.sub(" ", translation)))


def split_sense(word_doc: dict[str, Any], sense: dict[str, Any]) -> list[dict[str, Any]]:
    word = str(word_doc.get("word") or word_doc.get("normalized") or "").strip()
    default_pos = normalize_pos(str(sense.get("pos") or ""))
    translation_blocks = merge_same_pos(split_pos_blocks(str(sense.get("translation") or ""), default_pos))
    if len(translation_blocks) <= 1:
        return [sense]

    definition_zh_blocks = merge_same_pos(split_pos_blocks(str(sense.get("definitionZh") or ""), default_pos))
    definition_en_blocks = merge_same_pos(split_pos_blocks(str(sense.get("definitionEn") or ""), default_pos))
    zh_by_pos = {item["pos"]: item["text"] for item in definition_zh_blocks}
    en_by_pos = {item["pos"]: item["text"] for item in definition_en_blocks}

    counts: Counter[str] = Counter()
    next_senses: list[dict[str, Any]] = []
    for block in translation_blocks:
        pos = block["pos"]
        next_sense = dict(sense)
        next_sense["pos"] = pos
        next_sense["translation"] = block["text"]
        if zh_by_pos.get(pos):
            next_sense["definitionZh"] = zh_by_pos[pos]
        elif has_pos_markers(str(sense.get("definitionZh") or "")) or pos != default_pos:
            next_sense["definitionZh"] = ""
        if en_by_pos.get(pos):
            next_sense["definitionEn"] = en_by_pos[pos]
        elif has_pos_markers(str(sense.get("definitionEn") or "")) or pos != default_pos:
            next_sense["definitionEn"] = ""
        next_sense["senseId"] = sense_id_for(word, pos, counts)
        next_senses.append(next_sense)
    return next_senses


def main() -> None:
    rows = read_jsonl(WORDS_PATH)
    changed: list[dict[str, Any]] = []

    for row in rows:
        senses = row.get("senses") or []
        if len(senses) != 1 or not should_split(senses[0]):
            continue
        before = [
            {
                "senseId": senses[0].get("senseId"),
                "pos": senses[0].get("pos"),
                "translation": senses[0].get("translation"),
            }
        ]
        next_senses = split_sense(row, senses[0])
        if len(next_senses) <= 1:
            continue
        row["senses"] = next_senses
        changed.append(
            {
                "wordId": row.get("_id"),
                "word": row.get("word"),
                "before": before,
                "after": [
                    {
                        "senseId": sense.get("senseId"),
                        "pos": sense.get("pos"),
                        "translation": sense.get("translation"),
                    }
                    for sense in next_senses
                ],
            }
        )

    write_jsonl(WORDS_PATH, rows)
    REPORT_PATH.write_text(
        json.dumps({"changedCount": len(changed), "changed": changed}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"changed: {len(changed)}")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
