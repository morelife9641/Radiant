#!/usr/bin/env python3
"""Build word relation groups from ECDICT resemble.txt.

This is a conservative generator:
- only uses groups explicitly listed in resemble.txt;
- only keeps members that already exist in the current words import;
- treats each group as a confusing/near-synonym set with bidirectional edges;
- writes JSONL files with .json suffix for cloud database import.
"""

import json
import re
import sys
from itertools import permutations
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORDS = ROOT / "tmp" / "cloud_import" / "words.with_sense_id.import.json"
DEFAULT_RESEMBLE = ROOT / "ECDICT-master" / "resemble.txt"
DEFAULT_OUT_DIR = ROOT / "tmp" / "word_relations_resemble_import"


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")
    return re.sub(r"_+", "_", slug)


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
            current = {
                "terms": terms,
                "lines": []
            }
            continue
        if current:
            current["lines"].append(line)
    if current:
        groups.append(current)
    return groups


def first_sentence(lines):
    for line in lines:
        if line.startswith("这组词") or line.startswith("-"):
            return line
    return lines[0] if lines else ""


def explanation_for(term, lines):
    prefix = f"- {term}:"
    for line in lines:
        if line.lower().startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def relation_type_for(group_size):
    # resemble.txt is mostly "how to distinguish similar words"; model it as
    # confusing for UI placement, while still usable as near-synonym material.
    return "confusing" if group_size <= 6 else "near_synonym"


def main(argv):
    words_path = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_WORDS
    resemble_path = Path(argv[2]).resolve() if len(argv) > 2 else DEFAULT_RESEMBLE
    out_dir = Path(argv[3]).resolve() if len(argv) > 3 else DEFAULT_OUT_DIR

    words = load_jsonl(words_path)
    by_normalized = {str(item.get("normalized") or item.get("word") or "").lower(): item for item in words}
    by_word = {str(item.get("word") or "").lower(): item for item in words}

    def find_word(term):
        return by_normalized.get(term.lower()) or by_word.get(term.lower())

    groups_out = []
    relations_out = []
    skipped = []

    for source_index, group in enumerate(parse_resemble(resemble_path), 1):
        members = []
        missing = []
        for term in group["terms"]:
            word = find_word(term)
            if word:
                members.append(word)
            else:
                missing.append(term)

        # Avoid weak two-word leftovers from a much larger group; they often lose
        # too much context. Keep original two-word groups though.
        if len(members) < 2 or (len(members) == 2 and len(group["terms"]) > 3):
            skipped.append({
                "sourceIndex": source_index,
                "terms": group["terms"],
                "kept": [item.get("word") for item in members],
                "missing": missing,
                "reason": "not_enough_current_words"
            })
            continue

        member_words = [item["word"] for item in members]
        group_id = f"group_resemble_{slugify('_'.join(member_words[:8]))}"
        relation_type = relation_type_for(len(members))
        summary = first_sentence(group["lines"])

        group_doc = {
            "_id": group_id,
            "type": "confusing_set" if relation_type == "confusing" else "synonym_set",
            "title": " / ".join(member_words),
            "memberWordIds": [item["_id"] for item in members],
            "members": [
                {
                    "wordId": item["_id"],
                    "word": item["word"],
                    "role": "member",
                    "shortZh": explanation_for(item["word"].lower(), group["lines"])[:80]
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
                        {
                            "wordId": item["_id"],
                            "textZh": explanation_for(item["word"].lower(), group["lines"])
                        }
                        for item in members
                        if explanation_for(item["word"].lower(), group["lines"])
                    ]
                }
            ],
            "examples": [],
            "source": {
                "type": "ecdict_resemble",
                "file": str(resemble_path.relative_to(ROOT)) if resemble_path.is_relative_to(ROOT) else str(resemble_path),
                "sourceIndex": source_index,
                "originalTerms": group["terms"],
                "missingTerms": missing
            },
            "status": "published",
            "createdAt": 1780646400000,
            "updatedAt": 1780646400000
        }
        groups_out.append(group_doc)

        for left, right in permutations(members, 2):
            left_sense = first_sense_id(left)
            right_sense = first_sense_id(right)
            left_word = left["word"]
            right_word = right["word"]
            left_expl = explanation_for(left_word.lower(), group["lines"])
            right_expl = explanation_for(right_word.lower(), group["lines"])
            explanation = build_pair_explanation(left_word, right_word, left_expl, right_expl)
            relation_id = (
                f"rel_{left['_id']}_{left_sense or 'any'}_"
                f"{right['_id']}_{right_sense or 'any'}_{relation_type}"
            )
            relations_out.append({
                "_id": relation_id,
                "fromWordId": left["_id"],
                "fromWord": left_word,
                "toWordId": right["_id"],
                "toWord": right_word,
                "relationType": relation_type,
                "groupId": group_id,
                "direction": "bidirectional",
                "strength": 4 if len(members) <= 5 else 3,
                "senseScope": {
                    "pos": first_pos(left),
                    "fromSenseId": left_sense or "any",
                    "toSenseId": right_sense or "any"
                },
                "explanationEn": "",
                "explanationZh": explanation,
                "exampleEn": "",
                "exampleZh": "",
                "tags": ["ielts", "ecdict_resemble", relation_type],
                "status": "published",
                "createdAt": 1780646400000,
                "updatedAt": 1780646400000
            })

    write_jsonl(out_dir / "word_relation_groups.import.json", groups_out)
    write_jsonl(out_dir / "word_relations.import.json", relations_out)
    (out_dir / "skipped.preview.json").write_text(
        json.dumps(skipped, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    report = {
        "words": len(words),
        "groups": len(groups_out),
        "relations": len(relations_out),
        "skipped": len(skipped),
        "outputDir": str(out_dir)
    }
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def first_sense_id(word):
    senses = word.get("senses") if isinstance(word, dict) else []
    if isinstance(senses, list) and senses:
        return senses[0].get("senseId") or ""
    return ""


def first_pos(word):
    senses = word.get("senses") if isinstance(word, dict) else []
    if isinstance(senses, list) and senses:
        return senses[0].get("pos") or ""
    return ""


def build_pair_explanation(left_word, right_word, left_expl, right_expl):
    parts = []
    if left_expl:
        parts.append(f"{left_word}: {left_expl}")
    if right_expl:
        parts.append(f"{right_word}: {right_expl}")
    return "；".join(parts)


if __name__ == "__main__":
    main(sys.argv)
