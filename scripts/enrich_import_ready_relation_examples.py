#!/usr/bin/env python3
"""Fill exampleEn/exampleZh for import_ready word relations.

The app renders relation examples from word_relations.exampleEn/exampleZh.
Most generated relation edges have good explanations but no examples. This
script adds a short, stable usage-note example for every missing relation while
preserving hand-written examples.
"""

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IMPORT_DIR = ROOT / "tmp" / "import_ready"
RELATIONS_PATH = IMPORT_DIR / "word_relations.import.json"
GROUPS_PATH = IMPORT_DIR / "word_relation_groups.import.json"


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            file.write("\n")


def clean_space(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def split_explanation(relation):
    explanation = clean_space(relation.get("explanationZh") or "")
    from_word = relation.get("fromWord") or ""
    to_word = relation.get("toWord") or ""
    left = ""
    right = ""
    for part in re.split(r"[;；]", explanation):
        part = part.strip()
        lower = part.lower()
        if lower.startswith(f"{from_word.lower()}:"):
            left = part.split(":", 1)[1].strip()
        elif lower.startswith(f"{to_word.lower()}:"):
            right = part.split(":", 1)[1].strip()
    if not left:
        left = explanation[:80]
    if not right:
        right = "侧重点不同"
    return trim_zh(left), trim_zh(right)


def trim_zh(text, limit=42):
    text = clean_space(text)
    text = re.sub(r"[。；;]+$", "", text)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def build_example(relation):
    from_word = relation.get("fromWord") or relation.get("fromWordId") or ""
    to_word = relation.get("toWord") or relation.get("toWordId") or ""
    relation_type = relation.get("relationType") or ""
    left, right = split_explanation(relation)

    if relation_type == "near_synonym":
        example_en = (
            f"In this context, \"{from_word}\" fits the intended meaning; "
            f"\"{to_word}\" would shift the focus."
        )
        example_zh = f"这个语境更适合用 {from_word}，因为它偏“{left}”；{to_word} 会偏“{right}”。"
    elif relation_type == "antonym":
        example_en = (
            f"The contrast is clear: \"{from_word}\" points one way, while "
            f"\"{to_word}\" points the other."
        )
        example_zh = f"这里形成反向对比：{from_word} 偏“{left}”，而 {to_word} 偏“{right}”。"
    else:
        example_en = (
            f"Do not mix them up: use \"{from_word}\" for this meaning, "
            f"not \"{to_word}\"."
        )
        example_zh = f"不要混用：{from_word} 偏“{left}”；{to_word} 偏“{right}”。"

    return example_en, example_zh


def enrich_relations(relations):
    updated = 0
    for relation in relations:
        if relation.get("exampleEn") or relation.get("exampleZh"):
            continue
        example_en, example_zh = build_example(relation)
        relation["exampleEn"] = example_en
        relation["exampleZh"] = example_zh
        updated += 1
    return updated


def enrich_groups(groups, relations):
    by_group = defaultdict(list)
    for relation in relations:
        if relation.get("groupId"):
            by_group[relation["groupId"]].append(relation)

    updated = 0
    for group in groups:
        if group.get("examples"):
            continue
        sample_relations = by_group.get(group.get("_id"), [])
        if not sample_relations:
            continue
        relation = sample_relations[0]
        group["examples"] = [
            {
                "en": relation.get("exampleEn") or "",
                "zh": relation.get("exampleZh") or ""
            }
        ]
        updated += 1
    return updated


def main():
    relations = load_jsonl(RELATIONS_PATH)
    groups = load_jsonl(GROUPS_PATH)
    relation_updates = enrich_relations(relations)
    group_updates = enrich_groups(groups, relations)

    write_jsonl(RELATIONS_PATH, relations)
    write_jsonl(GROUPS_PATH, groups)

    report = {
        "relations": len(relations),
        "relationExamplesAdded": relation_updates,
        "relationsWithExamples": sum(1 for item in relations if item.get("exampleEn") or item.get("exampleZh")),
        "groups": len(groups),
        "groupExamplesAdded": group_updates,
        "groupsWithExamples": sum(1 for item in groups if item.get("examples")),
    }
    (IMPORT_DIR / "examples.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
