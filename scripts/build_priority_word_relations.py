#!/usr/bin/env python3
"""Recover high-priority word relations from skipped resemble groups.

The first resemble pass skipped two-word leftovers from larger source groups.
That kept quality high, but it also left useful high-frequency IELTS words
uncovered. This script selectively recovers those skipped groups when:

- at least one kept word is in the high-priority uncovered list;
- at least two current words remain in the group;
- every kept word has an explicit explanation line in resemble.txt.

Output files keep the .json suffix but are JSONL for cloud database import.
"""

import csv
import json
import re
import sys
from itertools import permutations
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORDS = ROOT / "tmp" / "cloud_import" / "words.ecdict_enriched.import.json"
DEFAULT_RESEMBLE = ROOT / "ECDICT-master" / "resemble.txt"
DEFAULT_PRIORITY_CSV = ROOT / "tmp" / "word_group_delivery" / "top_uncovered_words.csv"
DEFAULT_EXISTING_RELATIONS = ROOT / "tmp" / "word_relations_published_balanced_import" / "word_relations.import.json"
DEFAULT_OUT_DIR = ROOT / "tmp" / "word_relations_priority_import"


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")
    return re.sub(r"_+", "_", slug)


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            file.write("\n")


def parse_resemble(path):
    groups = []
    current = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("%"):
            if current:
                groups.append(current)
            terms = [item.strip().lower() for item in line[1:].split(",") if item.strip()]
            current = {"terms": terms, "lines": []}
            continue
        if current:
            current["lines"].append(line)
    if current:
        groups.append(current)
    return groups


def first_group_summary(lines):
    for line in lines:
        if line.startswith("这组词"):
            return line
    return ""


def explanation_for(term, lines):
    prefix = f"- {term}:"
    for line in lines:
        if line.lower().startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def first_sense(word):
    senses = word.get("senses") if isinstance(word, dict) else []
    return senses[0] if isinstance(senses, list) and senses else {}


NEAR_SYNONYM_PRIORITY_SETS = [
    {"appear", "emerge"},
    {"attempt", "endeavour"},
    {"effort", "endeavour"},
    {"occur", "appear", "emerge"},
]


def relation_type_for_words(words):
    word_set = {str(word.get("word") or "").lower() for word in words}
    if any(word_set.issubset(item) for item in NEAR_SYNONYM_PRIORITY_SETS):
        return "near_synonym"
    return "confusing"


def relation_id_type_for_words(words, relation_type):
    # Some batches were already imported with a `_confusing` id suffix. Keep
    # those ids stable and update the relationType field in place.
    word_set = {str(word.get("word") or "").lower() for word in words}
    if relation_type == "near_synonym" and word_set == {"appear", "emerge"}:
        return "confusing"
    return relation_type


def load_priority_words(path, limit):
    priority = set()
    with path.open(encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader):
            if index >= limit:
                break
            word_id = (row.get("wordId") or "").strip()
            if word_id:
                priority.add(word_id)
    return priority


def main(argv):
    limit = int(argv[1]) if len(argv) > 1 else 160
    words_path = Path(argv[2]).resolve() if len(argv) > 2 else DEFAULT_WORDS
    out_dir = Path(argv[3]).resolve() if len(argv) > 3 else DEFAULT_OUT_DIR

    words = load_jsonl(words_path)
    by_normalized = {str(item.get("normalized") or item.get("word") or "").lower(): item for item in words}
    by_word = {str(item.get("word") or "").lower(): item for item in words}
    priority_word_ids = load_priority_words(DEFAULT_PRIORITY_CSV, limit)
    existing_relation_ids = {row["_id"] for row in load_jsonl(DEFAULT_EXISTING_RELATIONS)}

    def find_word(term):
        return by_normalized.get(term.lower()) or by_word.get(term.lower())

    groups_out = []
    relations_out = []
    rejected = []
    review_groups = []
    seen_group_ids = set()
    seen_relation_ids = set(existing_relation_ids)

    for source_index, group in enumerate(parse_resemble(DEFAULT_RESEMBLE), 1):
        members = []
        missing = []
        for term in group["terms"]:
            word = find_word(term)
            if word:
                members.append(word)
            else:
                missing.append(term)

        if len(members) < 2:
            continue

        priority_members = [word for word in members if word["_id"] in priority_word_ids]
        if not priority_members:
            continue

        explanations = {word["_id"]: explanation_for(word["word"].lower(), group["lines"]) for word in members}
        if any(not explanations[word["_id"]] for word in members):
            rejected.append({
                "sourceIndex": source_index,
                "terms": group["terms"],
                "kept": [word["word"] for word in members],
                "priorityKept": [word["word"] for word in priority_members],
                "missing": missing,
                "reason": "missing_member_explanation"
            })
            continue

        summary = first_group_summary(group["lines"])
        if not summary:
            review_groups.append({
                "sourceIndex": source_index,
                "terms": group["terms"],
                "kept": [word["word"] for word in members],
                "priorityKept": [word["word"] for word in priority_members],
                "missing": missing,
                "reason": "no_group_summary"
            })
            continue

        member_words = [item["word"] for item in members]
        relation_type = relation_type_for_words(members)
        relation_id_type = relation_id_type_for_words(members, relation_type)
        group_id = f"group_priority_resemble_{source_index}_{slugify('_'.join(member_words[:8]))}"
        if group_id in seen_group_ids:
            continue
        seen_group_ids.add(group_id)

        groups_out.append({
            "_id": group_id,
            "type": "synonym_set" if relation_type == "near_synonym" else "confusing_set",
            "title": " / ".join(member_words),
            "memberWordIds": [item["_id"] for item in members],
            "members": [
                {
                    "wordId": item["_id"],
                    "word": item["word"],
                    "role": "member",
                    "shortZh": explanations[item["_id"]][:80]
                }
                for item in members
            ],
            "summaryEn": "",
            "summaryZh": summary,
            "dimensions": [
                {
                    "key": "usage_difference",
                    "nameZh": "用法区别",
                    "items": [
                        {"wordId": item["_id"], "textZh": explanations[item["_id"]]}
                        for item in members
                    ]
                }
            ],
            "examples": [],
            "source": {
                "type": "ecdict_resemble_priority_recovery",
                "file": "ECDICT-master/resemble.txt",
                "sourceIndex": source_index,
                "originalTerms": group["terms"],
                "missingTerms": missing,
                "priorityLimit": limit
            },
            "status": "published",
            "createdAt": 1780732800000,
            "updatedAt": 1780732800000
        })

        for left, right in permutations(members, 2):
            left_sense = first_sense(left)
            right_sense = first_sense(right)
            relation_id = (
                f"rel_{left['_id']}_{left_sense.get('senseId') or 'any'}_"
                f"{right['_id']}_{right_sense.get('senseId') or 'any'}_{relation_id_type}"
            )
            if relation_id in seen_relation_ids:
                continue
            seen_relation_ids.add(relation_id)
            relations_out.append({
                "_id": relation_id,
                "fromWordId": left["_id"],
                "fromWord": left["word"],
                "toWordId": right["_id"],
                "toWord": right["word"],
                "relationType": relation_type,
                "groupId": group_id,
                "direction": "bidirectional",
                "strength": 4 if len(members) <= 5 else 3,
                "senseScope": {
                    "pos": left_sense.get("pos") or "",
                    "fromSenseId": left_sense.get("senseId") or "any",
                    "toSenseId": right_sense.get("senseId") or "any"
                },
                "explanationEn": "",
                "explanationZh": f"{left['word']}: {explanations[left['_id']]}; {right['word']}: {explanations[right['_id']]}",
                "exampleEn": "",
                "exampleZh": "",
                "tags": ["ielts", "ecdict_resemble", "priority_recovery", relation_type],
                "status": "published",
                "createdAt": 1780732800000,
                "updatedAt": 1780732800000
            })

    write_jsonl(out_dir / "word_relation_groups.import.json", groups_out)
    write_jsonl(out_dir / "word_relations.import.json", relations_out)
    write_jsonl(out_dir / "rejected.preview.json", rejected)
    write_jsonl(out_dir / "review_groups.preview.json", review_groups)

    report = {
        "priorityLimit": limit,
        "groups": len(groups_out),
        "relations": len(relations_out),
        "rejected": len(rejected),
        "reviewGroups": len(review_groups),
        "outputDir": str(out_dir)
    }
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv)
