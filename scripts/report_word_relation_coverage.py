#!/usr/bin/env python3
"""Report word relation coverage for the current import files."""

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WORDS_PATH = ROOT / "tmp" / "cloud_import" / "words.ecdict_enriched.import.json"
RELATIONS_PATH = ROOT / "tmp" / "word_relations_recommended_import" / "word_relations.import.json"
OUT_DIR = ROOT / "tmp" / "word_group_delivery"


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def first_sense(word):
    senses = word.get("senses") or []
    return senses[0] if senses else {}


def main():
    words = load_jsonl(WORDS_PATH)
    relations = load_jsonl(RELATIONS_PATH)
    by_word_id = {row["_id"]: row for row in words}
    relation_counts = Counter(row["fromWordId"] for row in relations)
    relation_types = defaultdict(Counter)
    for row in relations:
        relation_types[row["fromWordId"]][row.get("relationType") or "unknown"] += 1

    covered = []
    uncovered = []
    for word in words:
        sense = first_sense(word)
        row = {
            "wordId": word["_id"],
            "word": word.get("word"),
            "translation": sense.get("translation") or sense.get("definitionZh") or "",
            "collins": (word.get("ecdict") or {}).get("collins") or 0,
            "bnc": (word.get("ecdict") or {}).get("bnc") or 0,
            "frq": (word.get("ecdict") or {}).get("frq") or 0,
            "relationCount": relation_counts[word["_id"]],
            "relationTypes": dict(relation_types[word["_id"]])
        }
        if row["relationCount"]:
            covered.append(row)
        else:
            uncovered.append(row)

    covered.sort(key=lambda row: (-row["relationCount"], row["word"]))
    uncovered.sort(key=lambda row: (-(row["collins"] or 0), row["bnc"] or 10**9, row["word"]))
    top_uncovered = uncovered[:120]
    top_covered = covered[:120]

    report = {
        "words": len(words),
        "relations": len(relations),
        "coveredWords": len(covered),
        "uncoveredWords": len(uncovered),
        "coveragePercent": round(len(covered) * 100 / len(words), 2) if words else 0,
        "relationTypeCounts": dict(Counter(row.get("relationType") for row in relations)),
        "topCovered": top_covered[:30],
        "topUncovered": top_uncovered[:30]
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "coverage.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(OUT_DIR / "top_uncovered_words.csv", top_uncovered)
    write_csv(OUT_DIR / "top_covered_words.csv", top_covered)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def write_csv(path, rows):
    headers = ["wordId", "word", "translation", "collins", "bnc", "frq", "relationCount", "relationTypes"]
    with path.open("w", encoding="utf-8") as file:
        file.write(",".join(headers) + "\n")
        for row in rows:
            values = []
            for key in headers:
                value = row.get(key, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
                text = str(value).replace('"', '""')
                values.append(f'"{text}"')
            file.write(",".join(values) + "\n")


if __name__ == "__main__":
    main()
