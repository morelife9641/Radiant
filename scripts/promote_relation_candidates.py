#!/usr/bin/env python3
"""Promote a conservative subset of algorithmic candidates to import JSONL."""

import json
import re
import sys
from itertools import permutations
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CANDIDATES = ROOT / "tmp" / "word_relation_candidates" / "relation_candidates.preview.json"
DEFAULT_WORDS = ROOT / "tmp" / "cloud_import" / "words.ecdict_enriched.import.json"
DEFAULT_OUT_DIR = ROOT / "tmp" / "word_relations_algorithmic_import"

ANTONYM_PREFIXES = (
    ("in", ""),
    ("im", ""),
    ("un", ""),
    ("dis", ""),
    ("non", ""),
    ("over", "under"),
    ("under", "over"),
    ("max", "min"),
    ("min", "max"),
)


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")
    return re.sub(r"_+", "_", slug)


def first_sense(word):
    senses = word.get("senses") or []
    return senses[0] if senses else {}


def is_likely_antonym(a, b):
    a = a.lower()
    b = b.lower()
    for prefix, other in ANTONYM_PREFIXES:
        if other:
            if a.startswith(prefix) and b.startswith(other):
                return True
            if b.startswith(prefix) and a.startswith(other):
                return True
        else:
            if a.startswith(prefix) and a[len(prefix):] == b:
                return True
            if b.startswith(prefix) and b[len(prefix):] == a:
                return True
    return False


def relation_type_for(row):
    if is_likely_antonym(row["fromWord"], row["toWord"]):
        return "antonym"
    return "near_synonym"


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            file.write("\n")


def main(argv):
    candidates_path = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_CANDIDATES
    words_path = Path(argv[2]).resolve() if len(argv) > 2 else DEFAULT_WORDS
    out_dir = Path(argv[3]).resolve() if len(argv) > 3 else DEFAULT_OUT_DIR

    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    words = {word["_id"]: word for word in load_jsonl(words_path)}

    promoted_pairs = []
    review_only = []
    for row in candidates:
        score = float(row.get("score") or 0)
        # Keep only very high-confidence semantic matches or obvious prefix
        # antonyms. Everything else remains preview-only.
        if score >= 0.48 or is_likely_antonym(row["fromWord"], row["toWord"]):
            promoted_pairs.append(row)
        else:
            review_only.append(row)

    groups = []
    relations = []
    for row in promoted_pairs:
        left = words.get(row["fromWordId"])
        right = words.get(row["toWordId"])
        if not left or not right:
            continue
        relation_type = relation_type_for(row)
        group_id = f"group_algorithmic_{slugify(left['word'])}_{slugify(right['word'])}"
        groups.append({
            "_id": group_id,
            "type": "antonym_axis" if relation_type == "antonym" else "synonym_set",
            "title": f"{left['word']} / {right['word']}",
            "memberWordIds": [left["_id"], right["_id"]],
            "members": [
                {"wordId": left["_id"], "word": left["word"], "role": "member", "shortZh": row.get("fromTranslation", "")[:80]},
                {"wordId": right["_id"], "word": right["word"], "role": "member", "shortZh": row.get("toTranslation", "")[:80]},
            ],
            "summaryEn": "",
            "summaryZh": "算法根据英文/中文释义相似度生成的候选关系，已通过高置信阈值筛选。",
            "dimensions": [],
            "examples": [],
            "source": {
                "type": "algorithmic_definition_similarity",
                "score": row.get("score"),
                "needsReview": True
            },
            "status": "draft",
            "createdAt": 1780646400000,
            "updatedAt": 1780646400000
        })
        for source, target in permutations([left, right], 2):
            source_sense = first_sense(source)
            target_sense = first_sense(target)
            relation_id = (
                f"rel_{source['_id']}_{source_sense.get('senseId') or 'any'}_"
                f"{target['_id']}_{target_sense.get('senseId') or 'any'}_{relation_type}"
            )
            relations.append({
                "_id": relation_id,
                "fromWordId": source["_id"],
                "fromWord": source["word"],
                "toWordId": target["_id"],
                "toWord": target["word"],
                "relationType": relation_type,
                "groupId": group_id,
                "direction": "bidirectional",
                "strength": 4 if float(row.get("score") or 0) >= 0.5 else 3,
                "senseScope": {
                    "pos": source_sense.get("pos") or "",
                    "fromSenseId": source_sense.get("senseId") or "any",
                    "toSenseId": target_sense.get("senseId") or "any"
                },
                "explanationEn": "",
                "explanationZh": build_explanation(source, target, row, relation_type),
                "exampleEn": "",
                "exampleZh": "",
                "tags": ["ielts", "algorithmic_candidate", relation_type],
                "status": "draft",
                "createdAt": 1780646400000,
                "updatedAt": 1780646400000
            })

    write_jsonl(out_dir / "word_relation_groups.draft.import.json", groups)
    write_jsonl(out_dir / "word_relations.draft.import.json", relations)
    (out_dir / "review_only.preview.json").write_text(json.dumps(review_only, ensure_ascii=False, indent=2), encoding="utf-8")
    report = {
        "inputCandidates": len(candidates),
        "promotedPairs": len(promoted_pairs),
        "draftGroups": len(groups),
        "draftRelations": len(relations),
        "reviewOnly": len(review_only),
        "status": "draft"
    }
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def build_explanation(source, target, row, relation_type):
    if relation_type == "antonym":
        return f"{source['word']} 与 {target['word']} 可能构成反义或方向相反的关系，请人工确认。"
    source_text = row.get("fromTranslation", "")
    target_text = row.get("toTranslation", "")
    return f"{source['word']}: {source_text}；{target['word']}: {target_text}"


if __name__ == "__main__":
    main(sys.argv)
