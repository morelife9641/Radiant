#!/usr/bin/env python3
"""Add stable senseId values to words JSONL import files.

The script keeps the existing senses intact and only fills missing senseId.
It is intentionally conservative: it does not split meanings or rewrite
translations.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "tmp" / "cloud_import" / "words.import.json"
DEFAULT_OUTPUT = ROOT / "tmp" / "cloud_import" / "words.with_sense_id.import.json"
DEFAULT_REPORT = ROOT / "tmp" / "cloud_import" / "words.with_sense_id.report.json"

POS_ALIASES = {
    "a": "adj",
    "ad": "adv",
    "adj": "adj",
    "adv": "adv",
    "conj": "conj",
    "excl": "excl",
    "int": "excl",
    "n": "n",
    "num": "num",
    "prep": "prep",
    "pron": "pron",
    "v": "v",
    "vi": "v",
    "vt": "v",
}


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")
    return re.sub(r"_+", "_", slug)


def normalize_pos(pos):
    raw = str(pos or "").lower().strip()
    raw = raw.replace("．", ".").replace("。", ".")
    raw = raw.rstrip(".")
    if not raw:
        return "sense"

    parts = re.split(r"[/,;\s]+", raw)
    normalized = []
    for part in parts:
        key = part.rstrip(".")
        if not key:
            continue
        normalized.append(POS_ALIASES.get(key, slugify(key)))

    normalized = [item for item in normalized if item]
    if not normalized:
        return "sense"

    unique = []
    for item in normalized:
        if item not in unique:
            unique.append(item)

    if "n" in unique and "v" in unique:
        return "n_v"
    if "adj" in unique and "adv" in unique:
        return "adj_adv"
    if len(unique) > 2:
        return "_".join(unique[:2])
    return "_".join(unique)


def sense_id_for(word, sense, counter):
    existing = str(sense.get("senseId") or "").strip()
    if existing:
        return existing

    base = slugify(word.get("normalized") or word.get("word") or word.get("_id") or "word")
    pos = normalize_pos(sense.get("pos"))
    key = (base, pos)
    counter[key] += 1
    return f"{base}_{pos}_{counter[key]:02d}"


def load_jsonl(path):
    items = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON at {path}:{line_no}: {exc}") from exc
    return items


def write_jsonl(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for item in items:
            file.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")))
            file.write("\n")


def main(argv):
    input_path = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_INPUT
    output_path = Path(argv[2]).resolve() if len(argv) > 2 else DEFAULT_OUTPUT
    report_path = Path(argv[3]).resolve() if len(argv) > 3 else DEFAULT_REPORT

    words = load_jsonl(input_path)
    changed_words = 0
    added_sense_ids = 0
    existing_sense_ids = 0
    pos_counts = Counter()

    for word in words:
      senses = word.get("senses")
      if not isinstance(senses, list):
          continue

      counter = Counter()
      changed = False
      for sense in senses:
          if not isinstance(sense, dict):
              continue
          before = sense.get("senseId")
          sense_id = sense_id_for(word, sense, counter)
          pos_counts[normalize_pos(sense.get("pos"))] += 1
          if before:
              existing_sense_ids += 1
          else:
              sense["senseId"] = sense_id
              added_sense_ids += 1
              changed = True

      if changed:
          changed_words += 1

    write_jsonl(output_path, words)

    report = {
        "input": str(input_path),
        "output": str(output_path),
        "words": len(words),
        "changedWords": changed_words,
        "addedSenseIds": added_sense_ids,
        "existingSenseIds": existing_sense_ids,
        "posCounts": dict(sorted(pos_counts.items())),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv)
