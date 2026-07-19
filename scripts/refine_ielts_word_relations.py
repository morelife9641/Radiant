#!/usr/bin/env python3
"""Refine IELTS word relation examples and publication status.

The first relation batch mixed curated explanations with many generated
placeholder examples. This pass keeps the useful relation structure, replaces
placeholder examples with non-truncated usage contrast notes, and marks the
content as draft pending human review rather than published.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
RELATIONS_PATH = DATA_DIR / "word_relations.json"
GROUPS_PATH = DATA_DIR / "word_relation_groups.json"
REPORT_PATH = DATA_DIR / "word_relations_refine_report.json"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def clean_space(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def strip_final_punct(text: str) -> str:
    return clean_space(text).rstrip("。.;； ")


def remove_ellipsis(text: str) -> str:
    return clean_space(str(text or "").replace("...", "").replace("…", ""))


def split_relation_explanation(relation: dict) -> tuple[str, str]:
    """Return full Chinese usage notes for from/to words."""
    explanation = remove_ellipsis(relation.get("explanationZh") or "")
    from_word = (relation.get("fromWord") or "").lower()
    to_word = (relation.get("toWord") or "").lower()
    notes: dict[str, str] = {}

    for part in re.split(r"[;；]", explanation):
        part = strip_final_punct(part)
        if ":" not in part and "：" not in part:
            continue
        word, note = re.split(r"[:：]", part, maxsplit=1)
        notes[word.strip().lower()] = strip_final_punct(note)

    left = notes.get(from_word) or explanation
    right = notes.get(to_word) or "侧重点不同，需要结合语境判断"
    return strip_final_punct(left), strip_final_punct(right)


def build_relation_examples(relation: dict, words_by_id: dict[str, dict]) -> tuple[str, str]:
    from_word = relation.get("fromWord") or ""
    to_word = relation.get("toWord") or ""
    relation_type = relation.get("relationType") or "confusing"
    left_zh, right_zh = split_relation_explanation(relation)
    if relation_type == "near_synonym":
        example_en = (
            f"In academic reading, \"{from_word}\" and \"{to_word}\" may be close, "
            f"but the two words are not fully interchangeable in this contrast."
        )
        example_zh = f"在学术阅读中，{from_word} 与 {to_word} 可能接近，但 {from_word} 偏“{left_zh}”，{to_word} 偏“{right_zh}”。"
    elif relation_type == "antonym":
        example_en = (
            f"The contrast is between \"{from_word}\" and \"{to_word}\"; "
            f"use the Chinese note to check which side of the contrast is intended."
        )
        example_zh = f"这两个词构成反向对比：{from_word} 偏“{left_zh}”，{to_word} 偏“{right_zh}”。"
    else:
        example_en = (
            f"Treat \"{from_word}\" and \"{to_word}\" as a usage contrast, "
            f"not as two freely interchangeable words."
        )
        example_zh = f"选择 {from_word} 时，重点应是“{left_zh}”；只有当语义转向“{right_zh}”时，才适合用 {to_word}。"
    return clean_space(example_en), clean_space(example_zh)


def normalize_relation(relation: dict, words_by_id: dict[str, dict]) -> tuple[dict, bool]:
    original_example = relation.get("exampleEn") or ""
    original_zh = relation.get("exampleZh") or ""
    is_placeholder = (
        original_example.startswith("Do not mix them up")
        or original_example.startswith("Choose \"")
        or "when the intended focus is" in original_example
        or "focus shifts to" in original_example
        or "..." in original_zh
        or "…" in original_zh
        or (relation.get("quality") or {}).get("exampleType") == "usage_contrast"
    )

    relation["explanationZh"] = remove_ellipsis(relation.get("explanationZh") or "")
    should_replace_explanation_en = (
        not relation.get("explanationEn")
        or "ecdict_resemble" in (relation.get("tags") or [])
        or " focuses on " in str(relation.get("explanationEn") or "")
    )
    if should_replace_explanation_en:
        relation["explanationEn"] = (
            f"{relation.get('fromWord')} and {relation.get('toWord')} are close enough to confuse, "
            f"but they differ in usage focus."
        )

    if is_placeholder or not original_example or not original_zh:
        relation["exampleEn"], relation["exampleZh"] = build_relation_examples(relation, words_by_id)
    else:
        relation["exampleEn"] = clean_space(original_example)
        relation["exampleZh"] = remove_ellipsis(original_zh)

    relation["status"] = "draft"
    relation["reviewStatus"] = "ai_enriched_pending_human_review"
    relation["quality"] = {
        "exampleType": "usage_contrast",
        "placeholderRemoved": bool(is_placeholder),
        "needsHumanReview": True,
    }
    relation["updatedAt"] = None
    return relation, is_placeholder


def build_group_example(group: dict, words_by_id: dict[str, dict]) -> dict:
    members = group.get("members") or []
    if len(members) < 2:
        return {"en": "", "zh": ""}
    left = members[0]
    right = members[1]
    left_word = left.get("word") or left.get("wordId", "")
    right_word = right.get("word") or right.get("wordId", "")
    left_zh = strip_final_punct(remove_ellipsis(left.get("shortZh") or ""))
    right_zh = strip_final_punct(remove_ellipsis(right.get("shortZh") or ""))
    return {
        "en": (
            f"This set contrasts words that may look similar in reading, "
            f"but each member has a different usage focus."
        ),
        "zh": f"这组词中，{left_word} 偏“{left_zh}”；{right_word} 偏“{right_zh}”。",
    }


def normalize_group(group: dict, words_by_id: dict[str, dict]) -> dict:
    for member in group.get("members") or []:
        member["shortZh"] = remove_ellipsis(member.get("shortZh") or "")
    for dimension in group.get("dimensions") or []:
        for item in dimension.get("items") or []:
            item["textZh"] = remove_ellipsis(item.get("textZh") or "")

    group["summaryZh"] = remove_ellipsis(group.get("summaryZh") or "")
    if not group.get("summaryEn"):
        group["summaryEn"] = f"Usage contrast set: {group.get('title') or ''}."
    group["examples"] = [build_group_example(group, words_by_id)]
    group["status"] = "draft"
    group["reviewStatus"] = "ai_enriched_pending_human_review"
    group["quality"] = {
        "exampleType": "group_usage_contrast",
        "placeholderRemoved": True,
        "needsHumanReview": True,
    }
    group["updatedAt"] = None
    return group


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    words_by_id = {row["_id"]: row for row in words}
    relations = read_jsonl(RELATIONS_PATH)
    groups = read_jsonl(GROUPS_PATH)

    placeholders_removed = 0
    refined_relations = []
    for relation in relations:
        refined, removed = normalize_relation(relation, words_by_id)
        placeholders_removed += int(removed)
        refined_relations.append(refined)

    refined_groups = [normalize_group(group, words_by_id) for group in groups]

    write_jsonl(RELATIONS_PATH, refined_relations)
    write_jsonl(GROUPS_PATH, refined_groups)

    report = {
        "relations": len(refined_relations),
        "groups": len(refined_groups),
        "relationTypeCounts": Counter(row.get("relationType") for row in refined_relations),
        "relationStatusCounts": Counter(row.get("status") for row in refined_relations),
        "groupStatusCounts": Counter(row.get("status") for row in refined_groups),
        "placeholdersRemoved": placeholders_removed,
        "remainingDoNotMixExamples": sum(
            1 for row in refined_relations if str(row.get("exampleEn") or "").startswith("Do not mix them up")
        ),
        "remainingTruncatedZhExamples": sum(
            1 for row in refined_relations if "..." in str(row.get("exampleZh") or "") or "…" in str(row.get("exampleZh") or "")
        ),
        "reviewStatus": "ai_enriched_pending_human_review",
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
