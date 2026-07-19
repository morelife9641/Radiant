#!/usr/bin/env python3
"""Reconcile every IELTS word sense against its POS-labelled definitions.

The historical import mixes three different sources in one sense: the curated
Chinese translation, ECDICT's Chinese definition and WordNet's English
definition.  Each source can contain multiple parts of speech.  This script
makes ``words.senses`` the source of truth again:

* split any recoverable POS into a separate sense;
* give each sense only the matching POS part of definitionEn/definitionZh;
* standardise POS values to n/v/a/adv/prep/conj/pron/excl;
* never invent a Chinese translation.  A POS found only in English is logged
  for review instead of creating a misleading empty sense.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
REPORT_PATH = ROOT / "tmp/cloud_import_ielts_content_words/reconcile_word_sense_definitions_report.json"

# ``r`` and ``s`` are WordNet's adverb/adjective labels.  ``ad`` is a
# historical import shorthand for adverb.
MARKER_RE = re.compile(
    r"(?<![A-Za-z])(?P<pos>adj|adv|ad|prep|conj|pron|excl|vt|vi|n|v|a|r|s)\.(?:/)?\s*",
    re.I,
)
POS_ORDER = ("n", "v", "a", "adv", "prep", "conj", "pron", "excl", "phrase")
POS_ALIASES = {
    "adj": "a", "s": "a", "vt": "v", "vi": "v", "r": "adv", "ad": "adv",
}
BARE_VERB_LABEL_RE = re.compile(r"(?<![A-Za-z])(vt|vi)(?=\s)", re.I)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    body = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    path.write_text(body + ("\n" if body else ""), encoding="utf-8")


def normalize_pos(value: Any) -> str:
    raw = str(value or "").lower().strip().rstrip(".")
    return POS_ALIASES.get(raw, raw)


def pos_tokens(value: Any) -> list[str]:
    text = str(value or "")
    tokens = [normalize_pos(match.group("pos")) for match in MARKER_RE.finditer(text)]
    # POS fields sometimes use compact legacy forms such as ``n./vt``.
    if re.fullmatch(r"[A-Za-z./\s]+", text):
        compact = [normalize_pos(item) for item in re.split(r"[./\s]+", text.lower()) if item]
        if compact and all(item in POS_ORDER for item in compact):
            tokens = compact
    # A field such as ``n./vt`` has no whitespace after the last marker.
    if not tokens and text:
        raw = re.split(r"[./\\s]+", text.lower())
        tokens = [normalize_pos(item) for item in raw if item]
    return [item for item in tokens if item in POS_ORDER]


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\\n", " ")).strip(" ;；,，")


def blocks(value: Any) -> dict[str, str]:
    """Return POS -> text, keeping repeated entries of the same POS."""
    # ECDICT rows in this import preserve line breaks as literal ``\\n``.
    # Convert them before locating the next POS label, otherwise the ``n`` in
    # ``\\nvt.`` makes the following vt. label invisible to the regex.
    text = str(value or "").replace("\\n", "\n")
    # A few ECDICT Chinese rows use ``vi 倾斜`` rather than ``vi. 倾斜``.
    # Only normalize bare vt/vi labels: treating bare ``a``/``n`` as markers
    # would incorrectly split ordinary English prose such as "a bottle".
    text = BARE_VERB_LABEL_RE.sub(lambda match: f"{match.group(1)}. ", text)
    matches = list(MARKER_RE.finditer(text))
    if not matches:
        return {}
    result: dict[str, list[str]] = defaultdict(list)
    for index, match in enumerate(matches):
        pos = normalize_pos(match.group("pos"))
        if pos not in POS_ORDER:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = clean(text[match.end() : end])
        if body and body not in result[pos]:
            result[pos].append(body)
    return {pos: "；".join(parts) for pos, parts in result.items()}


def ordered_positions(values: set[str]) -> list[str]:
    return [pos for pos in POS_ORDER if pos in values]


def sense_id(word: str, pos: str, used: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", word.lower()).strip("_") or "word"
    index = 1
    while True:
        candidate = f"{base}_{pos}_{index:02d}"
        if candidate not in used:
            used.add(candidate)
            return candidate
        index += 1


def main() -> None:
    rows = read_jsonl(WORDS_PATH)
    changed: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    legacy_id_map: dict[str, str] = {}

    for row in rows:
        word = str(row.get("word") or row.get("normalized") or "")
        original = row.get("senses") or []
        if not original:
            continue

        # Collect every labelled source block at word scope.  That lets route
        # recover its v. sense when the original translation only listed n.
        source_by_pos: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        existing_by_pos: dict[str, list[dict[str, Any]]] = defaultdict(list)
        observed_positions: set[str] = set()
        for sense in original:
            declared = pos_tokens(sense.get("pos"))
            observed_positions.update(declared)
            if len(declared) == 1:
                existing_by_pos[declared[0]].append(sense)
            for field in ("translation", "definitionZh", "definitionEn"):
                for pos, text in blocks(sense.get(field)).items():
                    observed_positions.add(pos)
                    if text not in source_by_pos[pos][field]:
                        source_by_pos[pos][field].append(text)

            # An unlabelled definition on an already unambiguous sense is
            # already sense-scoped.  Preserve it instead of treating it as
            # missing merely because it has no ``n.``/``v.`` prefix.
            if len(declared) == 1:
                pos = declared[0]
                for field in ("definitionZh", "definitionEn"):
                    raw = sense.get(field)
                    value = clean(raw)
                    if value and not blocks(raw) and value not in source_by_pos[pos][field]:
                        source_by_pos[pos][field].append(value)

        # Phrases have no grammatical POS in the source, but they still need
        # a renderable sense instead of being discarded by word-only logic.
        if not observed_positions and row.get("type") == "phrase":
            observed_positions.add("phrase")
            first = original[0]
            for field in ("translation", "definitionZh", "definitionEn"):
                value = clean(first.get(field))
                if value:
                    source_by_pos["phrase"][field].append(value)

        # A clean existing translation is also evidence for its declared POS.
        for pos, senses in existing_by_pos.items():
            for sense in senses:
                translation = clean(sense.get("translation"))
                if translation and not blocks(translation):
                    source_by_pos[pos]["translation"].append(translation)

        next_senses: list[dict[str, Any]] = []
        used_ids: set[str] = set()
        for pos in ordered_positions(observed_positions):
            matching_existing = existing_by_pos.get(pos, [])
            source = source_by_pos[pos]
            translation = "；".join(dict.fromkeys(source.get("translation", [])))
            zh = "；".join(dict.fromkeys(source.get("definitionZh", [])))
            en = "；".join(dict.fromkeys(source.get("definitionEn", [])))

            # ECDICT's matching Chinese block is a reliable fallback when the
            # curated translation omitted this POS, as in route -> vt.
            if not translation:
                translation = zh
            if not translation:
                if en:
                    unresolved.append({
                        "wordId": row.get("_id"), "word": word, "pos": pos,
                        "reason": "english_definition_has_pos_but_no_chinese_translation",
                        "definitionEn": en,
                    })
                continue

            if matching_existing:
                # Keep genuinely separate senses with the same POS, but make
                # their auxiliary definitions POS-pure.
                for index, old in enumerate(matching_existing):
                    item = dict(old)
                    old_id = str(item.get("senseId") or "")
                    item["pos"] = pos
                    item["translation"] = translation if len(matching_existing) == 1 else clean(old.get("translation")) or translation
                    item["definitionZh"] = zh
                    item["definitionEn"] = en
                    desired_id = old_id if re.fullmatch(rf"{re.escape(re.sub(r'[^a-z0-9]+', '_', word.lower()).strip('_') or 'word')}_{pos}_\d{{2}}", old_id) else ""
                    item["senseId"] = desired_id if desired_id and desired_id not in used_ids else sense_id(word, pos, used_ids)
                    used_ids.add(item["senseId"])
                    if old_id and old_id != item["senseId"]:
                        legacy_id_map[old_id] = item["senseId"]
                    next_senses.append(item)
            else:
                template = dict(original[0])
                template["pos"] = pos
                template["translation"] = translation
                template["definitionZh"] = zh
                template["definitionEn"] = en
                template["senseId"] = sense_id(word, pos, used_ids)
                next_senses.append(template)

        if next_senses != original:
            row["senses"] = next_senses
            changed.append({
                "wordId": row.get("_id"),
                "word": word,
                "before": [{"senseId": s.get("senseId"), "pos": s.get("pos"), "translation": s.get("translation")} for s in original],
                "after": [{"senseId": s.get("senseId"), "pos": s.get("pos"), "translation": s.get("translation")} for s in next_senses],
            })

    write_jsonl(WORDS_PATH, rows)
    REPORT_PATH.write_text(json.dumps({
        "changedCount": len(changed),
        "unresolvedCount": len(unresolved),
        "changed": changed,
        "unresolved": unresolved,
        "legacySenseIdMap": legacy_id_map,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changed": len(changed), "unresolved": len(unresolved), "legacySenseIdMap": len(legacy_id_map)}, ensure_ascii=False))
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
