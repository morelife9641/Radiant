#!/usr/bin/env python3
"""Repair POS/definition mismatches without collapsing curated senses.

Existing sense IDs can encode a useful distinction (for example
``design_n_plan_01`` vs ``design_n_pattern_01``), so this pass only creates
new senses when a POS is genuinely absent.  It never replaces an existing
sense ID merely to make its suffix prettier.
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
MARKER_RE = re.compile(r"(?<![A-Za-z])(?P<pos>adj|adv|ad|prep|conj|pron|excl|vt|vi|n|v|a|r|s)\.(?:/)?\s*", re.I)
BARE_VERB_LABEL_RE = re.compile(r"(?<![A-Za-z])(vt|vi)(?=\s)", re.I)
POS_ORDER = ("n", "v", "a", "adv", "prep", "conj", "pron", "excl", "phrase")
ALIASES = {"adj": "a", "s": "a", "vt": "v", "vi": "v", "r": "adv", "ad": "adv"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n", encoding="utf-8")


def norm(value: Any) -> str:
    raw = str(value or "").lower().strip().rstrip(".")
    return ALIASES.get(raw, raw)


def pos_field(value: Any) -> list[str]:
    raw = str(value or "")
    compact = [norm(item) for item in re.split(r"[./\s]+", raw.lower()) if item]
    if compact and all(item in POS_ORDER[:-1] for item in compact):
        return list(dict.fromkeys(compact))
    result = [norm(match.group("pos")) for match in MARKER_RE.finditer(raw)]
    return list(dict.fromkeys(item for item in result if item in POS_ORDER))


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\\n", " ")).strip(" ;；,，")


def labelled_blocks(value: Any, default_pos: str = "") -> dict[str, str]:
    text = str(value or "").replace("\\n", "\n")
    text = BARE_VERB_LABEL_RE.sub(lambda match: f"{match.group(1)}. ", text)
    matches = list(MARKER_RE.finditer(text))
    if not matches:
        return {}
    output: dict[str, list[str]] = defaultdict(list)
    leading = clean(text[: matches[0].start()])
    if leading and default_pos in POS_ORDER:
        output[default_pos].append(leading)
    for index, match in enumerate(matches):
        pos = norm(match.group("pos"))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = clean(text[match.end() : end])
        if body and body not in output[pos]:
            output[pos].append(body)
    return {pos: "；".join(parts) for pos, parts in output.items()}


def generated_sense_id(word: str, pos: str, used: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", word.lower()).strip("_") or "word"
    index = 1
    while f"{base}_{pos}_{index:02d}" in used:
        index += 1
    result = f"{base}_{pos}_{index:02d}"
    used.add(result)
    return result


def main() -> None:
    rows = read_jsonl(WORDS_PATH)
    changed: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    legacy_map: dict[str, str] = {}

    for row in rows:
        original = row.get("senses") or []
        if not original:
            continue
        word = str(row.get("word") or row.get("normalized") or "")
        before = json.dumps(original, ensure_ascii=False, sort_keys=True)
        used = {str(s.get("senseId") or "") for s in original}
        existing_pos: set[str] = set()
        source: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        rebuilt: list[dict[str, Any]] = []

        for original_sense in original:
            declared = pos_field(original_sense.get("pos"))
            # Phrases deliberately use a non-grammatical POS so they remain
            # renderable in the same component as words.
            if not declared and row.get("type") == "phrase":
                declared = ["phrase"]

            # A formerly mixed POS item is the only case where the original
            # sense is replaced.  Every unambiguous, curated sense is kept.
            if len(declared) != 1:
                for field in ("translation", "definitionZh", "definitionEn"):
                    for pos, text in labelled_blocks(original_sense.get(field)).items():
                        source[pos][field].append(text)
                # An unlabelled translation can still seed the first declared
                # POS (e.g. lack n./vt -> n).
                if declared:
                    value = clean(original_sense.get("translation"))
                    if value and not labelled_blocks(original_sense.get("translation")):
                        source[declared[0]]["translation"].append(value)
                continue

            pos = declared[0]
            existing_pos.add(pos)
            sense = dict(original_sense)
            sense["pos"] = pos
            for field in ("translation", "definitionZh", "definitionEn"):
                raw = original_sense.get(field)
                parts = labelled_blocks(raw, pos)
                if parts:
                    # Each existing sense receives only its own POS block.
                    sense[field] = parts.get(pos, "")
                    for source_pos, text in parts.items():
                        if text not in source[source_pos][field]:
                            source[source_pos][field].append(text)
                else:
                    sense[field] = clean(raw)
                    if sense[field]:
                        source[pos][field].append(sense[field])
            rebuilt.append(sense)

        # Recover missing POS values only where Chinese data exists.  WordNet
        # sometimes lists an obscure homograph (e.g. Forth river); that is
        # reported rather than silently becoming a learner sense.
        all_positions = set(source) | existing_pos
        for pos in (item for item in POS_ORDER if item in all_positions and item not in existing_pos):
            translation = "；".join(dict.fromkeys(source[pos]["translation"]))
            zh = "；".join(dict.fromkeys(source[pos]["definitionZh"]))
            en = "；".join(dict.fromkeys(source[pos]["definitionEn"]))
            if not translation:
                translation = zh
            if not translation:
                unresolved.append({"wordId": row.get("_id"), "word": word, "pos": pos, "definitionEn": en})
                continue
            template = dict(original[0])
            template.update({
                "pos": pos,
                "translation": translation,
                "definitionZh": zh,
                "definitionEn": en,
                "senseId": generated_sense_id(word, pos, used),
            })
            rebuilt.append(template)

        # Mixed original POS values need IDs that can be addressed by the
        # relation tables.  Map the old ID to the first recovered sense.
        if rebuilt and len(pos_field(original[0].get("pos"))) > 1:
            old_id = str(original[0].get("senseId") or "")
            if old_id:
                legacy_map[old_id] = str(rebuilt[0].get("senseId") or "")

        if not rebuilt:  # defensive: do not throw away a source record
            rebuilt = [dict(original[0])]
            rebuilt[0]["pos"] = "phrase" if row.get("type") == "phrase" else "n"

        row["senses"] = rebuilt
        after = json.dumps(rebuilt, ensure_ascii=False, sort_keys=True)
        if after != before:
            changed.append({"wordId": row.get("_id"), "word": word})

    write_jsonl(WORDS_PATH, rows)
    REPORT_PATH.write_text(json.dumps({
        "changedCount": len(changed), "unresolvedCount": len(unresolved),
        "changed": changed, "unresolved": unresolved, "legacySenseIdMap": legacy_map,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changed": len(changed), "unresolved": len(unresolved), "legacySenseIdMap": len(legacy_map)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
