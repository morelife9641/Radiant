#!/usr/bin/env python3
"""Build a local HTML inventory page for IELTS word content coverage."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
OUT_DIR = ROOT / "tmp/ielts_review_tool"
HTML_PATH = OUT_DIR / "ielts_word_inventory.html"
SUMMARY_PATH = OUT_DIR / "ielts_word_inventory_summary.json"
MIXED_POS_CANDIDATES_PATH = DATA_DIR / "remaining_mixed_pos_sense_candidates.json"
SEMANTIC_SENSE_MANUAL_REVIEW_PATH = DATA_DIR / "semantic_sense_manual_review.json"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def uniq(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        value = str(value or "").strip()
        if not value or value.lower() in seen:
            continue
        seen.add(value.lower())
        out.append(value)
    return out


def flatten_word_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(flatten_word_list(item))
        return out
    if isinstance(value, dict):
        for key in ("word", "text", "value", "normalized"):
            if value.get(key):
                return [str(value[key])]
        return []
    return [part.strip() for part in re.split(r"[,;/，；、\s]+", str(value)) if part.strip()]


def sense_values(word_doc: dict[str, Any] | None, key: str) -> list[str]:
    if not word_doc:
        return []
    values: list[str] = []
    for sense in word_doc.get("senses") or []:
        values.extend(flatten_word_list(sense.get(key)))
    return uniq(values)


def first_sense_text(word_doc: dict[str, Any] | None, key: str) -> str:
    if not word_doc:
        return ""
    for sense in word_doc.get("senses") or []:
        value = str(sense.get(key) or "").strip()
        if value:
            return re.sub(r"\s+", " ", value.replace("\\n", " "))
    return ""


def split_translation_by_pos(text: str) -> list[dict[str, str]]:
    text = re.sub(r"\s+", " ", str(text or "").replace("\\n", " ")).strip()
    if not text:
        return []
    # Some imported translations contain embedded pronunciation and another
    # POS block, e.g. "n. ... /səbˈdʒekt/ a. ...". Keep those visible.
    cleaned = re.sub(r"/[^/]+/", " ", text)
    matches = list(re.finditer(r"\b(n|v|vt|vi|a|adj|adv|prep|conj|pron)\.\s*", cleaned, flags=re.I))
    if not matches:
        return []
    out: list[dict[str, str]] = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
        pos = match.group(1).lower()
        if pos == "adj":
            pos = "a"
        body = cleaned[start:end].strip(" ;；")
        if body:
            out.append({"pos": pos, "translation": body})
    return out


def sense_entries(word_doc: dict[str, Any] | None) -> list[dict[str, str]]:
    if not word_doc:
        return []
    entries: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for sense in word_doc.get("senses") or []:
        pos = str(sense.get("pos") or "").strip()
        translation = re.sub(r"\s+", " ", str(sense.get("translation") or "").replace("\\n", " ")).strip()
        if not translation:
            continue
        key = (pos, translation)
        if key not in seen:
            seen.add(key)
            entries.append({
                "senseId": str(sense.get("senseId") or ""),
                "pos": pos,
                "translation": translation,
            })
    return entries


def sense_group_label(sense: dict[str, Any]) -> str:
    pos = str(sense.get("pos") or "?").strip()
    translation = re.sub(r"\s+", " ", str(sense.get("translation") or "").replace("\\n", " ")).strip()
    return f"{pos} · {translation}" if translation else pos


def normalize_pos_for_group(pos: str) -> str:
    value = str(pos or "").lower().strip().rstrip(".")
    if value in {"adj", "a"}:
        return "a"
    if value in {"vt", "vi"}:
        return "v"
    return value


COMMON_TARGET_POS = {
    "liable": "a",
    "likely": "a",
    "prone": "a",
    "apt": "a",
    "theme": "n",
    "topic": "n",
    "issue": "n",
    "object": "n",
    "subject": "n",
}


def unique_source_sense_for_pos(source_senses: list[dict[str, Any]], pos: str) -> str:
    wanted = normalize_pos_for_group(pos)
    matching = [
        sense
        for sense in source_senses
        if normalize_pos_for_group(str(sense.get("pos") or "")) == wanted
    ]
    if len(matching) == 1:
        return str(matching[0].get("senseId") or "")
    return ""


def hint_pos_from_suggestion_text(suggestion: dict[str, Any]) -> str:
    text = " ".join(
        str(suggestion.get(key) or "")
        for key in ("groupTitle", "groupSummaryZh", "explanationZh")
    )
    if any(term in text for term in ("主题", "话题", "题目", "主语", "宾语")):
        return "n"
    if any(term in text for term in ("倾向于", "易于", "容易", "易受", "受……")):
        return "a"
    return ""


def infer_specific_source_sense_id(suggestion: dict[str, Any], source_senses: list[dict[str, Any]]) -> str:
    source_word = str(suggestion.get("word") or "").lower()
    target_word = str(suggestion.get("targetWord") or "").lower()
    text = " ".join(
        str(suggestion.get(key) or "")
        for key in ("groupTitle", "groupSummaryZh", "explanationZh")
    )
    available = {str(sense.get("senseId") or "") for sense in source_senses}

    if source_word == "course":
        if target_word in {"class", "lesson", "lecture"} or any(term in text for term in ("课程", "课", "上课", "讲课")):
            return "course_n_study_01" if "course_n_study_01" in available else ""
        if target_word in {"route", "path", "way"} or any(term in text for term in ("路线", "航线", "路径", "方针")):
            return "course_n_route_01" if "course_n_route_01" in available else ""
        if target_word in {"process", "progress", "development"} or any(term in text for term in ("过程", "进程", "发展")):
            return "course_n_process_01" if "course_n_process_01" in available else ""
    return ""


def infer_suggestion_sense_id(
    suggestion: dict[str, Any],
    source_senses: list[dict[str, Any]],
    words_by_id: dict[str, dict[str, Any]],
) -> str:
    sense_ids = [str(sense.get("senseId") or "") for sense in source_senses if sense.get("senseId")]
    if len(sense_ids) == 1:
        return sense_ids[0]

    specific = infer_specific_source_sense_id(suggestion, source_senses)
    if specific:
        return specific

    target_doc = words_by_id.get(str(suggestion.get("targetWordId") or ""))
    target_poses = {
        normalize_pos_for_group(str(sense.get("pos") or ""))
        for sense in (target_doc or {}).get("senses") or []
        if sense.get("pos")
    }
    common_pos = COMMON_TARGET_POS.get(str(suggestion.get("targetWord") or "").lower())
    if common_pos:
        target_poses.add(common_pos)
    target_poses.discard("")
    if not target_poses:
        hinted = hint_pos_from_suggestion_text(suggestion)
        return unique_source_sense_for_pos(source_senses, hinted) if hinted else ""

    matching_source_senses = [
        sense
        for sense in source_senses
        if normalize_pos_for_group(str(sense.get("pos") or "")) in target_poses
    ]
    if len(matching_source_senses) == 1:
        return str(matching_source_senses[0].get("senseId") or "")
    hinted = hint_pos_from_suggestion_text(suggestion)
    if hinted:
        hinted_sense_id = unique_source_sense_for_pos(source_senses, hinted)
        if hinted_sense_id:
            return hinted_sense_id
    return ""


def morphology_kind(content: dict[str, Any] | None) -> str:
    if not content:
        return "missing"
    segments = ((content.get("morphology") or {}).get("segments") or [])
    types = {str(seg.get("type") or "").lower() for seg in segments}
    if any(t in types for t in ("prefix", "root", "suffix")):
        return "analyzed"
    if segments:
        return "base_only"
    return "missing"


def short_list(values: list[str], limit: int = 8) -> str:
    if not values:
        return ""
    shown = values[:limit]
    suffix = f" +{len(values) - limit}" if len(values) > limit else ""
    return ", ".join(shown) + suffix


def usage_score(text: str) -> tuple[int, int, str]:
    """Prefer reusable writing/speaking patterns over narrow reading-only phrases."""
    value = str(text or "").strip()
    lower = value.lower()
    score = 0
    academic_terms = [
        "access", "affect", "approach", "assess", "conduct", "consider",
        "data", "develop", "effect", "effective", "ensure", "evidence",
        "factor", "impact", "important", "increase", "issue", "method",
        "policy", "provide", "reduce", "research", "response", "risk",
        "significant", "strategy", "support", "to do", "whether",
    ]
    spoken_terms = [
        "deal with", "focus on", "in response to", "lead to", "look at",
        "point out", "refer to", "take advantage of", "tend to",
    ]
    narrow_terms = [
        "ant", "bark", "burrow", "cherry", "gland", "mite", "mosquito",
        "pine", "trunk", "zoological",
    ]
    if any(term in lower for term in academic_terms):
        score += 3
    if any(term in lower for term in spoken_terms):
        score += 2
    if " + " in value or " / " in value or "+ noun" in lower or "+ object" in lower or "+ clause" in lower:
        score += 2
    if len(value.split()) <= 5:
        score += 1
    if any(term in lower for term in narrow_terms):
        score -= 3
    return (-score, len(value), lower)


def usage_patterns_for_display(collocations: list[dict[str, Any]], grammar: list[dict[str, Any]]) -> list[str]:
    values = [
        item.get("text")
        for item in collocations
        if item.get("text")
    ] + [
        item.get("pattern")
        for item in grammar
        if item.get("pattern")
    ]
    return sorted(uniq([str(value) for value in values if value]), key=usage_score)[:5]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    wordbook_words = read_jsonl(DATA_DIR / "wordbook_words.json")
    learning_rows = read_jsonl(DATA_DIR / "word_learning_content.json")
    relations = read_jsonl(DATA_DIR / "word_relations.json")
    lexical_suggestions = read_jsonl(DATA_DIR / "word_lexical_suggestions.json") if (DATA_DIR / "word_lexical_suggestions.json").exists() else []
    line_words = read_jsonl(DATA_DIR / "content_line_words.json")
    lines = read_jsonl(DATA_DIR / "content_lines.json")
    topics = read_jsonl(DATA_DIR / "content_topics.json")
    words = read_jsonl(WORDS_PATH)
    mixed_pos_candidates = read_json(MIXED_POS_CANDIDATES_PATH, [])
    semantic_manual_review = read_json(SEMANTIC_SENSE_MANUAL_REVIEW_PATH, [])

    learning_by_id = {row["wordId"]: row for row in learning_rows}
    words_by_id = {row["_id"]: row for row in words}
    lines_by_id = {row["_id"]: row for row in lines}
    topics_by_id = {row["_id"]: row for row in topics}
    mixed_pos_by_word_id = {
        row["wordId"]: row
        for row in mixed_pos_candidates
        if isinstance(row, dict) and row.get("wordId")
    }
    semantic_manual_by_word_id = {
        row["wordId"]: row
        for row in semantic_manual_review
        if isinstance(row, dict) and row.get("wordId")
    }

    relation_out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    relation_in: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for relation in relations:
        relation_out[relation["fromWordId"]].append(relation)
        relation_in[relation["toWordId"]].append(relation)

    suggestions_by_word: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for suggestion in lexical_suggestions:
        suggestions_by_word[suggestion["wordId"]].append(suggestion)

    line_links: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for link in line_words:
        line_links[link["wordId"]].append(link)

    rows: list[dict[str, Any]] = []
    for wb in sorted(wordbook_words, key=lambda item: item.get("order") or 999999):
        word_id = wb["wordId"]
        word_doc = words_by_id.get(word_id)
        learning = learning_by_id.get(word_id)
        outgoing_rels = relation_out.get(word_id, [])
        incoming_rels = relation_in.get(word_id, [])
        rels = outgoing_rels + incoming_rels
        suggestions = suggestions_by_word.get(word_id, [])
        rel_by_type = defaultdict(list)
        for rel in outgoing_rels:
            rel_by_type[rel.get("relationType") or "unknown"].append(rel)
        incoming_by_type = defaultdict(list)
        for rel in incoming_rels:
            incoming_by_type[rel.get("relationType") or "unknown"].append(rel)

        word_senses = (word_doc or {}).get("senses") or []
        sense_entries_list = sense_entries(word_doc)
        sense_ids = [str(sense.get("senseId") or "") for sense in word_senses if sense.get("senseId")]
        first_sense_id = sense_ids[0] if sense_ids else ""
        sense_labels = {
            str(sense.get("senseId")): sense_group_label(sense)
            for sense in word_senses
            if sense.get("senseId")
        }

        dict_synonyms = sense_values(word_doc, "synonyms")
        dict_antonyms = sense_values(word_doc, "antonyms")
        relation_synonyms = uniq(
            [rel.get("toWord", "") for rel in rel_by_type.get("near_synonym", [])]
            + [rel.get("fromWord", "") for rel in incoming_by_type.get("near_synonym", [])]
        )
        synonym_items: list[dict[str, Any]] = []
        for sense in word_senses:
            sense_id = str(sense.get("senseId") or "")
            for value in flatten_word_list(sense.get("synonyms")):
                synonym_items.append({
                    "text": value,
                    "senseId": sense_id,
                    "sourceKind": "dictionary",
                    "sourceLabel": "词典",
                    "deletable": True,
                })
        for rel in rel_by_type.get("near_synonym", []):
            if rel.get("toWord"):
                scope = rel.get("senseScope") or {}
                synonym_items.append({
                    "text": rel.get("toWord"),
                    "senseId": scope.get("fromSenseId") or "",
                    "targetSenseId": scope.get("toSenseId") or "",
                    "sourceKind": "word_relations",
                    "sourceLabel": "关系",
                    "sourceId": rel.get("_id"),
                    "deletable": True,
                })
        for rel in incoming_by_type.get("near_synonym", []):
            if rel.get("fromWord"):
                scope = rel.get("senseScope") or {}
                synonym_items.append({
                    "text": rel.get("fromWord"),
                    "senseId": scope.get("toSenseId") or "",
                    "targetSenseId": scope.get("fromSenseId") or "",
                    "sourceKind": "word_relations",
                    "sourceLabel": "关系",
                    "sourceId": rel.get("_id"),
                    "deletable": True,
                })
        for rel in rel_by_type.get("confusing", []):
            if rel.get("toWord"):
                scope = rel.get("senseScope") or {}
                synonym_items.append({
                    "text": rel.get("toWord"),
                    "senseId": scope.get("fromSenseId") or "",
                    "targetSenseId": scope.get("toSenseId") or "",
                    "sourceKind": "word_relations",
                    "sourceLabel": "语义辨析",
                    "sourceId": rel.get("_id"),
                    "deletable": True,
                })
        for rel in incoming_by_type.get("confusing", []):
            if rel.get("fromWord"):
                scope = rel.get("senseScope") or {}
                synonym_items.append({
                    "text": rel.get("fromWord"),
                    "senseId": scope.get("toSenseId") or "",
                    "targetSenseId": scope.get("fromSenseId") or "",
                    "sourceKind": "word_relations",
                    "sourceLabel": "语义辨析",
                    "sourceId": rel.get("_id"),
                    "deletable": True,
                })
        for item in suggestions:
            if item.get("relationType") == "near_synonym" and item.get("targetWord"):
                suggestion_scope = item.get("senseScope") if isinstance(item.get("senseScope"), dict) else {}
                synonym_items.append({
                    "text": item.get("targetWord"),
                    "senseId": suggestion_scope.get("fromSenseId") or infer_suggestion_sense_id(item, word_senses, words_by_id),
                    "sourceKind": "word_lexical_suggestions",
                    "sourceLabel": "候选",
                    "sourceId": item.get("_id"),
                    "deletable": True,
                })
        synonym_items = [
            item for item in {
                f"{item.get('senseId') or '__unbound__'}:{str(item.get('text', '')).lower()}": item
                for item in synonym_items
                if item.get("text")
            }.values()
        ]
        synonym_groups_by_key: dict[str, dict[str, Any]] = {}
        for sense_id in sense_ids:
            synonym_groups_by_key[sense_id] = {
                "senseId": sense_id,
                "label": sense_labels.get(sense_id) or sense_id,
                "items": [],
            }
        synonym_groups_by_key["__unbound__"] = {
            "senseId": "",
            "label": "未绑定词义候选",
            "items": [],
        }
        for item in synonym_items:
            key = str(item.get("senseId") or "")
            if key not in synonym_groups_by_key:
                key = "__unbound__"
            synonym_groups_by_key[key]["items"].append(item)
        synonym_groups = [
            group
            for key, group in synonym_groups_by_key.items()
            if group["items"] or key != "__unbound__"
        ]
        relation_antonyms = uniq(
            [rel.get("toWord", "") for rel in rel_by_type.get("antonym", [])]
            + [rel.get("fromWord", "") for rel in incoming_by_type.get("antonym", [])]
        )
        lexical_synonyms = uniq([item.get("targetWord", "") for item in suggestions if item.get("relationType") == "near_synonym"])
        lexical_antonyms = uniq([item.get("targetWord", "") for item in suggestions if item.get("relationType") == "antonym"])
        lexical_contrasts = uniq([
            item.get("targetWord", "")
            for item in suggestions
            if item.get("relationType") in {"contrast", "context_contrast"}
        ])
        semantic_near = uniq(
            [rel.get("toWord", "") for rel in rel_by_type.get("confusing", [])]
            + [rel.get("fromWord", "") for rel in incoming_by_type.get("confusing", [])]
        )
        spelling_confusables = uniq([
            item.get("targetWord", "")
            for item in suggestions
            if item.get("relationType") == "spelling_confusable"
        ])

        links = line_links.get(word_id, [])
        primary_line_id = (learning or {}).get("primaryLineId") or (wb.get("sourceStats") or {}).get("primaryLineId")
        primary_line = lines_by_id.get(primary_line_id) if primary_line_id else None
        source_stats = wb.get("sourceStats") or {}
        source_topic_ids = source_stats.get("topicIds") if isinstance(source_stats.get("topicIds"), list) else []
        first_topic_id = source_stats.get("firstTopicId") or ""
        has_newdocs_source = (
            str(first_topic_id).startswith("ielts-reading-newdocs-")
            or any(str(topic_id).startswith("ielts-reading-newdocs-") for topic_id in source_topic_ids)
        )
        is_newdocs_word = (wb.get("order") or 0) > 1352
        article_titles = uniq([
            lines_by_id.get(link.get("lineId"), {}).get("articleTitle")
            or topics_by_id.get(link.get("topicId"), {}).get("name")
            or ""
            for link in links
        ])

        morphology = (learning or {}).get("morphology") or {}
        collocations = (learning or {}).get("collocations") or []
        grammar = (learning or {}).get("grammarPatterns") or []
        common_errors = (learning or {}).get("commonErrors") or []
        related_words = morphology.get("relatedWords") or []
        morph_kind = morphology_kind(learning)
        mixed_pos_candidate = mixed_pos_by_word_id.get(word_id)
        semantic_manual_item = semantic_manual_by_word_id.get(word_id)

        missing = {
            "dictSynonyms": not dict_synonyms,
            "dictAntonyms": not dict_antonyms,
            "relationSynonyms": not relation_synonyms,
            "relationAntonyms": not relation_antonyms,
            "anySynonyms": not (dict_synonyms or relation_synonyms or lexical_synonyms or semantic_near),
            "anyAntonyms": not (dict_antonyms or relation_antonyms or lexical_antonyms),
            "relations": not (rels or suggestions),
            "collocations": not (collocations or grammar),
            "morphologyAnalysis": morph_kind != "analyzed",
            "grammarPatterns": not grammar,
            "commonErrors": not common_errors,
            "relatedWords": not related_words,
            "primaryLine": not primary_line,
            "mixedPosSenseCandidate": bool(mixed_pos_candidate),
            "needsHumanSenseReview": bool(semantic_manual_item),
        }

        row = {
            "order": wb.get("order"),
            "wordId": word_id,
            "word": wb.get("word"),
            "chapter": wb.get("chapter"),
            "sourceBatch": "newdocs" if is_newdocs_word else "initial_pdf",
            "isNewdocsWord": is_newdocs_word,
            "hasNewdocsSource": has_newdocs_source,
            "important": bool(wb.get("important")),
            "occurrenceCount": source_stats.get("occurrenceCount") or 0,
            "articleCount": source_stats.get("articleCount") or 0,
            "phonetic": ((word_doc or {}).get("phonetic") or {}).get("default")
            or ((word_doc or {}).get("phonetic") or {}).get("uk")
            or ((word_doc or {}).get("phonetic") or {}).get("us")
            or "",
            "translation": first_sense_text(word_doc, "translation"),
            "definitionEn": first_sense_text(word_doc, "definitionEn"),
            "shortDefinitionEn": (learning or {}).get("shortDefinitionEn") or "",
            "shortDefinitionZh": (learning or {}).get("shortDefinitionZh") or "",
            "shortDefinitionStatus": (learning or {}).get("shortDefinitionStatus") or "",
            "shortDefinitionReview": (learning or {}).get("shortDefinitionReview") or {},
            "senses": sense_entries_list,
            "mixedPosSenseCandidate": mixed_pos_candidate,
            "semanticManualReview": semantic_manual_item,
            "dictSynonyms": dict_synonyms,
            "synonymItems": synonym_items,
            "synonymGroups": synonym_groups,
            "dictAntonyms": dict_antonyms,
            "relationSynonyms": relation_synonyms,
            "lexicalSynonyms": lexical_synonyms,
            "semanticNear": semantic_near,
            "relationAntonyms": relation_antonyms,
            "lexicalAntonyms": lexical_antonyms,
            "lexicalContrasts": lexical_contrasts,
            "spellingConfusables": spelling_confusables,
            "relationCount": len(rels),
            "suggestionCount": len(suggestions),
            "relationStatus": Counter(rel.get("status") for rel in rels),
            "suggestionStatus": Counter(item.get("status") for item in suggestions),
            "collocationCount": len(collocations),
            "collocations": [item.get("text") for item in collocations if item.get("text")],
            "morphologyKind": morph_kind,
            "morphologySegments": [
                (
                    f"{seg.get('form')}({seg.get('type')})"
                    + (f": {seg.get('meaningZh')}" if seg.get("meaningZh") else "")
                )
                for seg in morphology.get("segments") or []
                if seg.get("form")
            ],
            "relatedWordCount": len(related_words),
            "relatedWords": [item.get("word") for item in related_words if item.get("word")],
            "grammarCount": len(grammar),
            "grammarPatterns": [item.get("pattern") for item in grammar if item.get("pattern")],
            "usagePatterns": usage_patterns_for_display(collocations, grammar),
            "commonErrorCount": len(common_errors),
            "commonErrors": [item.get("wrong") for item in common_errors if item.get("wrong")],
            "lexicalSuggestions": suggestions,
            "learningStatus": (learning or {}).get("status") or "",
            "reviewStatus": ((learning or {}).get("provenance") or {}).get("reviewStatus") or "",
            "articleTitles": article_titles,
            "primaryLineId": primary_line_id or "",
            "primaryLineText": (primary_line or {}).get("text") or "",
            "primaryLineZh": (primary_line or {}).get("translationZh") or "",
            "missing": missing,
        }
        rows.append(row)

    summary = {
        "totalWords": len(rows),
        "missingAnySynonyms": sum(row["missing"]["anySynonyms"] for row in rows),
        "missingAnyAntonyms": sum(row["missing"]["anyAntonyms"] for row in rows),
        "missingRelations": sum(row["missing"]["relations"] for row in rows),
        "missingCollocations": sum(row["missing"]["collocations"] for row in rows),
        "missingMorphologyAnalysis": sum(row["missing"]["morphologyAnalysis"] for row in rows),
        "missingGrammarPatterns": sum(row["missing"]["grammarPatterns"] for row in rows),
        "missingCommonErrors": sum(row["missing"]["commonErrors"] for row in rows),
        "mixedPosSenseCandidates": sum(row["missing"]["mixedPosSenseCandidate"] for row in rows),
        "needsHumanSenseReview": sum(row["missing"]["needsHumanSenseReview"] for row in rows),
        "newdocsWords": sum(bool(row["isNewdocsWord"]) for row in rows),
        "autoEnglishShortDefinitions": sum(
            row.get("shortDefinitionStatus") == "auto_from_english_definition_pending_review"
            for row in rows
        ),
        "morphologyKinds": Counter(row["morphologyKind"] for row in rows),
        "relationStatus": Counter(row.get("status") for row in relations),
        "lexicalSuggestions": len(lexical_suggestions),
    }

    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=dict), encoding="utf-8")
    embedded_rows = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    embedded_summary = json.dumps(summary, ensure_ascii=False, default=dict).replace("<", "\\u003c")

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>IELTS 词书内容覆盖体检表</title>
  <style>
    :root {{ --brand:#234E52; --ink:#17252a; --muted:#64748b; --line:#dbe3ea; --soft:#f6f8fb; --bad:#fff1f2; --warn:#fff7ed; --ok:#ecfdf5; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:var(--ink); background:#f3f6f8; }}
    header {{ position:sticky; top:0; z-index:10; background:linear-gradient(135deg,#234E52,#173A3F); color:white; padding:18px 24px; box-shadow:0 6px 20px rgba(15,23,42,.16); }}
    h1 {{ margin:0 0 10px; font-size:22px; }}
    .toolbar {{ display:flex; gap:10px; flex-wrap:wrap; align-items:center; }}
    input, select, button, textarea {{ font:inherit; border-radius:10px; border:1px solid rgba(255,255,255,.32); padding:9px 10px; }}
    button {{ cursor:pointer; border:0; background:#e6fffa; color:#134e4a; font-weight:700; }}
    button.secondary {{ background:#e2e8f0; color:#0f172a; }}
    main {{ padding:18px 24px 42px; }}
    .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(145px,1fr)); gap:12px; margin-bottom:14px; }}
    .stat {{ background:white; border:1px solid var(--line); border-radius:14px; padding:12px 14px; box-shadow:0 1px 5px rgba(15,23,42,.05); }}
    .stat.clickable {{ cursor:pointer; transition:transform .12s ease, border-color .12s ease; }}
    .stat.clickable:hover {{ transform:translateY(-1px); border-color:#0f766e; }}
    .stat.active {{ outline:2px solid #0f766e; }}
    .stat b {{ display:block; font-size:24px; margin-top:4px; }}
    .filters {{ display:flex; gap:8px; flex-wrap:wrap; margin:12px 0 16px; }}
    .chip {{ border:1px solid var(--line); background:white; color:#334155; padding:8px 10px; border-radius:999px; cursor:pointer; }}
    .chip.active {{ background:#234E52; color:white; border-color:#234E52; }}
    .table-wrap {{ background:white; border:1px solid var(--line); border-radius:16px; overflow:auto; max-height:72vh; box-shadow:0 2px 8px rgba(15,23,42,.05); }}
    table {{ width:100%; border-collapse:separate; border-spacing:0; min-width:2100px; table-layout:fixed; }}
    th, td {{ border-right:1px solid #e5e7eb; border-bottom:1px solid #e5e7eb; padding:10px 11px; vertical-align:top; font-size:13px; }}
    th:last-child, td:last-child {{ border-right:0; }}
    thead th {{ position:sticky; top:0; z-index:3; background:#f8fafc; text-align:left; color:#334155; box-shadow:0 1px 0 #e5e7eb; }}
    tr:hover td {{ background:#f8fafc; }}
    .word {{ font-weight:800; font-size:15px; }}
    .muted {{ color:var(--muted); font-size:12px; }}
    .badge {{ display:inline-flex; align-items:center; max-width:100%; min-height:20px; padding:2px 8px; border-radius:999px; background:#e2e8f0; color:#334155; margin:2px 4px 2px 0; white-space:normal; overflow-wrap:anywhere; word-break:break-word; line-height:1.3; vertical-align:top; }}
    .badge.missing {{ background:#ffe4e6; color:#9f1239; }}
    .badge.ok {{ background:#dcfce7; color:#166534; }}
    .badge.draft {{ background:#fef3c7; color:#92400e; }}
    .badge.warn {{ background:#fed7aa; color:#9a3412; }}
    .badge.count {{ display:inline-flex; margin-bottom:5px; font-weight:700; }}
    .badge.deletable {{ gap:5px; padding-right:4px; }}
    .delete-badge {{ display:inline-flex; align-items:center; justify-content:center; width:16px; height:16px; border-radius:999px; border:0; padding:0; margin-left:2px; background:#bbf7d0; color:#166534; font-size:12px; line-height:1; font-weight:900; cursor:pointer; }}
    .delete-badge:hover {{ background:#fecaca; color:#991b1b; }}
    .sense-relation-group {{ margin:0 0 8px; padding:7px 8px; border:1px solid #e2e8f0; border-radius:12px; background:#fff; }}
    .sense-relation-title {{ display:flex; align-items:center; gap:6px; margin-bottom:5px; color:#334155; font-weight:800; font-size:12px; }}
    .sense-relation-title .pos {{ min-width:auto; margin-right:0; }}
    .sense-relation-group.unbound {{ background:#fff7ed; border-color:#fed7aa; }}
    .relation-item {{ display:flex; gap:6px; flex-wrap:wrap; align-items:center; margin:3px 0; }}
    .bind-controls {{ display:inline-flex; gap:5px; align-items:center; flex-wrap:wrap; }}
    .bind-controls select {{ max-width:180px; padding:4px 6px; border:1px solid #fdba74; background:#fff; color:#7c2d12; border-radius:8px; font-size:12px; }}
    .bind-sense-btn {{ padding:4px 7px; border-radius:8px; background:#ffedd5; color:#9a3412; font-size:12px; }}
    .bind-sense-btn.reject {{ background:#ffe4e6; color:#9f1239; }}
    .bulk-bind {{ display:flex; gap:6px; flex-wrap:wrap; align-items:center; margin:4px 0 7px; padding:6px; border-radius:10px; background:#fff; border:1px dashed #fdba74; }}
    .bulk-bind select {{ max-width:210px; padding:5px 7px; border:1px solid #fdba74; background:#fff; color:#7c2d12; border-radius:8px; font-size:12px; }}
    .num {{ text-align:right; font-variant-numeric:tabular-nums; }}
    details {{ max-width:100%; }}
    summary {{ cursor:pointer; color:#0f766e; font-weight:700; }}
    .detail {{ margin-top:8px; padding:10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; line-height:1.55; }}
    .mini-list {{ max-height:94px; overflow:hidden; }}
    .mini-list.expanded {{ max-height:none; }}
    .usage-list {{ max-height:none; overflow:visible; display:block; }}
    .usage-cell {{ background:#fcfffd; }}
    .usage-cell .badge.ok {{ display:flex; width:max-content; max-width:100%; margin-bottom:4px; border-radius:9px; }}
    .show-more {{ display:inline-block; margin-top:4px; color:#0f766e; cursor:pointer; font-weight:700; font-size:12px; }}
    .sense {{ display:block; margin:2px 0; line-height:1.45; }}
    .pos {{ display:inline-block; min-width:28px; padding:1px 6px; border-radius:6px; background:#dbeafe; color:#1e40af; font-weight:800; text-align:center; margin-right:4px; }}
    textarea.editbox {{ width:100%; min-height:62px; border:1px solid #cbd5e1; background:#fff; color:#0f172a; margin:4px 0 8px; line-height:1.45; resize:vertical; }}
    .edit-panel {{ margin-top:8px; padding:10px; border:1px dashed #94a3b8; background:#fff; border-radius:12px; }}
    .edit-only {{ display:none; }}
    body.editing .edit-only {{ display:block; }}
    .cell-edit {{ display:none; margin-top:8px; }}
    body.editing .cell-edit {{ display:block; }}
    .quick-cell-edit {{ display:block; margin-top:8px; }}
    .edit-toggle {{ margin-top:6px; padding:4px 8px; border-radius:8px; background:#e0f2fe; color:#075985; font-size:12px; }}
    .cell-editor {{ display:none; margin-top:6px; }}
    .cell-editor.open {{ display:block; }}
    .mark-tools {{ display:flex; gap:6px; flex-wrap:wrap; margin:7px 0 4px; }}
    .mark-btn {{ padding:4px 8px; border-radius:999px; background:#f1f5f9; color:#334155; border:1px solid #cbd5e1; font-size:12px; }}
    .mark-btn.marked {{ background:#fde68a; color:#78350f; border-color:#f59e0b; }}
    .mark-summary {{ display:inline-flex; gap:6px; align-items:center; padding:7px 10px; border-radius:999px; background:rgba(255,255,255,.14); color:#fff; font-weight:700; }}
    .sense-review-tools {{ display:flex; gap:6px; flex-wrap:wrap; margin:6px 0; }}
    .sense-review-btn {{ padding:4px 8px; border-radius:999px; background:#fff7ed; color:#9a3412; border:1px solid #fdba74; font-size:12px; }}
    .sense-review-btn.selected {{ background:#fb923c; color:#fff; border-color:#ea580c; }}
    .short-review-tools {{ display:flex; gap:6px; flex-wrap:wrap; align-items:center; margin-top:8px; }}
    .short-review-btn {{ padding:4px 8px; border-radius:999px; background:#f1f5f9; color:#334155; border:1px solid #cbd5e1; font-size:12px; }}
    .short-review-btn.approve.selected {{ background:#16a34a; color:#fff; border-color:#15803d; }}
    .short-review-btn.reject.selected {{ background:#e11d48; color:#fff; border-color:#be123c; }}
    .short-review-status {{ margin-top:5px; font-size:12px; color:#64748b; }}
    .missing-cell {{ background:#fff1f2; }}
    .soft {{ color:#475569; }}
  </style>
</head>
<body>
  <header>
    <h1>IELTS 词书内容覆盖体检表</h1>
    <div class="toolbar">
      <input id="search" placeholder="搜索单词 / 中文 / 文章 / 原句" size="36" />
      <select id="chapter"><option value="">全部文章</option></select>
      <select id="status"><option value="">全部学习状态</option></select>
      <button id="toggleEdit">开启编辑</button>
      <button id="submitMarks">提交标记</button>
      <button id="clearMarks" class="secondary">清空标记</button>
      <button id="submitSenseDecisions">提交拆义选择</button>
      <button id="clearSenseDecisions" class="secondary">清空拆义选择</button>
      <button id="submitShortDefinitionReviews">提交短释审核</button>
      <button id="clearShortDefinitionReviews" class="secondary">清空短释审核</button>
      <button id="exportRelationSenseDecisions">导出词义绑定</button>
      <button id="clearRelationSenseDecisions" class="secondary">清空绑定</button>
      <button id="exportPatch">导出修改 JSON</button>
      <button id="exportCsv">导出当前筛选 CSV</button>
      <button id="reset" class="secondary">重置筛选</button>
      <span id="markSummary" class="mark-summary">已标记 0</span>
    </div>
  </header>
  <main>
    <section class="stats" id="stats"></section>
    <section class="filters" id="chips"></section>
    <div class="muted" id="countLabel"></div>
    <section class="table-wrap">
      <table>
        <colgroup>
          <col style="width:48px" />
          <col style="width:140px" />
          <col style="width:260px" />
          <col style="width:220px" />
          <col style="width:150px" />
          <col style="width:260px" />
          <col style="width:210px" />
          <col style="width:280px" />
          <col style="width:220px" />
          <col style="width:180px" />
          <col style="width:180px" />
          <col style="width:300px" />
          <col style="width:150px" />
        </colgroup>
        <thead>
          <tr>
            <th>#</th><th>单词</th><th>释义/音标</th><th>英文短释</th><th>文章</th><th>近义/同类/语义辨析</th><th>反义/对比</th><th>形近易混</th>
            <th>搭配/句型</th><th>构词</th><th>派生/相关词</th><th>原句</th><th>状态</th>
          </tr>
        </thead>
        <tbody id="tbody"></tbody>
      </table>
    </section>
  </main>
  <script>
    const rows = {embedded_rows};
    const summary = {embedded_summary};
    const editStorageKey = 'ielts_word_inventory_edits_v1';
    const markStorageKey = 'ielts_word_inventory_relation_marks_v1';
    const senseDecisionStorageKey = 'ielts_word_inventory_sense_decisions_v1';
    const relationSenseDecisionStorageKey = 'ielts_relation_sense_decisions_v1';
    const shortDefinitionReviewStorageKey = 'ielts_short_definition_reviews_v1';
    let editMode = false;
    let edits = JSON.parse(localStorage.getItem(editStorageKey) || '{{}}');
    let marks = JSON.parse(localStorage.getItem(markStorageKey) || '{{}}');
    let senseDecisions = JSON.parse(localStorage.getItem(senseDecisionStorageKey) || '{{}}');
    let relationSenseDecisions = JSON.parse(localStorage.getItem(relationSenseDecisionStorageKey) || '{{}}');
    let shortDefinitionReviews = JSON.parse(localStorage.getItem(shortDefinitionReviewStorageKey) || '{{}}');
    const active = new Set();
    const searchEl = document.getElementById('search');
    const chapterEl = document.getElementById('chapter');
    const statusEl = document.getElementById('status');
    const tbody = document.getElementById('tbody');
    const chipsEl = document.getElementById('chips');
    const countLabel = document.getElementById('countLabel');

    const chipDefs = [
      ['newdocsWords', 'newdocs 新词'],
      ['autoEnglishShortDefinitions', '自动英文短释待审'],
      ['anySynonyms', '缺近义/同义'],
      ['anyAntonyms', '缺反义词'],
      ['relations', '无词关系'],
      ['collocations', '无搭配/句型'],
      ['morphologyAnalysis', '无构词拆解'],
      ['relatedWords', '无派生/相关词'],
      ['unboundRelationCandidates', '未绑定待处理'],
      ['mixedPosSenseCandidate', '疑似多词性待拆'],
      ['needsHumanSenseReview', '需人工拆义确认'],
      ['primaryLine', '无主例句']
    ];

    function esc(value) {{
      return String(value ?? '').replace(/[&<>"]/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[ch]));
    }}
    function splitEditList(value) {{
      return String(value || '').split(/[,，;；\\n]/).map(x => x.trim()).filter(Boolean);
    }}
    function displayTerm(value) {{
      return String(value || '').replace(/ \\((edited|suggested|relation|semantic|contrast)\\)$/,'');
    }}
    function mergedList(row, baseValues, field) {{
      const extra = splitEditList((edits[row.wordId] || {{}})[field]);
      const seen = new Set();
      return [...(baseValues || []), ...extra.map(x => x + ' (edited)')].filter(v => {{
        const key = displayTerm(v).toLowerCase();
        if (!key || seen.has(key)) return false;
        seen.add(key);
        return true;
      }});
    }}
    function list(values, missingText='空', limit=10, className='') {{
      if (!values || !values.length) return `<span class="badge missing">${{missingText}}</span>`;
      const id = 'list_' + Math.random().toString(36).slice(2);
      const body = values.map(v => `<span class="badge ok" title="${{esc(v)}}">${{esc(displayTerm(v))}}</span>`).join('');
      const more = values.length > limit ? `<span class="show-more" data-target="${{id}}">展开全部 ${{values.length}}</span>` : '';
      return `<div id="${{id}}" class="mini-list ${{className}}">${{body}}</div>${{more}}`;
    }}
    function synonymBadgeList(row, items, missingText='无近义/同义') {{
      const editExtras = splitEditList((edits[row.wordId] || {{}}).synonyms).map(text => ({{
        text,
        sourceKind: 'local_edit',
        sourceLabel: '本地编辑',
        deletable: false
      }}));
      const all = [...(items || []), ...editExtras];
      const seen = new Set();
      const unique = all.filter(item => {{
        const key = displayTerm(item.text).toLowerCase();
        if (!key || seen.has(key)) return false;
        seen.add(key);
        return true;
      }});
      if (!unique.length) return `<span class="badge missing">${{missingText}}</span>`;
      const body = unique.map(item => {{
        const title = item.sourceLabel || item.sourceKind || '来源';
        const deleteButton = item.deletable ? `<button class="delete-badge" title="删除该近义/同类词" data-word-id="${{esc(row.wordId)}}" data-word="${{esc(row.word)}}" data-target-word="${{esc(item.text)}}" data-source-kind="${{esc(item.sourceKind || '')}}" data-source-id="${{esc(item.sourceId || '')}}">×</button>` : '';
        return `<span class="badge ok deletable" title="${{esc(title)}}"><span>${{esc(displayTerm(item.text))}}</span>${{deleteButton}}</span>`;
      }}).join('');
      return `<div class="mini-list">${{body}}</div>`;
    }}
    function senseOptions(row, selected='') {{
      return (row.senses || []).map(s => {{
        const label = `${{s.pos || '?'}} · ${{s.translation || s.senseId || ''}}`;
        const value = s.senseId || '';
        return `<option value="${{esc(value)}}" ${{value === selected ? 'selected' : ''}}>${{esc(label)}}</option>`;
      }}).join('');
    }}
    function relationDecisionKey(row, item) {{
      return `${{row.wordId}}::${{item.sourceKind || ''}}::${{item.sourceId || ''}}::${{item.text || ''}}`;
    }}
    function unboundItems(row) {{
      return (row.synonymGroups || [])
        .filter(group => !group.senseId)
        .flatMap(group => group.items || []);
    }}
    function unresolvedUnboundItems(row) {{
      return unboundItems(row).filter(item => !relationSenseDecisions[relationDecisionKey(row, item)]);
    }}
    function hasUnresolvedUnbound(row) {{
      return unresolvedUnboundItems(row).length > 0;
    }}
    function synonymGroupsHtml(row, groups, missingText='无近义/同义') {{
      const editExtras = splitEditList((edits[row.wordId] || {{}}).synonyms).map(text => ({{
        text,
        sourceKind: 'local_edit',
        sourceLabel: '本地编辑',
        deletable: false
      }}));
      const sourceGroups = (groups || []).map(group => ({{
        ...group,
        items: [...(group.items || [])]
      }}));
      if (editExtras.length) {{
        let unbound = sourceGroups.find(group => !group.senseId);
        if (!unbound) {{
          unbound = {{ senseId: '', label: '未绑定词义候选', items: [] }};
          sourceGroups.push(unbound);
        }}
        unbound.items.push(...editExtras);
      }}
      const visibleGroups = sourceGroups.map(group => {{
        const seen = new Set();
        const unique = (group.items || []).filter(item => {{
          const key = displayTerm(item.text).toLowerCase();
          if (!key || seen.has(key)) return false;
          seen.add(key);
          return true;
        }});
        return {{ ...group, items: unique }};
      }}).filter(group => group.items.length);
      if (!visibleGroups.length) return `<span class="badge missing">${{missingText}}</span>`;
      return visibleGroups.map(group => {{
        const titleParts = String(group.label || '未绑定词义候选').split(' · ');
        const pos = titleParts.length > 1 ? titleParts[0] : '';
        const label = titleParts.length > 1 ? titleParts.slice(1).join(' · ') : titleParts[0];
        const title = group.senseId
          ? `<div class="sense-relation-title"><span class="pos">${{esc(pos || '?')}}</span><span>${{esc(label)}}</span></div>`
          : `<div class="sense-relation-title"><span class="badge warn">未绑定词义候选</span></div>`;
        const groupKey = `${{row.wordId}}::unbound::${{Math.random().toString(36).slice(2)}}`;
        const bulkControls = !group.senseId ? `<div class="bulk-bind">
            <span class="muted">先逐条选择，再提交整组</span>
            <button class="bulk-bind-btn" data-group-key="${{esc(groupKey)}}" data-action="submit_group">提交本组选择</button>
          </div>` : '';
        const body = group.items.map(item => {{
          const sourceTitle = item.sourceLabel || item.sourceKind || '来源';
          const targetSense = item.targetSenseId ? ` / target: ${{item.targetSenseId}}` : '';
          const deleteButton = item.deletable ? `<button class="delete-badge" title="删除该近义/同类词" data-word-id="${{esc(row.wordId)}}" data-word="${{esc(row.word)}}" data-target-word="${{esc(item.text)}}" data-source-kind="${{esc(item.sourceKind || '')}}" data-source-id="${{esc(item.sourceId || '')}}">×</button>` : '';
          const key = relationDecisionKey(row, item);
          const decision = relationSenseDecisions[key] || {{}};
          const bindControls = !group.senseId ? `<span class="bind-controls" data-group-key="${{esc(groupKey)}}">
              <select class="bind-sense-select" data-group-key="${{esc(groupKey)}}" data-decision-key="${{esc(key)}}" data-word-id="${{esc(row.wordId)}}" data-word="${{esc(row.word)}}" data-target-word="${{esc(item.text)}}" data-source-kind="${{esc(item.sourceKind || '')}}" data-source-id="${{esc(item.sourceId || '')}}">
                <option value="">选择词义/不合适</option>${{senseOptions(row, decision.senseId || '')}}<option value="__reject__" ${{decision.action === 'reject' ? 'selected' : ''}}>不合适</option>
              </select>
            </span>` : '';
          const chosen = decision.action === 'bind'
            ? `<span class="badge draft">已选：${{esc(decision.senseLabel || decision.senseId || '')}}</span>`
            : (decision.action === 'reject' ? `<span class="badge missing">已标不合适</span>` : '');
          return `<div class="relation-item"><span class="badge ok deletable" title="${{esc(sourceTitle + targetSense)}}"><span>${{esc(displayTerm(item.text))}}</span>${{deleteButton}}</span>${{chosen}}${{bindControls}}</div>`;
        }}).join('');
        return `<div class="sense-relation-group ${{group.senseId ? '' : 'unbound'}}">${{title}}${{bulkControls}}<div>${{body}}</div></div>`;
      }}).join('');
    }}
    function countBadge(count, label) {{
      return count ? `<span class="badge ok count">${{count}} ${{label}}</span>` : `<span class="badge missing count">0 ${{label}}</span>`;
    }}

    async function deleteSynonymBadge(button) {{
      const word = button.dataset.word || '';
      const wordId = button.dataset.wordId || '';
      const targetWord = button.dataset.targetWord || '';
      if (!wordId || !targetWord) return;
      const ok = confirm(`确定删除「${{word}}」的近义/同类词「${{targetWord}}」吗？\\n\\n会同步删除数据源里的相关候选/关系，并重建页面。`);
      if (!ok) return;
      button.disabled = true;
      button.textContent = '…';
      try {{
        const resp = await fetch('/api/delete-synonym', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            wordId,
            word,
            targetWord,
            sourceKind: button.dataset.sourceKind || '',
            sourceId: button.dataset.sourceId || ''
          }})
        }});
        const result = await resp.json();
        if (!resp.ok || !result.ok) {{
          throw new Error(result.error || `HTTP ${{resp.status}}`);
        }}
        alert(`已删除「${{targetWord}}」。\\n候选删除：${{result.removed.lexicalSuggestions}}\\n关系删除：${{result.removed.wordRelations}}\\n词典删除：${{result.removed.dictionarySynonyms}}`);
        window.location.reload();
      }} catch (error) {{
        alert(`删除失败：${{error.message}}\\n如果当前还是静态 http.server，请让我重新启动 review API 服务。`);
        button.disabled = false;
        button.textContent = '×';
      }}
    }}

    function init() {{
      [...new Set(rows.map(r => r.chapter).filter(Boolean))].sort().forEach(ch => {{
        const option = document.createElement('option'); option.value = ch; option.textContent = ch; chapterEl.appendChild(option);
      }});
      [...new Set(rows.map(r => r.learningStatus).filter(Boolean))].sort().forEach(st => {{
        const option = document.createElement('option'); option.value = st; option.textContent = st; statusEl.appendChild(option);
      }});
      chipsEl.innerHTML = chipDefs.map(([key, label]) => `<button class="chip" data-key="${{key}}">${{label}} <b>${{chipCount(key)}}</b></button>`).join('');
      document.querySelectorAll('.chip').forEach(btn => btn.onclick = () => {{
        const key = btn.dataset.key;
        active.has(key) ? active.delete(key) : active.add(key);
        btn.classList.toggle('active');
        syncStatActive();
        render();
      }});
      document.getElementById('stats').addEventListener('click', event => {{
        const card = event.target.closest('[data-filter-key]');
        if (!card) return;
        const key = card.dataset.filterKey;
        active.clear();
        searchEl.value=''; chapterEl.value=''; statusEl.value='';
        active.add(key);
        document.querySelectorAll('.chip').forEach(btn => btn.classList.toggle('active', btn.dataset.key === key));
        syncStatActive();
        render();
        document.querySelector('.table-wrap').scrollIntoView({{ behavior:'smooth', block:'start' }});
      }});
      document.getElementById('reset').onclick = () => {{
        active.clear(); searchEl.value=''; chapterEl.value=''; statusEl.value='';
        document.querySelectorAll('.chip').forEach(btn => btn.classList.remove('active'));
        syncStatActive();
        render();
      }};
      document.getElementById('toggleEdit').onclick = () => {{
        editMode = !editMode;
        document.body.classList.toggle('editing', editMode);
        document.getElementById('toggleEdit').textContent = editMode ? '关闭编辑' : '开启编辑';
        render();
      }};
      document.getElementById('submitMarks').onclick = submitMarks;
      document.getElementById('clearMarks').onclick = clearMarks;
      document.getElementById('submitSenseDecisions').onclick = submitSenseDecisions;
      document.getElementById('clearSenseDecisions').onclick = clearSenseDecisions;
      document.getElementById('submitShortDefinitionReviews').onclick = submitShortDefinitionReviews;
      document.getElementById('clearShortDefinitionReviews').onclick = clearShortDefinitionReviews;
      document.getElementById('exportRelationSenseDecisions').onclick = exportRelationSenseDecisions;
      document.getElementById('clearRelationSenseDecisions').onclick = clearRelationSenseDecisions;
      document.getElementById('exportPatch').onclick = exportPatch;
      document.getElementById('exportCsv').onclick = exportCsv;
      tbody.addEventListener('click', event => {{
        const more = event.target.closest('.show-more');
        if (more) {{
          const target = document.getElementById(more.dataset.target);
          if (target) target.classList.toggle('expanded');
          more.textContent = target && target.classList.contains('expanded') ? '收起' : more.textContent.replace('收起', '展开全部');
        }}
        const editToggle = event.target.closest('.edit-toggle');
        if (editToggle) {{
          const target = document.getElementById(editToggle.dataset.target);
          if (target) target.classList.toggle('open');
        }}
        const markBtn = event.target.closest('.mark-btn');
        if (markBtn) {{
          toggleMark(markBtn.dataset.wordId, markBtn.dataset.field);
        }}
        const deleteBtn = event.target.closest('.delete-badge');
        if (deleteBtn) {{
          deleteSynonymBadge(deleteBtn);
        }}
        const senseBtn = event.target.closest('.sense-review-btn');
        if (senseBtn) {{
          setSenseDecision(senseBtn.dataset.wordId, senseBtn.dataset.decision);
        }}
        const shortReviewBtn = event.target.closest('.short-review-btn');
        if (shortReviewBtn) {{
          setShortDefinitionReview(shortReviewBtn.dataset.wordId, shortReviewBtn.dataset.decision);
        }}
        const bindBtn = event.target.closest('.bind-sense-btn');
        if (bindBtn) {{
          handleRelationSenseDecision(bindBtn);
        }}
        const bulkBindBtn = event.target.closest('.bulk-bind-btn');
        if (bulkBindBtn) {{
          handleBulkRelationSenseDecision(bulkBindBtn);
        }}
      }});
      tbody.addEventListener('input', event => {{
        const field = event.target.dataset.editField;
        const wordId = event.target.dataset.wordId;
        if (!field || !wordId) return;
        edits[wordId] = edits[wordId] || {{}};
        edits[wordId][field] = event.target.value;
        edits[wordId].word = event.target.dataset.word || '';
        localStorage.setItem(editStorageKey, JSON.stringify(edits));
      }});
      [searchEl, chapterEl, statusEl].forEach(el => el.addEventListener('input', render));
      renderStats();
      renderMarkSummary();
      render();
    }}

    function renderStats() {{
      const cards = [
        ['总词数', summary.totalWords, ''],
        ['newdocs 新词', summary.newdocsWords, 'newdocsWords'],
        ['自动英文短释待审', summary.autoEnglishShortDefinitions, 'autoEnglishShortDefinitions'],
        ['缺近义/同义', summary.missingAnySynonyms, 'anySynonyms'],
        ['缺反义词', summary.missingAnyAntonyms, 'anyAntonyms'],
        ['无词关系', summary.missingRelations, 'relations'],
        ['无搭配/句型', summary.missingCollocations, 'collocations'],
        ['无构词拆解', summary.missingMorphologyAnalysis, 'morphologyAnalysis'],
        ['未绑定待处理', rows.filter(hasUnresolvedUnbound).length, 'unboundRelationCandidates'],
        ['疑似多词性', summary.mixedPosSenseCandidates, 'mixedPosSenseCandidate'],
        ['需人工拆义', summary.needsHumanSenseReview, 'needsHumanSenseReview']
      ];
      document.getElementById('stats').innerHTML = cards.map(([k,v,key]) => `<div class="stat ${{key ? 'clickable' : ''}}" ${{key ? `data-filter-key="${{key}}"` : ''}}>${{k}}<b>${{v}}</b></div>`).join('');
      syncStatActive();
    }}

    function chipCount(key) {{
      if (key === 'newdocsWords') return rows.filter(r => r.isNewdocsWord).length;
      if (key === 'autoEnglishShortDefinitions') return rows.filter(r => r.shortDefinitionStatus === 'auto_from_english_definition_pending_review').length;
      if (key === 'unboundRelationCandidates') return rows.filter(hasUnresolvedUnbound).length;
      return rows.filter(r => r.missing[key]).length;
    }}

    function syncStatActive() {{
      document.querySelectorAll('[data-filter-key]').forEach(card => {{
        card.classList.toggle('active', active.has(card.dataset.filterKey));
      }});
    }}

    function filtered() {{
      const q = searchEl.value.trim().toLowerCase();
      return rows.filter(r => {{
        const edit = edits[r.wordId] || {{}};
        const hay = [r.word, r.translation, r.definitionEn, r.shortDefinitionEn, r.shortDefinitionZh, r.chapter, r.primaryLineText, r.primaryLineZh, edit.synonyms, edit.antonyms, edit.confusables, edit.contrasts, edit.note, ...(r.articleTitles || []), ...(r.lexicalSynonyms || []), ...(r.lexicalAntonyms || []), ...(r.lexicalContrasts || []), ...(r.semanticNear || []), ...(r.spellingConfusables || [])].join('\\n').toLowerCase();
        return (!q || hay.includes(q))
          && (!chapterEl.value || r.chapter === chapterEl.value)
          && (!statusEl.value || r.learningStatus === statusEl.value)
          && [...active].every(key => {{
            if (key === 'newdocsWords') return r.isNewdocsWord;
            if (key === 'autoEnglishShortDefinitions') return r.shortDefinitionStatus === 'auto_from_english_definition_pending_review';
            if (key === 'unboundRelationCandidates') return hasUnresolvedUnbound(r);
            return r.missing[key];
          }});
      }});
    }}

    function render() {{
      const visible = filtered();
      const unresolvedCount = rows.reduce((sum, row) => sum + unresolvedUnboundItems(row).length, 0);
      countLabel.textContent = `当前显示 ${{visible.length}} / ${{rows.length}} 个词｜未绑定待处理 ${{unresolvedCount}} 条`;
      tbody.innerHTML = visible.map(rowHtml).join('');
      renderMarkSummary();
    }}

    function senseHtml(r) {{
      const mixed = r.mixedPosSenseCandidate;
      const manual = r.semanticManualReview;
      const mixedBadge = mixed ? `<div><span class="badge warn" title="${{esc(mixed.definitionZh || '')}}">疑似待拆：${{esc((mixed.detectedPos || []).join(' / '))}}</span></div>` : '';
      const manualBadge = manual ? `<div><span class="badge warn" title="${{esc(manual.reasonZh || '')}}">需人工确认：${{esc(manual.reasonZh || '语义拆分粒度待确认')}}</span></div>` : '';
      const reviewTools = manual ? senseReviewTools(r) : '';
      if (!r.senses || !r.senses.length) return `${{mixedBadge}}${{manualBadge}}${{reviewTools}}<div>${{esc(r.translation || '')}}</div>`;
      return mixedBadge + manualBadge + reviewTools + r.senses.map(s => `<span class="sense"><span class="pos">${{esc(s.pos || '?')}}</span>${{esc(s.translation || '')}}</span>`).join('');
    }}

    function senseReviewTools(r) {{
      const decision = (senseDecisions[r.wordId] || {{}}).decision || '';
      return `<div class="sense-review-tools">
        <button class="sense-review-btn ${{decision === 'split' ? 'selected' : ''}}" data-word-id="${{esc(r.wordId)}}" data-decision="split">需要拆</button>
        <button class="sense-review-btn ${{decision === 'skip' ? 'selected' : ''}}" data-word-id="${{esc(r.wordId)}}" data-decision="skip">不用拆</button>
      </div>`;
    }}

    function setSenseDecision(wordId, decision) {{
      if (!wordId || !decision) return;
      const row = rows.find(r => r.wordId === wordId);
      if (!row) return;
      const label = decision === 'split' ? '需要拆' : '不用拆';
      const ok = confirm(`确认把「${{row.word}}」标记为「${{label}}」吗？`);
      if (!ok) return;
      senseDecisions[wordId] = {{
        wordId,
        word: row.word,
        decision,
        decisionLabelZh: label,
        translation: row.translation || '',
        currentSenses: row.senses || [],
        detectedPos: ((row.mixedPosSenseCandidate || {{}}).detectedPos || []),
        reasonZh: ((row.semanticManualReview || {{}}).reasonZh || ''),
        decidedAt: new Date().toISOString(),
        status: decision === 'split' ? 'user_marked_needs_semantic_split' : 'user_marked_no_split_needed'
      }};
      localStorage.setItem(senseDecisionStorageKey, JSON.stringify(senseDecisions));
      render();
    }}

    function editValue(r, field) {{
      return esc((edits[r.wordId] || {{}})[field] || '');
    }}

    function editBox(r, field, label, placeholder='') {{
      return `<label class="muted">${{label}}</label><textarea class="editbox" data-word-id="${{esc(r.wordId)}}" data-word="${{esc(r.word)}}" data-edit-field="${{field}}" placeholder="${{esc(placeholder)}}">${{editValue(r, field)}}</textarea>`;
    }}

    function cellEditor(r, field, label, placeholder='') {{
      const id = `edit_${{r.wordId}}_${{field}}`;
      return `<div class="cell-edit"><button class="edit-toggle" data-target="${{id}}">编辑</button><div id="${{id}}" class="cell-editor">${{editBox(r, field, label, placeholder)}}</div></div>`;
    }}

    function quickCellEditor(r, field, label, placeholder='') {{
      const id = `quick_edit_${{r.wordId}}_${{field}}`;
      return `<div class="quick-cell-edit"><button class="edit-toggle" data-target="${{id}}">编辑</button><div id="${{id}}" class="cell-editor">${{editBox(r, field, label, placeholder)}}</div></div>`;
    }}

    function isMarked(wordId, field) {{
      return !!((marks[wordId] || {{}})[field]);
    }}

    function markTools(r, field, label) {{
      const marked = isMarked(r.wordId, field);
      return `<div class="mark-tools"><button class="mark-btn ${{marked ? 'marked' : ''}}" data-word-id="${{esc(r.wordId)}}" data-field="${{field}}">${{marked ? '已标记' : '标记待补'}}${{label}}</button></div>`;
    }}

    function toggleMark(wordId, field) {{
      if (!wordId || !field) return;
      marks[wordId] = marks[wordId] || {{}};
      marks[wordId][field] = !marks[wordId][field];
      marks[wordId].updatedAt = new Date().toISOString();
      const row = rows.find(r => r.wordId === wordId);
      if (row) marks[wordId].word = row.word;
      if (!marks[wordId].synonyms && !marks[wordId].antonyms) delete marks[wordId];
      localStorage.setItem(markStorageKey, JSON.stringify(marks));
      render();
    }}

    function markedPayload() {{
      return Object.entries(marks).flatMap(([wordId, value]) => {{
        const row = rows.find(r => r.wordId === wordId) || {{}};
        const requests = [];
        if (value.synonyms) requests.push('synonyms');
        if (value.antonyms) requests.push('antonyms');
        return requests.map(type => ({{
          wordId,
          word: row.word || value.word || '',
          requestType: type,
          requestLabelZh: type === 'synonyms' ? '补充近义/同类/语义辨析' : '补充反义/对比',
          chapter: row.chapter || '',
          translation: row.translation || '',
          phonetic: row.phonetic || '',
          existingSynonyms: [
            ...(row.dictSynonyms || []),
            ...(row.relationSynonyms || []),
            ...(row.lexicalSynonyms || []),
            ...(row.semanticNear || [])
          ],
          existingAntonyms: [
            ...(row.dictAntonyms || []),
            ...(row.relationAntonyms || []),
            ...(row.lexicalAntonyms || []),
            ...(row.lexicalContrasts || [])
          ],
          primaryLineId: row.primaryLineId || '',
          primaryLineText: row.primaryLineText || '',
          primaryLineZh: row.primaryLineZh || '',
          markedAt: value.updatedAt || null,
          status: 'user_marked_for_ai_enrichment'
        }}));
      }});
    }}

    function renderMarkSummary() {{
      const payload = markedPayload();
      const synCount = payload.filter(item => item.requestType === 'synonyms').length;
      const antCount = payload.filter(item => item.requestType === 'antonyms').length;
      const sensePayload = senseDecisionPayload();
      const splitCount = sensePayload.filter(item => item.decision === 'split').length;
      const skipCount = sensePayload.filter(item => item.decision === 'skip').length;
      const relationSensePayload = relationSenseDecisionPayload();
      const bindCount = relationSensePayload.filter(item => item.action === 'bind').length;
      const rejectCount = relationSensePayload.filter(item => item.action === 'reject').length;
      const shortPayload = shortDefinitionReviewPayload();
      const shortApproveCount = shortPayload.filter(item => item.decision === 'approved').length;
      const shortRejectCount = shortPayload.filter(item => item.decision === 'rejected').length;
      document.getElementById('markSummary').textContent = `已标记 ${{payload.length}}（近义 ${{synCount}} / 反义 ${{antCount}}）｜短释审核 ${{shortPayload.length}}（通过 ${{shortApproveCount}} / 有问题 ${{shortRejectCount}}）｜拆义选择 ${{sensePayload.length}}（拆 ${{splitCount}} / 不拆 ${{skipCount}}）｜词义绑定 ${{relationSensePayload.length}}（绑 ${{bindCount}} / 拒 ${{rejectCount}}）`;
    }}

    function shortDefinitionReviewLabel(decision) {{
      if (decision === 'approved') return '通过';
      if (decision === 'rejected') return '有问题';
      return '';
    }}

    function shortDefinitionReviewTools(r) {{
      const local = shortDefinitionReviews[r.wordId] || {{}};
      const persisted = r.shortDefinitionReview || {{}};
      const decision = local.decision || '';
      const persistedStatus = persisted.status || '';
      const statusLabel = decision
        ? `本次已选：${{shortDefinitionReviewLabel(decision)}}`
        : (persistedStatus ? `已入库状态：${{persistedStatus === 'approved' ? '已通过' : persistedStatus === 'rejected' ? '有问题' : persistedStatus}}` : `来源：${{r.shortDefinitionStatus || '未标注'}}`);
      return `<div class="short-review-tools">
        <button class="short-review-btn approve ${{decision === 'approved' ? 'selected' : ''}}" data-word-id="${{esc(r.wordId)}}" data-decision="approved">通过</button>
        <button class="short-review-btn reject ${{decision === 'rejected' ? 'selected' : ''}}" data-word-id="${{esc(r.wordId)}}" data-decision="rejected">有问题</button>
      </div><div class="short-review-status">${{esc(statusLabel)}}</div>`;
    }}

    function setShortDefinitionReview(wordId, decision) {{
      if (!wordId || !decision) return;
      const row = rows.find(r => r.wordId === wordId);
      if (!row) return;
      const current = ((edits[wordId] || {{}}).shortDefinitionEn || row.shortDefinitionEn || '').trim();
      if (!current) {{
        alert('这个词还没有英文短释，不能审核。');
        return;
      }}
      shortDefinitionReviews[wordId] = {{
        wordId,
        word: row.word || '',
        decision,
        decisionLabelZh: shortDefinitionReviewLabel(decision),
        shortDefinitionEn: current,
        originalShortDefinitionEn: row.shortDefinitionEn || '',
        shortDefinitionStatus: row.shortDefinitionStatus || '',
        reviewedAt: new Date().toISOString()
      }};
      localStorage.setItem(shortDefinitionReviewStorageKey, JSON.stringify(shortDefinitionReviews));
      render();
    }}

    function shortDefinitionReviewPayload() {{
      return Object.values(shortDefinitionReviews)
        .filter(item => item && item.wordId && item.decision)
        .map(item => {{
          const row = rows.find(r => r.wordId === item.wordId) || {{}};
          const edited = ((edits[item.wordId] || {{}}).shortDefinitionEn || '').trim();
          return {{
            ...item,
            shortDefinitionEn: edited || item.shortDefinitionEn || row.shortDefinitionEn || '',
            originalShortDefinitionEn: item.originalShortDefinitionEn || row.shortDefinitionEn || ''
          }};
        }})
        .filter(item => item.shortDefinitionEn)
        .sort((a, b) => String(a.word || '').localeCompare(String(b.word || '')));
    }}

    async function submitShortDefinitionReviews() {{
      const payload = shortDefinitionReviewPayload();
      if (!payload.length) {{
        alert('还没有选择任何短释审核结果。');
        return;
      }}
      const approvedCount = payload.filter(item => item.decision === 'approved').length;
      const rejectedCount = payload.filter(item => item.decision === 'rejected').length;
      const preview = payload.slice(0, 16).map(item => `${{item.word}}：${{item.decisionLabelZh}}｜${{item.shortDefinitionEn}}`).join('\\n');
      const more = payload.length > 16 ? `\\n... 还有 ${{payload.length - 16}} 条` : '';
      const ok = confirm(`准备提交 ${{payload.length}} 条英文短释审核：\\n通过 ${{approvedCount}} / 有问题 ${{rejectedCount}}\\n\\n${{preview}}${{more}}\\n\\n确认后会写回数据源、重建页面，并清空本次选择。`);
      if (!ok) return;
      const button = document.getElementById('submitShortDefinitionReviews');
      button.disabled = true;
      button.textContent = '提交中...';
      try {{
        const resp = await fetch('/api/review-short-definitions', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            schema: 'ielts_short_definition_reviews_v1',
            submittedAt: new Date().toISOString(),
            items: payload
          }})
        }});
        const result = await resp.json();
        if (!resp.ok || !result.ok) throw new Error(result.error || `HTTP ${{resp.status}}`);
        shortDefinitionReviews = {{}};
        localStorage.setItem(shortDefinitionReviewStorageKey, JSON.stringify(shortDefinitionReviews));
        alert(`已提交短释审核。\\n写回：${{result.updated}} 条\\n通过：${{result.approved}} / 有问题：${{result.rejected}}`);
        window.location.reload();
      }} catch (error) {{
        alert(`提交失败：${{error.message}}\\n如果当前不是 review API 服务，请让我重启服务。`);
        button.disabled = false;
        button.textContent = '提交短释审核';
      }}
    }}

    function clearShortDefinitionReviews() {{
      const payload = shortDefinitionReviewPayload();
      if (payload.length && !confirm(`确定清空当前 ${{payload.length}} 条短释审核选择吗？`)) return;
      shortDefinitionReviews = {{}};
      localStorage.setItem(shortDefinitionReviewStorageKey, JSON.stringify(shortDefinitionReviews));
      render();
    }}

    function submitMarks() {{
      const payload = markedPayload();
      if (!payload.length) {{
        alert('还没有标记任何近义词/反义词待补项。');
        return;
      }}
      const preview = payload.slice(0, 12).map(item => `${{item.word}}：${{item.requestLabelZh}}`).join('\\n');
      const more = payload.length > 12 ? `\\n... 还有 ${{payload.length - 12}} 条` : '';
      const ok = confirm(`准备提交 ${{payload.length}} 条待补语料标记：\\n\\n${{preview}}${{more}}\\n\\n确认后会导出 JSON，我会按这份清单继续补。`);
      if (!ok) return;
      const submitted = {{
        schema: 'ielts_word_inventory_relation_marks_v1',
        submittedAt: new Date().toISOString(),
        total: payload.length,
        items: payload
      }};
      download('ielts_relation_enrichment_marks.json', 'application/json;charset=utf-8', JSON.stringify(submitted, null, 2));
      console.log('IELTS relation enrichment marks', submitted);
      marks = {{}};
      localStorage.setItem(markStorageKey, JSON.stringify(marks));
      render();
      alert('已生成 ielts_relation_enrichment_marks.json，并已清空本次标记。你可以继续筛下一批。');
    }}

    function clearMarks() {{
      const payload = markedPayload();
      if (payload.length && !confirm(`确定清空当前 ${{payload.length}} 条标记吗？`)) return;
      marks = {{}};
      localStorage.setItem(markStorageKey, JSON.stringify(marks));
      render();
    }}

    function senseDecisionPayload() {{
      return Object.values(senseDecisions)
        .filter(item => item && item.wordId && item.decision)
        .sort((a, b) => String(a.word || '').localeCompare(String(b.word || '')));
    }}

    function submitSenseDecisions() {{
      const payload = senseDecisionPayload();
      if (!payload.length) {{
        alert('还没有选择任何“需要拆 / 不用拆”。');
        return;
      }}
      const splitCount = payload.filter(item => item.decision === 'split').length;
      const skipCount = payload.filter(item => item.decision === 'skip').length;
      const preview = payload.slice(0, 14).map(item => `${{item.word}}：${{item.decisionLabelZh}}`).join('\\n');
      const more = payload.length > 14 ? `\\n... 还有 ${{payload.length - 14}} 条` : '';
      const ok = confirm(`准备提交 ${{payload.length}} 条拆义审核选择：\\n需要拆 ${{splitCount}} / 不用拆 ${{skipCount}}\\n\\n${{preview}}${{more}}\\n\\n确认后会导出 JSON，我会按这份清单继续处理。`);
      if (!ok) return;
      const submitted = {{
        schema: 'ielts_word_inventory_sense_decisions_v1',
        submittedAt: new Date().toISOString(),
        total: payload.length,
        splitCount,
        skipCount,
        items: payload
      }};
      download('ielts_sense_split_decisions.json', 'application/json;charset=utf-8', JSON.stringify(submitted, null, 2));
      console.log('IELTS sense split decisions', submitted);
      alert('已生成 ielts_sense_split_decisions.json。保留当前选择，方便你继续改；需要清空可以点“清空拆义选择”。');
    }}

    function clearSenseDecisions() {{
      const payload = senseDecisionPayload();
      if (payload.length && !confirm(`确定清空当前 ${{payload.length}} 条拆义选择吗？`)) return;
      senseDecisions = {{}};
      localStorage.setItem(senseDecisionStorageKey, JSON.stringify(senseDecisions));
      render();
    }}

    function handleRelationSenseDecision(button) {{
      const key = button.dataset.decisionKey || '';
      const action = button.dataset.action || '';
      if (!key || !action) return;
      const select = document.querySelector(`.bind-sense-select[data-decision-key="${{CSS.escape(key)}}"]`);
      const option = select ? select.options[select.selectedIndex] : null;
      const senseId = select ? select.value : '';
      const wordId = select ? select.dataset.wordId : '';
      const word = select ? select.dataset.word : '';
      const targetWord = select ? select.dataset.targetWord : '';
      if (action === 'bind' && !senseId) {{
        alert('先选择要绑定到哪个词义。');
        return;
      }}
      const label = action === 'bind' ? `绑定到「${{option ? option.textContent : senseId}}」` : '标记为不合适';
      if (!confirm(`确认将「${{word}} -> ${{targetWord}}」${{label}}吗？`)) return;
      relationSenseDecisions[key] = {{
        wordId,
        word,
        targetWord,
        sourceKind: select ? select.dataset.sourceKind : '',
        sourceId: select ? select.dataset.sourceId : '',
        action,
        senseId: action === 'bind' ? senseId : '',
        senseLabel: action === 'bind' && option ? option.textContent : '',
        decidedAt: new Date().toISOString(),
        status: action === 'bind' ? 'user_confirmed_relation_sense' : 'user_rejected_relation_candidate'
      }};
      localStorage.setItem(relationSenseDecisionStorageKey, JSON.stringify(relationSenseDecisions));
      render();
    }}

    function handleBulkRelationSenseDecision(button) {{
      const groupKey = button.dataset.groupKey || '';
      const action = button.dataset.action || '';
      if (!groupKey || action !== 'submit_group') return;
      const selects = Array.from(document.querySelectorAll(`.bind-sense-select[data-group-key="${{CSS.escape(groupKey)}}"]`));
      if (!selects.length) return;
      const unresolved = selects.filter(select => !relationSenseDecisions[select.dataset.decisionKey || '']);
      if (!unresolved.length) {{
        alert('这一组已经都处理过了。');
        return;
      }}
      const unselected = unresolved.filter(select => !select.value);
      if (unselected.length) {{
        alert(`这一组还有 ${{unselected.length}} 个没选。请每个候选都选择词义或“不合适”，再提交本组。`);
        return;
      }}
      const word = unresolved[0].dataset.word || '';
      if (!confirm(`确认提交「${{word}}」这一组 ${{unresolved.length}} 个候选的逐条选择吗？`)) return;
      unresolved.forEach(select => {{
        const key = select.dataset.decisionKey || '';
        const selectedAction = select.value === '__reject__' ? 'reject' : 'bind';
        const selectedOption = select.options[select.selectedIndex];
        relationSenseDecisions[key] = {{
          wordId: select.dataset.wordId || '',
          word: select.dataset.word || '',
          targetWord: select.dataset.targetWord || '',
          sourceKind: select.dataset.sourceKind || '',
          sourceId: select.dataset.sourceId || '',
          action: selectedAction,
          senseId: selectedAction === 'bind' ? select.value : '',
          senseLabel: selectedAction === 'bind' && selectedOption ? selectedOption.textContent : '',
          decidedAt: new Date().toISOString(),
          status: selectedAction === 'bind' ? 'user_confirmed_relation_sense' : 'user_rejected_relation_candidate'
        }};
      }});
      localStorage.setItem(relationSenseDecisionStorageKey, JSON.stringify(relationSenseDecisions));
      render();
    }}

    function relationSenseDecisionPayload() {{
      return Object.values(relationSenseDecisions)
        .filter(item => item && item.wordId && item.targetWord && item.action)
        .sort((a, b) => String(a.word || '').localeCompare(String(b.word || '')) || String(a.targetWord || '').localeCompare(String(b.targetWord || '')));
    }}

    function exportRelationSenseDecisions() {{
      const payload = relationSenseDecisionPayload();
      if (!payload.length) {{
        alert('还没有任何词义绑定/不合适选择。');
        return;
      }}
      const bindCount = payload.filter(item => item.action === 'bind').length;
      const rejectCount = payload.filter(item => item.action === 'reject').length;
      const submitted = {{
        schema: 'ielts_relation_sense_decisions_v1',
        submittedAt: new Date().toISOString(),
        total: payload.length,
        bindCount,
        rejectCount,
        items: payload
      }};
      download('ielts_relation_sense_decisions.json', 'application/json;charset=utf-8', JSON.stringify(submitted, null, 2));
      alert(`已导出 ${{payload.length}} 条词义绑定选择（绑定 ${{bindCount}} / 不合适 ${{rejectCount}}）。`);
    }}

    function clearRelationSenseDecisions() {{
      const payload = relationSenseDecisionPayload();
      if (payload.length && !confirm(`确定清空当前 ${{payload.length}} 条词义绑定选择吗？`)) return;
      relationSenseDecisions = {{}};
      localStorage.setItem(relationSenseDecisionStorageKey, JSON.stringify(relationSenseDecisions));
      render();
    }}

    function rowHtml(r) {{
      const baseSyns = [...(r.dictSynonyms || []), ...(r.relationSynonyms || []).map(x => x + ' (relation)'), ...(r.lexicalSynonyms || []).map(x => x + ' (suggested)'), ...(r.semanticNear || []).map(x => x + ' (semantic)')];
      const baseAnts = [...(r.dictAntonyms || []), ...(r.relationAntonyms || []).map(x => x + ' (relation)'), ...(r.lexicalAntonyms || []).map(x => x + ' (suggested)'), ...(r.lexicalContrasts || []).map(x => x + ' (contrast)')];
      const baseContrasts = [...(r.lexicalContrasts || [])];
      const syns = mergedList(r, baseSyns, 'synonyms');
      const ants = mergedList(r, baseAnts, 'antonyms');
      const confusables = mergedList(r, r.spellingConfusables || [], 'confusables');
      const usagePatterns = mergedList(r, r.usagePatterns || [], 'usagePatterns');
      const usageShown = usagePatterns.slice(0, 5);
      const morphologySegments = mergedList(r, r.morphologySegments || [], 'morphology');
      const relatedWords = mergedList(r, r.relatedWords || [], 'relatedWords');
      const hasRelations = (r.relationCount + r.suggestionCount) > 0 || confusables.length > 0;
      const relationStatus = Object.entries(r.relationStatus || {{}}).map(([k,v]) => `<span class="badge draft">${{esc(k)}}:${{v}}</span>`).join('');
      const suggestionStatus = Object.entries(r.suggestionStatus || {{}}).map(([k,v]) => `<span class="badge draft">suggestion-${{esc(k)}}:${{v}}</span>`).join('');
      const editPanel = `<div class="edit-panel edit-only">
        ${{editBox(r, 'synonyms', '补充近义/同类/语义辨析（逗号或换行分隔）', 'milestone, marker')}}
        ${{editBox(r, 'antonyms', '补充反义词（逗号或换行分隔）', 'invalid')}}
        ${{editBox(r, 'contrasts', '补充语境对比（逗号或换行分隔）', 'unstable, unreliable')}}
        ${{editBox(r, 'confusables', '补充形近/拼写易混（逗号或换行分隔）', 'content, contend')}}
        ${{editBox(r, 'note', '审核备注', '这里写你的判断或待处理说明')}}
      </div>`;
      return `<tr>
        <td class="num">${{r.order}}</td>
        <td><div class="word">${{esc(r.word)}}</div><div class="muted">${{esc(r.wordId)}}</div>${{cellEditor(r, 'wordNote', '编辑单词备注', '例如：英式拼写 / 需拆分词性')}}</td>
        <td>${{senseHtml(r)}}<div class="muted">${{esc(r.phonetic || '无音标')}}</div>${{cellEditor(r, 'senses', '编辑释义/词性/音标', 'n. ...\\nv. ...\\n音标：/.../')}}</td>
        <td class="${{r.shortDefinitionEn ? '' : 'missing-cell'}}"><div class="soft">${{esc(r.shortDefinitionEn || '待补英文短释')}}</div><div class="muted zh-short">${{esc(r.shortDefinitionZh || '待补中文短释')}}</div>${{shortDefinitionReviewTools(r)}}${{cellEditor(r, 'shortDefinitionEn', '编辑英文短释', 'A short phrase explaining the word.')}}</td>
        <td><div>${{esc(r.chapter || '')}}</div><div class="muted">${{r.occurrenceCount}} 次 / ${{r.articleCount}} 篇</div>${{cellEditor(r, 'sourceNote', '编辑出处备注', '这篇文章里的具体语义...')}}</td>
        <td class="${{syns.length ? '' : 'missing-cell'}}">${{markTools(r, 'synonyms', '近义')}}${{synonymGroupsHtml(r, r.synonymGroups || [], '无近义/同义')}}${{cellEditor(r, 'synonyms', '编辑近义/同类/语义辨析', 'knock, pat, rap')}}</td>
        <td class="${{ants.length ? '' : 'missing-cell'}}">${{markTools(r, 'antonyms', '反义')}}${{list(ants, '无反义')}}${{cellEditor(r, 'antonyms', '编辑反义/对比', 'invalid, unreliable')}}</td>
        <td class="${{confusables.length ? '' : 'missing-cell'}}">${{list(confusables, '无形近易混')}}<div class="muted">只放形近/音近且语义或用法不同的词；同词族放派生/相关词。</div>${{quickCellEditor(r, 'confusables', '编辑形近/拼写易混', 'adapt, adopt\\naffect, effect')}}</td>
        <td class="usage-cell ${{usageShown.length ? '' : 'missing-cell'}}">${{countBadge(usageShown.length, '搭配/句型')}}${{list(usageShown, '无', 5, 'usage-list')}}${{cellEditor(r, 'usagePatterns', '编辑搭配/句型', 'provide evidence\\nhave an effect on\\nfocus on')}}</td>
        <td class="${{morphologySegments.length ? '' : 'missing-cell'}}"><span class="badge ${{r.morphologyKind === 'analyzed' ? 'ok' : 'missing'}}">${{esc(r.morphologyKind)}}</span><br>${{list(morphologySegments, '无拆解')}}${{cellEditor(r, 'morphology', '编辑构词说明', 'trans-(prefix): 跨越；改变')}}</td>
        <td class="${{relatedWords.length ? '' : 'missing-cell'}}">${{countBadge(relatedWords.length, '相关')}}<br>${{list(relatedWords, '无')}}${{cellEditor(r, 'relatedWords', '编辑派生/相关词', 'transformation, transformative')}}</td>
        <td><details><summary>${{esc(r.primaryLineId || '查看 / 编辑')}}</summary><div class="detail"><b>EN</b><br>${{esc(r.primaryLineText)}}<br><br><b>ZH</b><br>${{esc(r.primaryLineZh)}}<br><br><b>文章</b><br>${{esc((r.articleTitles || []).join(' / '))}}${{editPanel}}</div></details></td>
        <td><span class="badge draft">${{esc(r.learningStatus || '无')}}</span><br><span class="muted">${{esc(r.reviewStatus || '')}}</span></td>
      </tr>`;
    }}

    function csv(value) {{
      const s = String(value ?? '');
      return /[",\\n\\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
    }}
    function download(name, type, text) {{
      const blob = new Blob([text], {{type}});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = name; a.click();
      URL.revokeObjectURL(url);
    }}
    function exportPatch() {{
      const patch = Object.entries(edits)
        .filter(([_, value]) => Object.values(value || {{}}).some(v => String(v || '').trim()))
        .map(([wordId, value]) => ({{
          wordId,
          word: value.word || (rows.find(r => r.wordId === wordId) || {{}}).word || '',
          wordNote: value.wordNote || '',
          senses: value.senses || '',
          sourceNote: value.sourceNote || '',
          synonyms: splitEditList(value.synonyms),
          antonyms: splitEditList(value.antonyms),
          contrasts: splitEditList(value.contrasts),
          confusables: splitEditList(value.confusables),
          usagePatterns: splitEditList(value.usagePatterns),
          morphology: splitEditList(value.morphology),
          relatedWords: splitEditList(value.relatedWords),
          commonErrors: splitEditList(value.commonErrors),
          note: value.note || '',
          status: 'draft_user_edited'
        }}));
      download('ielts_word_inventory_edits.json', 'application/json;charset=utf-8', JSON.stringify(patch, null, 2));
    }}
    function exportCsv() {{
      const header = ['order','word','translation','chapter','missingSynonyms','missingAntonyms','relationCount','collocationCount','morphologyKind','relatedWordCount','grammarCount','primaryLineId'];
      const body = filtered().map(r => [
        r.order, r.word, r.translation, r.chapter, r.missing.anySynonyms, r.missing.anyAntonyms,
        r.relationCount + r.suggestionCount, r.collocationCount, r.morphologyKind, r.relatedWordCount, r.grammarCount, r.primaryLineId
      ].map(csv).join(','));
      download('ielts_word_inventory_filtered.csv', 'text/csv;charset=utf-8', [header.join(','), ...body].join('\\n'));
    }}
    init();
  </script>
</body>
</html>"""

    HTML_PATH.write_text(html, encoding="utf-8")
    print(json.dumps({"html": str(HTML_PATH), "summary": str(SUMMARY_PATH), **summary}, ensure_ascii=False, indent=2, default=dict))


if __name__ == "__main__":
    main()
