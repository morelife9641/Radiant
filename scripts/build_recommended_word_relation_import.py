#!/usr/bin/env python3
"""Merge reviewed relation batches into one recommended import package."""

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "tmp" / "word_relations_recommended_import"

GROUP_FILES = [
    ROOT / "tmp" / "word_relations_import" / "word_relation_groups.import.json",
    ROOT / "tmp" / "word_relations_published_balanced_import" / "word_relation_groups.import.json",
    ROOT / "tmp" / "word_relations_priority_import" / "word_relation_groups.import.json",
    ROOT / "tmp" / "word_relations_curated_import" / "word_relation_groups.import.json",
]

RELATION_FILES = [
    ROOT / "tmp" / "word_relations_import" / "word_relations.with_sense_id.import.json",
    ROOT / "tmp" / "word_relations_published_balanced_import" / "word_relations.import.json",
    ROOT / "tmp" / "word_relations_priority_import" / "word_relations.import.json",
    ROOT / "tmp" / "word_relations_curated_import" / "word_relations.import.json",
]


def load_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            file.write("\n")


def merge_by_id(files):
    rows = []
    duplicates = []
    seen = set()
    for path in files:
        for row in load_jsonl(path):
            row_id = row.get("_id")
            if row_id in seen:
                duplicates.append({**row, "duplicateFromFile": str(path.relative_to(ROOT))})
                continue
            seen.add(row_id)
            rows.append(row)
    return rows, duplicates


def main():
    groups, duplicate_groups = merge_by_id(GROUP_FILES)
    relations, duplicate_relations = merge_by_id(RELATION_FILES)

    valid_group_ids = {group["_id"] for group in groups}
    orphan_relations = [row for row in relations if row.get("groupId") and row.get("groupId") not in valid_group_ids]
    relations = [row for row in relations if row not in orphan_relations]

    write_jsonl(OUT_DIR / "word_relation_groups.import.json", groups)
    write_jsonl(OUT_DIR / "word_relations.import.json", relations)
    write_jsonl(OUT_DIR / "duplicate_groups.preview.json", duplicate_groups)
    write_jsonl(OUT_DIR / "duplicate_relations.preview.json", duplicate_relations)
    write_jsonl(OUT_DIR / "orphan_relations.preview.json", orphan_relations)

    report = {
        "groups": len(groups),
        "relations": len(relations),
        "duplicateGroups": len(duplicate_groups),
        "duplicateRelations": len(duplicate_relations),
        "orphanRelations": len(orphan_relations),
        "relationTypeCounts": dict(Counter(row.get("relationType") for row in relations)),
        "sourceFiles": {
            "groups": [str(path.relative_to(ROOT)) for path in GROUP_FILES],
            "relations": [str(path.relative_to(ROOT)) for path in RELATION_FILES]
        },
        "outputDir": str(OUT_DIR)
    }
    (OUT_DIR / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
