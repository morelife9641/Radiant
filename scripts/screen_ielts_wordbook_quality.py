#!/usr/bin/env python3
"""Screen and safely refine the IELTS content wordbook.

This pass intentionally avoids aggressive semantic invention. It fixes obvious
data hygiene issues, fills low-risk display fields, and writes a compact report
for human review.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
SUGGESTIONS_PATH = DATA_DIR / "word_lexical_suggestions.json"
WORDBOOK_WORDS_PATH = DATA_DIR / "wordbook_words.json"
CONTENT_LINES_PATH = DATA_DIR / "content_lines.json"
REPORT_JSON_PATH = DATA_DIR / "ielts_wordbook_manual_screen_report.json"
REPORT_MD_PATH = DATA_DIR / "ielts_wordbook_manual_screen_report.md"


POS_PREFIX_RE = re.compile(r"^(?:n|v|vt|vi|a|adj|adv|prep|conj|pron|s|r)\.?\s+", re.I)
TEMPLATE_EXAMPLE_RE = re.compile(r"^(?:Compare |In context, )", re.I)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def compact_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\\n", "\n")).strip()


def first_sense(word_doc: dict[str, Any] | None) -> dict[str, Any]:
    if not word_doc:
        return {}
    senses = word_doc.get("senses") or []
    return senses[0] if senses else {}


def clean_short_definition(word_doc: dict[str, Any] | None) -> str:
    sense = first_sense(word_doc)
    raw_original = str(sense.get("definitionEn") or "")
    # Multi-line ECDICT/WordNet imports often start with obscure senses. For
    # example, tap may start with the metal plate used in tap dancing. Keep
    # this field for trusted editorial-style one-line definitions only.
    if "\\n" in raw_original or "\n" in raw_original:
        return ""
    if POS_PREFIX_RE.match(raw_original.strip()):
        return ""
    raw = raw_original.replace("\\n", "\n")
    if not raw.strip():
        return ""
    candidates: list[str] = []
    for part in re.split(r"[\n;]", raw):
        text = compact_text(part)
        text = POS_PREFIX_RE.sub("", text).strip(" .;:")
        if len(text.split()) >= 3 and not text.lower().startswith(("see ", "same as ")):
            candidates.append(text)
    if not candidates:
        return ""
    text = candidates[0]
    text = re.split(r"(?<=[.!?])\s+", text)[0].strip(" .;:")
    if len(text) > 150:
        text = text[:147].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    if text and text[-1] not in ".!?":
        text += "."
    return text[:1].upper() + text[1:] if text else ""


def dedupe_by_text(items: list[dict[str, Any]], key: str) -> tuple[list[dict[str, Any]], int]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    removed = 0
    for item in items:
        text = compact_text(item.get(key)).lower()
        if not text:
            removed += 1
            continue
        if text in seen:
            removed += 1
            continue
        seen.add(text)
        out.append(item)
    return out, removed


def score_collocation(item: dict[str, Any]) -> tuple[int, int, str]:
    text = compact_text(item.get("text") or item.get("pattern"))
    words = text.split()
    score = 0
    if item.get("translationZh"):
        score += 20
    if 2 <= len(words) <= 5:
        score += 8
    if re.search(r"\b(of|to|from|into|with|for|in|on|by)\b", text, re.I):
        score += 5
    if re.search(r"\bcan|should|may|likely|due to|lead to|result in|depend on|associated with\b", text, re.I):
        score += 4
    if len(words) > 8:
        score -= 10
    return (-score, len(words), text.lower())


def normalize_word(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    word_by_id = {row["_id"]: row for row in words}
    word_by_norm = {normalize_word(row.get("normalized") or row.get("word")): row for row in words}
    wordbook_rows = read_jsonl(WORDBOOK_WORDS_PATH)
    wordbook_norms = {normalize_word(row.get("normalized") or row.get("word")) for row in wordbook_rows}
    learning_rows = read_jsonl(LEARNING_PATH)
    suggestions = read_jsonl(SUGGESTIONS_PATH)
    content_lines = read_jsonl(CONTENT_LINES_PATH)

    stats: Counter[str] = Counter()
    samples: dict[str, list[Any]] = defaultdict(list)
    changed_learning = False
    changed_suggestions = False

    for row in learning_rows:
        word = normalize_word(row.get("normalized") or row.get("word"))
        word_doc = word_by_id.get(row.get("wordId")) or word_by_norm.get(word)

        current_short_status = str(row.get("shortDefinitionStatus") or "")
        if current_short_status == "auto_from_dictionary_pending_review":
            # Revoke the earlier broad auto-fill pass; it was too willing to
            # trust first dictionary senses for polysemous words.
            row.pop("shortDefinitionEn", None)
            row.pop("shortDefinitionStatus", None)
            stats["short_definitions_revoked_as_untrusted"] += 1
            changed_learning = True

        if not compact_text(row.get("shortDefinitionEn")):
            short_def = clean_short_definition(word_doc)
            if short_def:
                row["shortDefinitionEn"] = short_def
                row["shortDefinitionStatus"] = "trusted_editorial_definition_pending_review"
                stats["short_definitions_filled"] += 1
                changed_learning = True
                if len(samples["short_definitions_filled"]) < 12:
                    samples["short_definitions_filled"].append({"word": word, "shortDefinitionEn": short_def})
            else:
                stats["short_definitions_still_missing"] += 1

        morphology = row.get("morphology") or {}
        related = morphology.get("relatedWords") or []
        if related:
            kept = []
            for item in related:
                target = normalize_word(item.get("word"))
                if target and target == word:
                    stats["self_related_words_removed"] += 1
                    changed_learning = True
                    if len(samples["self_related_words_removed"]) < 12:
                        samples["self_related_words_removed"].append(word)
                    continue
                kept.append(item)
            if len(kept) != len(related):
                morphology["relatedWords"] = kept
                row["morphology"] = morphology

        collocations = row.get("collocations") or []
        if collocations:
            deduped, removed = dedupe_by_text(collocations, "text")
            if removed:
                stats["duplicate_or_empty_collocations_removed"] += removed
                changed_learning = True
            if len(deduped) > 5:
                deduped = sorted(deduped, key=score_collocation)
                removed_items = deduped[5:]
                row["collocations"] = deduped[:5]
                stats["collocations_trimmed_to_five"] += len(removed_items)
                changed_learning = True
                if len(samples["collocations_trimmed_words"]) < 12:
                    samples["collocations_trimmed_words"].append(word)
            elif len(deduped) != len(collocations):
                row["collocations"] = deduped

        grammar = row.get("grammarPatterns") or []
        if grammar:
            deduped_grammar, removed = dedupe_by_text(grammar, "pattern")
            if removed:
                row["grammarPatterns"] = deduped_grammar[:5]
                stats["duplicate_or_empty_grammar_removed"] += removed
                changed_learning = True

        if not (row.get("collocations") or []):
            stats["missing_collocations"] += 1
            if len(samples["missing_collocations"]) < 30:
                samples["missing_collocations"].append(word)
        if not ((row.get("morphology") or {}).get("segments") or []):
            stats["missing_morphology"] += 1

    kept_suggestions: list[dict[str, Any]] = []
    seen_suggestion_ids: set[str] = set()
    for row in suggestions:
        word = normalize_word(row.get("word"))
        target = normalize_word(row.get("targetWord"))
        row_id = str(row.get("_id") or "")
        if row_id and row_id in seen_suggestion_ids:
            stats["duplicate_suggestions_removed"] += 1
            changed_suggestions = True
            continue
        if row_id:
            seen_suggestion_ids.add(row_id)
        if target and target == word:
            stats["self_suggestions_removed"] += 1
            changed_suggestions = True
            if len(samples["self_suggestions_removed"]) < 12:
                samples["self_suggestions_removed"].append(word)
            continue

        example_en = compact_text(row.get("exampleEn"))
        if TEMPLATE_EXAMPLE_RE.search(example_en):
            row.setdefault("contentQuality", {})["exampleStatus"] = "template_needs_editorial_example"
            row["reviewStatus"] = "ai_suggested_pending_example_rewrite"
            stats["template_relation_examples_flagged"] += 1
            changed_suggestions = True
            if len(samples["template_relation_examples_flagged"]) < 12:
                samples["template_relation_examples_flagged"].append(
                    {"word": word, "targetWord": target, "relationType": row.get("relationType")}
                )

        if len(target.split()) > 3:
            row.setdefault("contentQuality", {})["targetStatus"] = "long_phrase_needs_review"
            stats["long_phrase_relation_targets_flagged"] += 1
            changed_suggestions = True

        kept_suggestions.append(row)

    relation_counts_by_word: dict[str, Counter[str]] = defaultdict(Counter)
    for row in kept_suggestions:
        relation_counts_by_word[normalize_word(row.get("word"))][str(row.get("relationType") or "")] += 1

    for wb in wordbook_rows:
        word = normalize_word(wb.get("normalized") or wb.get("word"))
        counts = relation_counts_by_word.get(word) or Counter()
        if not counts.get("near_synonym"):
            stats["missing_near_synonym_after_screen"] += 1
            if len(samples["missing_near_synonym_after_screen"]) < 30:
                samples["missing_near_synonym_after_screen"].append(word)
        if not counts.get("antonym"):
            stats["missing_antonym_after_screen"] += 1
            if len(samples["missing_antonym_after_screen"]) < 30:
                samples["missing_antonym_after_screen"].append(word)

    pending_translations = [
        row
        for row in content_lines
        if str(row.get("translationStatus") or row.get("reviewStatus") or "").lower()
        in {"pending_machine_translation", "pending_human_review", "draft"}
        or not compact_text(row.get("translationZh"))
    ]
    stats["content_lines_pending_translation_or_review"] = len(pending_translations)

    if changed_learning:
        write_jsonl(LEARNING_PATH, learning_rows)
    if changed_suggestions:
        write_jsonl(SUGGESTIONS_PATH, kept_suggestions)

    report = {
        "totalWords": len(wordbook_rows),
        "totalLearningRows": len(learning_rows),
        "totalLexicalSuggestions": len(kept_suggestions),
        "wordbookWordCount": len(wordbook_norms),
        "stats": dict(stats),
        "samples": dict(samples),
    }
    REPORT_JSON_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# IELTS 词库人工筛选报告",
        "",
        "本轮只做低风险清理：补展示短释、去自关联/重复项、标记模板关系例句、把搭配控制在 5 条以内。",
        "",
        "## 汇总",
        "",
        f"- 总词数：{len(wordbook_rows)}",
        f"- 学习内容条数：{len(learning_rows)}",
        f"- 词关系候选条数：{len(kept_suggestions)}",
        f"- 已补英文短释：{stats.get('short_definitions_filled', 0)}",
        f"- 仍缺英文短释：{stats.get('short_definitions_still_missing', 0)}",
        f"- 已移除自关联派生词：{stats.get('self_related_words_removed', 0)}",
        f"- 已移除自指向词关系：{stats.get('self_suggestions_removed', 0)}",
        f"- 已标记模板关系例句：{stats.get('template_relation_examples_flagged', 0)}",
        f"- 已裁剪超量搭配：{stats.get('collocations_trimmed_to_five', 0)}",
        f"- 待翻译/待审核原句：{stats.get('content_lines_pending_translation_or_review', 0)}",
        "",
        "## 仍建议人工看的项",
        "",
        f"- 缺近义/同类：{stats.get('missing_near_synonym_after_screen', 0)}",
        f"- 缺反义/对比：{stats.get('missing_antonym_after_screen', 0)}",
        f"- 缺搭配：{stats.get('missing_collocations', 0)}",
        "",
    ]

    for key, values in samples.items():
        if not values:
            continue
        md_lines.extend([f"## 样例：{key}", ""])
        for value in values[:30]:
            if isinstance(value, dict):
                md_lines.append("- `" + json.dumps(value, ensure_ascii=False) + "`")
            else:
                md_lines.append(f"- `{value}`")
        md_lines.append("")

    REPORT_MD_PATH.write_text("\n".join(md_lines), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
