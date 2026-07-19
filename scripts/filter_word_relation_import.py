#!/usr/bin/env python3
"""Create a cleaner import set from generated word relation JSONL files.

The full resemble import is useful, but some ECDICT groups lose context when
missing terms are not in the current IELTS word list. This script keeps only
the entries that are suitable for direct publishing and puts the rest into
preview files for later review.
"""

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IN_DIR = ROOT / "tmp" / "word_relations_resemble_import"
DEFAULT_OUT_DIR = ROOT / "tmp" / "word_relations_published_clean_import"


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


def is_clean_group(group, preset):
    source = group.get("source") or {}
    summary = str(group.get("summaryZh") or "").strip()
    dimensions = group.get("dimensions") or []
    dimension_items = dimensions[0].get("items") if dimensions and isinstance(dimensions[0], dict) else []
    member_word_ids = group.get("memberWordIds") or []

    if summary.startswith("-"):
        return False, "summary_is_single_term_note"
    if preset == "balanced" and not summary.startswith("这组词"):
        return False, "summary_is_not_group_note"
    if preset == "strict" and source.get("missingTerms"):
        return False, "has_missing_terms"
    if len(member_word_ids) < 2:
        return False, "not_enough_members"
    if len(dimension_items or []) < len(member_word_ids):
        return False, "incomplete_dimension_items"
    return True, "clean"


def main(argv):
    in_dir = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_IN_DIR
    out_dir = Path(argv[2]).resolve() if len(argv) > 2 else DEFAULT_OUT_DIR
    preset = argv[3] if len(argv) > 3 else "strict"
    if preset not in {"strict", "balanced"}:
        raise SystemExit("preset must be strict or balanced")

    groups = load_jsonl(in_dir / "word_relation_groups.import.json")
    relations = load_jsonl(in_dir / "word_relations.import.json")

    clean_groups_raw = []
    review_groups = []
    reasons = Counter()
    for group in groups:
        ok, reason = is_clean_group(group, preset)
        reasons[reason] += 1
        if ok:
            clean_groups_raw.append(group)
        else:
            review_groups.append({**group, "reviewReason": reason})

    clean_groups = []
    duplicate_clean_groups = []
    seen_group_ids = set()
    for group in clean_groups_raw:
        group_id = group.get("_id")
        if group_id in seen_group_ids:
            duplicate_clean_groups.append({**group, "reviewReason": "duplicate_group_id"})
            continue
        seen_group_ids.add(group_id)
        clean_groups.append(group)

    clean_group_ids = {group["_id"] for group in clean_groups}
    clean_relations_raw = [row for row in relations if row.get("groupId") in clean_group_ids]
    review_relations = [row for row in relations if row.get("groupId") not in clean_group_ids]
    clean_relations = []
    duplicate_clean_relations = []
    seen_relation_ids = set()
    for row in clean_relations_raw:
        row_id = row.get("_id")
        if row_id in seen_relation_ids:
            duplicate_clean_relations.append({**row, "reviewReason": "duplicate_relation_id"})
            continue
        seen_relation_ids.add(row_id)
        clean_relations.append(row)

    write_jsonl(out_dir / "word_relation_groups.import.json", clean_groups)
    write_jsonl(out_dir / "word_relations.import.json", clean_relations)
    write_jsonl(out_dir / "review_groups.preview.json", review_groups)
    write_jsonl(out_dir / "review_relations.preview.json", review_relations)
    write_jsonl(out_dir / "duplicate_groups.preview.json", duplicate_clean_groups)
    write_jsonl(out_dir / "duplicate_relations.preview.json", duplicate_clean_relations)

    report = {
        "inputGroups": len(groups),
        "inputRelations": len(relations),
        "cleanGroups": len(clean_groups),
        "cleanRelations": len(clean_relations),
        "duplicateCleanGroups": len(duplicate_clean_groups),
        "duplicateCleanRelations": len(duplicate_clean_relations),
        "reviewGroups": len(review_groups),
        "reviewRelations": len(review_relations),
        "reasonCounts": dict(reasons),
        "preset": preset,
        "outputDir": str(out_dir)
    }
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv)
