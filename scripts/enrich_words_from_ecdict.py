#!/usr/bin/env python3
"""Enrich existing words import with ECDICT metadata.

Conservative rules:
- keep the current display translation unchanged;
- fill empty senses[].definitionEn / definitionZh from ECDICT;
- add ecdict metadata under words.ecdict;
- preserve existing fields for easy cloud import overwrite by _id.
"""

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORDS = ROOT / "tmp" / "cloud_import" / "words.with_sense_id.import.json"
DEFAULT_ECDICT = ROOT / "ECDICT-master" / "ecdict.csv"
DEFAULT_OUTPUT = ROOT / "tmp" / "cloud_import" / "words.ecdict_enriched.import.json"
DEFAULT_REPORT = ROOT / "tmp" / "cloud_import" / "words.ecdict_enriched.report.json"


def load_jsonl(path):
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON at {path}:{line_no}: {exc}") from exc
    return rows


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            file.write("\n")


def clean_definition(value):
    lines = []
    for line in str(value or "").splitlines():
        line = line.strip()
        if not line:
            continue
        lines.append(line)
    return "\n".join(lines)


def clean_translation(value):
    lines = []
    for line in str(value or "").splitlines():
        line = line.strip()
        if not line or line.startswith("[网络]"):
            continue
        # Drop domain-only hints but keep actual definitions.
        if re.match(r"^\[[^\]]+\]\s*$", line):
            continue
        lines.append(line)
    return "\n".join(lines)


def load_ecdict(path):
    data = {}
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            word = str(row.get("word") or "").strip().lower()
            if not word:
                continue
            data[word] = row
    return data


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def main(argv):
    words_path = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_WORDS
    ecdict_path = Path(argv[2]).resolve() if len(argv) > 2 else DEFAULT_ECDICT
    output_path = Path(argv[3]).resolve() if len(argv) > 3 else DEFAULT_OUTPUT
    report_path = Path(argv[4]).resolve() if len(argv) > 4 else DEFAULT_REPORT

    words = load_jsonl(words_path)
    ecdict = load_ecdict(ecdict_path)

    matched = 0
    definition_en_added = 0
    definition_zh_added = 0
    metadata_added = 0
    missing = []

    for word in words:
        key = str(word.get("normalized") or word.get("word") or "").strip().lower()
        row = ecdict.get(key)
        if not row:
            missing.append(key)
            continue

        matched += 1
        definition_en = clean_definition(row.get("definition"))
        definition_zh = clean_translation(row.get("translation"))

        senses = word.get("senses")
        if isinstance(senses, list):
            for sense in senses[:1]:
                if not isinstance(sense, dict):
                    continue
                if definition_en and not sense.get("definitionEn"):
                    sense["definitionEn"] = definition_en
                    definition_en_added += 1
                if definition_zh and not sense.get("definitionZh"):
                    sense["definitionZh"] = definition_zh
                    definition_zh_added += 1

        word["ecdict"] = {
            "collins": to_int(row.get("collins")),
            "oxford": row.get("oxford") == "1",
            "tag": str(row.get("tag") or "").split(),
            "bnc": to_int(row.get("bnc")),
            "frq": to_int(row.get("frq")),
            "exchange": row.get("exchange") or ""
        }
        metadata_added += 1

    write_jsonl(output_path, words)
    report = {
        "input": str(words_path),
        "output": str(output_path),
        "words": len(words),
        "matched": matched,
        "missing": len(missing),
        "definitionEnAdded": definition_en_added,
        "definitionZhAdded": definition_zh_added,
        "metadataAdded": metadata_added,
        "missingPreview": missing[:50]
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv)
