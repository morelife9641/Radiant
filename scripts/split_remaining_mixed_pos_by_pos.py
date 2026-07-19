#!/usr/bin/env python3
"""Split remaining manually approved mixed-POS IELTS word senses by POS."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
CANDIDATES_PATH = DATA_DIR / "remaining_mixed_pos_sense_candidates.json"
MANUAL_REVIEW_PATH = DATA_DIR / "semantic_sense_manual_review.json"
REPORT_PATH = DATA_DIR / "remaining_pos_split_report.json"

POS_PATTERN = re.compile(r"(?:^|[\s；;，,])(?P<pos>n|vt|vi|v|a|adj|adv|prep|conj|pron)\.\s*", re.I)
IPA_PATTERN = re.compile(r"/[^/\n]+/|\{[^{}\n]+\}")

POS_LABEL_ZH = {
    "n": "名词",
    "v": "动词",
    "vt": "及物动词",
    "vi": "不及物动词",
    "a": "形容词",
    "adj": "形容词",
    "adv": "副词",
    "prep": "介词",
    "conj": "连词",
    "pron": "代词",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def clean_text(value: str) -> str:
    value = IPA_PATTERN.sub(" ", str(value or ""))
    value = re.sub(r"\[[^\]\n]+\]", " ", value)
    value = re.sub(r"\s+", " ", value).strip(" ;；,，")
    return value


def normalize_pos(pos: str) -> str:
    value = str(pos or "").lower().strip().rstrip(".")
    return "a" if value == "adj" else value


def pos_for_id(pos: str) -> str:
    value = normalize_pos(pos)
    if value == "a":
        return "adj"
    return value or "sense"


def split_pos_blocks(text: str) -> list[dict[str, str]]:
    text = clean_text(text)
    if not text:
        return []
    matches = list(POS_PATTERN.finditer(text))
    if not matches:
        return []
    blocks: list[dict[str, str]] = []
    leading = text[: matches[0].start()].strip(" ;；,，")
    if leading:
        blocks.append({"pos": "", "body": leading})
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip(" ;；,，")
        if body:
            blocks.append({"pos": normalize_pos(match.group("pos")), "body": body})
    return blocks


def candidate_pos_order(candidate: dict[str, Any], template: dict[str, Any]) -> list[str]:
    order: list[str] = []
    for source in (candidate.get("detectedPos") or [], str(template.get("pos") or "")):
        parts = source if isinstance(source, list) else re.split(r"[/,;\s]+", str(source))
        for part in parts:
            pos = normalize_pos(str(part))
            if pos and pos not in order:
                order.append(pos)
    return order


def pick_bodies_by_pos(blocks: list[dict[str, str]], order: list[str], fallback_pos: str) -> dict[str, str]:
    by_pos: dict[str, list[str]] = {}
    leading: list[str] = []
    for block in blocks:
        pos = block.get("pos") or ""
        body = block.get("body") or ""
        if not body:
            continue
        if pos:
            by_pos.setdefault(pos, []).append(body)
        else:
            leading.append(body)
    if leading and fallback_pos:
        by_pos.setdefault(fallback_pos, []).insert(0, "；".join(leading))
    return {pos: "；".join(values) for pos, values in by_pos.items() if values}


def translation_for_pos(pos: str, candidate: dict[str, Any], template: dict[str, Any]) -> str:
    order = candidate_pos_order(candidate, template)
    fallback = normalize_pos(template.get("pos") or (order[0] if order else ""))
    translation_blocks = split_pos_blocks(candidate.get("translation") or template.get("translation") or "")
    definition_blocks = split_pos_blocks(candidate.get("definitionZh") or template.get("definitionZh") or "")
    translation_by_pos = pick_bodies_by_pos(translation_blocks, order, fallback)
    definition_by_pos = pick_bodies_by_pos(definition_blocks, order, fallback)

    value = translation_by_pos.get(pos) or definition_by_pos.get(pos)
    if value:
        return clean_text(value)
    if pos in definition_by_pos:
        return clean_text(definition_by_pos[pos])
    label = POS_LABEL_ZH.get(pos, pos)
    return f"{label}义"


def definition_zh_for_pos(pos: str, translation: str) -> str:
    label = POS_LABEL_ZH.get(pos, pos)
    return f"该词作{label}时表示：{translation}。"


def definition_en_for_pos(pos: str, template: dict[str, Any]) -> str:
    source = str(template.get("definitionEn") or "").strip()
    if source:
        return source
    label = {
        "n": "noun",
        "v": "verb",
        "vt": "transitive verb",
        "vi": "intransitive verb",
        "a": "adjective",
        "adv": "adverb",
        "prep": "preposition",
        "conj": "conjunction",
        "pron": "pronoun",
    }.get(pos, "sense")
    return f"Used as a {label}."


def build_sense(word: str, index_by_pos: dict[str, int], pos: str, template: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    index_by_pos[pos] = index_by_pos.get(pos, 0) + 1
    item = deepcopy(template)
    translation = translation_for_pos(pos, candidate, template)
    item.update(
        {
            "senseId": f"{word}_{pos_for_id(pos)}_{index_by_pos[pos]:02d}",
            "pos": pos,
            "translation": translation,
            "definitionEn": definition_en_for_pos(pos, template),
            "definitionZh": definition_zh_for_pos(pos, translation),
            "synonyms": [],
            "antonyms": [],
        }
    )
    item.setdefault("collinsEn", "")
    item.setdefault("collinsZh", "")
    item.setdefault("gamingLink", None)
    return item


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    candidates = read_json(CANDIDATES_PATH, [])
    by_word_id = {
        row["wordId"]: row
        for row in candidates
        if isinstance(row, dict) and row.get("wordId")
    }

    changed: list[dict[str, Any]] = []
    for row in words:
        candidate = by_word_id.get(row["_id"])
        if not candidate:
            continue
        old_senses = row.get("senses") or []
        if len(old_senses) != 1:
            continue
        template = old_senses[0]
        order = candidate_pos_order(candidate, template)
        if len(order) < 2:
            continue
        index_by_pos: dict[str, int] = {}
        row["senses"] = [build_sense(row["normalized"] or row["word"], index_by_pos, pos, template, candidate) for pos in order]
        changed.append(
            {
                "word": row["word"],
                "wordId": row["_id"],
                "oldSenseIds": [sense.get("senseId") for sense in old_senses],
                "newSenseIds": [sense["senseId"] for sense in row["senses"]],
            }
        )

    write_jsonl(WORDS_PATH, words)
    MANUAL_REVIEW_PATH.write_text("[]\n", encoding="utf-8")
    REPORT_PATH.write_text(
        json.dumps({"changedCount": len(changed), "changedWords": changed}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"split by POS: {len(changed)}")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
