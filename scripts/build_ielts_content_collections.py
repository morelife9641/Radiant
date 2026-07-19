#!/usr/bin/env python3
"""Build IELTS content topics, lines, line-word links and learning baselines."""

from __future__ import annotations

import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
MEMBERSHIP_PATH = OUT_DIR / "wordbook_words.json"
REPORT_PATH = ROOT / "docs/IELTS真题语境词书-内容集合导入说明.md"


def import_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


BOOK_BUILDER = import_script("book_builder", ROOT / "scripts/build_ielts_content_wordbook_words.py")
ANTS = import_script("ants_builder", ROOT / "scripts/build_ants_core_word_report.py")
MATCHER = BOOK_BUILDER.MATCHER


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def normalize_text(value: str) -> str:
    return " ".join(MATCHER.normalize(token) for token in MATCHER.WORD_RE.findall(value))


def match_line(sentence: str, article: dict, sentence_index: int, words_by_normalized: dict[str, dict], phrases: set[str]):
    line_id = BOOK_BUILDER.line_id(article, sentence_index)
    hits = defaultdict(lambda: {"positions": [], "surfaces": [], "modes": set()})

    for phrase in phrases:
        pattern = re.compile(rf"(?<![A-Za-z]){re.escape(phrase).replace(r'\ ', r'\s+')}(?![A-Za-z])", re.I)
        for match in pattern.finditer(sentence):
            hits[phrase]["positions"].append({"start": match.start(), "end": match.end()})
            hits[phrase]["surfaces"].append(match.group(0))
            hits[phrase]["modes"].add("phrase")

    single = set(words_by_normalized) - phrases
    for token_index, match in enumerate(MATCHER.WORD_RE.finditer(sentence)):
        raw = match.group(0)
        surface = MATCHER.normalize(raw)
        key = surface if surface in single else next(
            (candidate for candidate in MATCHER.lemma_candidates(surface) if candidate in single), None
        )
        if key is None or BOOK_BUILDER.should_skip_proper_noun(raw, token_index, key, surface):
            continue
        hits[key]["positions"].append({"start": match.start(), "end": match.end()})
        hits[key]["surfaces"].append(raw)
        hits[key]["modes"].add("exact" if key == surface else "lemma")

    links = []
    for normalized, data in hits.items():
        word = words_by_normalized[normalized]
        modes = sorted(data["modes"])
        links.append({
            "_id": f"{line_id}:{word['_id']}",
            "topicId": article["topicId"],
            "lineId": line_id,
            "wordId": word["_id"],
            "normalized": normalized,
            "surface": data["surfaces"][0],
            "positions": data["positions"],
            "matchType": "+".join(modes),
            "createdAt": None,
        })
    return links


def build_content(articles: list[dict], words_by_normalized: dict[str, dict]):
    phrases = {value for value in words_by_normalized if " " in value}
    topics = []
    lines = []
    links = []
    lines_by_id = {}
    word_links = defaultdict(list)
    existing_translations = {}
    existing_lines_path = OUT_DIR / "content_lines.json"
    if existing_lines_path.exists():
        for existing in load_jsonl(existing_lines_path):
            if existing.get("translationZh"):
                existing_translations[existing["_id"]] = {
                    "translationZh": existing["translationZh"],
                    "translationStatus": existing.get("translationStatus") or "pending_human_review",
                    "translationMeta": existing.get("translationMeta"),
                    "sourceReview": existing.get("sourceReview"),
                    "textOriginal": existing.get("textOriginal"),
                    "correctedText": existing.get("correctedText"),
                }
    ants_translation_by_text = {}
    for index, sentence in enumerate(ANTS.article_sentences(ANTS.extract_article()), 1):
        if index in ANTS.SENTENCE_ZH:
            ants_translation_by_text[normalize_text(sentence)] = ANTS.SENTENCE_ZH[index]

    for article in articles:
        article_lines = []
        article_links = []
        for sentence_index, sentence in enumerate(BOOK_BUILDER.split_sentences(article["body"]), 1):
            line_id = BOOK_BUILDER.line_id(article, sentence_index)
            matched = match_line(sentence, article, sentence_index, words_by_normalized, phrases)
            translation = ants_translation_by_text.get(normalize_text(sentence), "") if article["linePrefix"] == "ants" else ""
            row = {
                "_id": line_id,
                "topicId": article["topicId"],
                "articleTitle": article["title"],
                "text": sentence,
                "normalizedText": normalize_text(sentence),
                "translationZh": translation,
                "translationStatus": "draft_human_review" if translation else "pending_machine_translation",
                "speaker": {"name": "Narrator", "type": "narrator"},
                "scene": {
                    "section": f"Reading Test {article['test']} / Passage {article['section']}",
                    "season": f"Test {article['test']}",
                    "episode": f"Passage {article['section']}",
                    "timestampMs": None,
                },
                "source": {
                    "name": "IELTS Reading Actual Tests 2016-2017",
                    "sourceFile": BOOK_BUILDER.PDF.name,
                    "locator": f"{article['title']}#sentence-{sentence_index:02d}",
                    "sourceUrl": "",
                },
                "tokenCount": len(MATCHER.WORD_RE.findall(sentence)),
                "matchedWordCount": len(matched),
                "status": "draft",
                "createdAt": None,
                "updatedAt": None,
            }
            preserved = existing_translations.get(line_id)
            if preserved:
                row["translationZh"] = preserved["translationZh"]
                row["translationStatus"] = preserved["translationStatus"]
                if preserved.get("translationMeta"):
                    row["translationMeta"] = preserved["translationMeta"]
                for field in ("sourceReview", "textOriginal", "correctedText"):
                    if preserved.get(field):
                        row[field] = preserved[field]
            if article["linePrefix"] == "ants" and sentence_index in ANTS.SOURCE_NOTES:
                row["sourceNote"] = ANTS.SOURCE_NOTES[sentence_index]
            article_lines.append(row)
            article_links.extend(matched)
            lines_by_id[line_id] = row
            for link in matched:
                word_links[link["wordId"]].append(link)

        topics.append({
            "_id": article["topicId"],
            "name": article["title"],
            "type": "ielts_reading",
            "description": f"IELTS Reading Test {article['test']} Passage {article['section']}",
            "language": "en",
            "cover": {"image": "", "color": "#234E52"},
            "status": "draft",
            "source": {
                "name": "IELTS Reading Actual Tests 2016-2017",
                "sourceFile": BOOK_BUILDER.PDF.name,
                "licenseNote": "For learning use. Verify publication rights before commercial release.",
            },
            "meta": {"test": article["test"], "passage": article["section"], "linePrefix": article["linePrefix"]},
            "stats": {
                "lineCount": len(article_lines),
                "audioCount": 0,
                "matchedLineCount": sum(row["matchedWordCount"] > 0 for row in article_lines),
                "wordLinkCount": len(article_links),
                "uniqueWordCount": len({link["wordId"] for link in article_links}),
            },
            "createdAt": None,
            "updatedAt": None,
        })
        lines.extend(article_lines)
        links.extend(article_links)
    return topics, lines, links, lines_by_id, word_links


def parse_derivatives(values: list[str]) -> list[dict]:
    return ANTS.derivative_objects(values)


def corpus_candidates(word_id: str, word_links: dict[str, list[dict]], lines_by_id: dict[str, dict], limit: int = 5):
    candidates = Counter()
    source_ids = {}
    for link in word_links.get(word_id, []):
        line = lines_by_id[link["lineId"]]
        for position in link["positions"]:
            before = line["text"][:position["start"]]
            after = line["text"][position["end"]:]
            left = MATCHER.WORD_RE.findall(before)[-2:]
            center = line["text"][position["start"]:position["end"]]
            right = MATCHER.WORD_RE.findall(after)[:2]
            phrase = " ".join(left + [center] + right)
            if len(phrase.split()) < 2:
                continue
            key = phrase.lower()
            candidates[key] += 1
            source_ids[key] = link["lineId"]
    return [{
        "text": value,
        "sourceLineId": source_ids[value],
        "sourceType": "corpus_candidate",
        "status": "pending_human_review",
    } for value, _ in candidates.most_common(limit)]


def first_translation(word: dict) -> str:
    senses = word.get("senses") or []
    return str(senses[0].get("translation") or "").strip() if senses else ""


def build_learning(memberships: list[dict], words_by_id: dict[str, dict], word_links, lines_by_id):
    rows = []
    for membership in memberships:
        word_id = membership["wordId"]
        word = words_by_id[word_id]
        normalized = membership["normalized"]
        translation = first_translation(word)
        is_ants = membership["chapter"] == BOOK_BUILDER.TOPICS[0][2]
        derivatives = parse_derivatives(ANTS.DERIVATIVES.get(normalized, [])) if is_ants else []
        for related in derivatives:
            if related.get("wordId") in words_by_id:
                related["clickable"] = True
            else:
                related.pop("wordId", None)
                related["clickable"] = False
                related["referenceStatus"] = "text_only_missing_word_doc"

        if is_ants and normalized in ANTS.EDITORIAL:
            _, _, raw_collocations = ANTS.EDITORIAL[normalized]
            collocations = []
            for value in raw_collocations:
                text, translation_zh = value.rsplit(" ", 1)
                collocations.append({"text": text, "translationZh": translation_zh, "status": "draft"})
            segments = ANTS.MORPH_SEGMENTS.get(normalized) or [{
                "form": normalized, "type": "base", "meaningZh": ANTS.SENSE_OVERRIDES[normalized][1],
                "noteZh": "建议作为整体词学习，不强行拆分词根词缀。",
            }]
            morphology = {
                "segments": segments,
                "explanationZh": ANTS.MORPHOLOGY.get(normalized) or f"{normalized} 按整体词处理，不强行拆分。",
                "relatedWords": derivatives,
            }
            grammar = [{
                "pattern": ANTS.GRAMMAR_PATTERNS[normalized],
                "exampleEn": ANTS.EDITORIAL[normalized][0],
                "exampleZh": ANTS.EDITORIAL[normalized][1],
                "status": "draft",
            }]
            error = ANTS.ERRORS.get(normalized)
            common_errors = ([{
                "wrong": error[0], "correct": error[1], "explanationZh": error[2], "status": "draft",
            }] if error else [])
            status = "draft_editorial"
        else:
            morphology = {
                "segments": [{
                    "form": normalized, "type": "base", "meaningZh": translation,
                    "noteZh": "当前仅建立整体词基线；构词分析待词典编辑审核。",
                }],
                "explanationZh": f"{normalized} 当前按整体词学习，不自动推断词根词缀。",
                "relatedWords": [],
            }
            # Arbitrary context windows are not collocations. Keep this empty until
            # an editor or a trusted lexical source supplies a useful expression.
            collocations = []
            grammar = []
            common_errors = []
            status = "generated_baseline"

        topic_ids = []
        for link in word_links.get(word_id, []):
            if link["topicId"] not in topic_ids:
                topic_ids.append(link["topicId"])
        occurrence_count = membership["sourceStats"]["occurrenceCount"]
        priority = 5 if membership["important"] and occurrence_count >= 10 else 4 if membership["important"] else 3
        rows.append({
            "_id": word_id,
            "wordId": word_id,
            "word": membership["word"],
            "normalized": normalized,
            "primaryLineId": membership["sourceStats"]["primaryLineId"],
            "preferredTopicIds": topic_ids[:5],
            "morphology": morphology,
            "collocations": collocations,
            "grammarPatterns": grammar,
            "commonErrors": common_errors,
            "examProfile": {
                "skills": ["reading"],
                "topics": topic_ids,
                "priority": priority,
                "writingValue": 3 if membership["important"] else 2,
            },
            "sourceStats": membership["sourceStats"],
            "provenance": {
                "dictionarySources": ["words", "ECDICT"],
                "corpusSource": BOOK_BUILDER.PDF.name,
                "generationMethod": "editorial" if is_ants else "dictionary_baseline",
                "reviewStatus": "pending_human_review",
            },
            "status": status,
            "createdAt": None,
            "updatedAt": None,
        })
    return rows


def validate(topics, lines, links, learning, memberships, words_by_id):
    topic_ids = {row["_id"] for row in topics}
    line_ids = {row["_id"] for row in lines}
    link_ids = {row["_id"] for row in links}
    learning_ids = {row["_id"] for row in learning}
    if len(topic_ids) != len(topics) or len(line_ids) != len(lines) or len(link_ids) != len(links):
        raise RuntimeError("duplicate IDs in content collections")
    if len(learning_ids) != len(learning) or len(learning) != len(memberships):
        raise RuntimeError("word_learning_content count mismatch")
    for link in links:
        if link["topicId"] not in topic_ids or link["lineId"] not in line_ids or link["wordId"] not in words_by_id:
            raise RuntimeError(f"invalid content_line_words foreign key: {link['_id']}")
        line = next(row for row in lines if row["_id"] == link["lineId"])
        for position in link["positions"]:
            if line["text"][position["start"]:position["end"]] == "":
                raise RuntimeError(f"empty match position: {link['_id']}")
    for membership in memberships:
        if membership["sourceStats"]["primaryLineId"] not in line_ids:
            raise RuntimeError(f"missing primary content line: {membership['_id']}")


def build_report(topics, lines, links, learning):
    relation_path = OUT_DIR / "word_relations.json"
    group_path = OUT_DIR / "word_relation_groups.json"
    relation_count = len(load_jsonl(relation_path)) if relation_path.exists() else 0
    group_count = len(load_jsonl(group_path)) if group_path.exists() else 0
    translated = sum(bool(row["translationZh"]) for row in lines)
    machine_translated = sum(row.get("translationStatus") == "machine_translated_pending_human_review" for row in lines)
    second_pass = sum(row.get("translationStatus") == "ai_second_pass_pending_human_review" for row in lines)
    editorial_translated = sum(row.get("translationStatus") == "draft_human_review" for row in lines)
    editorial = sum(row["status"] == "draft_editorial" for row in learning)
    return f"""# 雅思真题语境词书内容集合导入说明

## 文件

- `content_topics.json`：{len(topics):,} 条，JSONL。
- `content_lines.json`：{len(lines):,} 条，JSONL。
- `content_line_words.json`：{len(links):,} 条，JSONL。
- `word_learning_content.json`：{len(learning):,} 条，JSONL。
- `word_relations.json`：{relation_count:,} 条，JSONL。
- `word_relation_groups.json`：{group_count:,} 条，JSONL。
- `translation_review_queue.json`：机器译文的重点人工复核队列。

## 当前状态

- 已有中文翻译：{translated:,} / {len(lines):,}。
- 待机器翻译：{len(lines) - translated:,} 条。
- 机器翻译待人工复核：{machine_translated:,} 条。
- AI 二次校订待人工复核：{second_pass:,} 条。
- 第一篇编辑译文待人工复核：{editorial_translated:,} 条。
- 完整编辑学习内容：{editorial:,} 条（第一篇命中词）。
- 词典基线学习内容：{len(learning) - editorial:,} 条；未生成不可靠的正文窗口搭配。

## 约束

- 所有 `content_line_words` 均满足 `_id = lineId:wordId`，重复词位置聚合进 `positions[]`。
- 所有 `word_learning_content._id = wordId`，与新词书的 1,352 条关联一一对应。
- 所有 `wordbook_words.sourceStats.primaryLineId` 均存在于 `content_lines`。
- 未把机器生成或未审核内容标记为 `reviewed/published`。
"""


def main():
    articles = BOOK_BUILDER.extract_articles(BOOK_BUILDER.extract_pdf_lines())
    words = load_jsonl(WORDS_PATH)
    words_by_id = {row["_id"]: row for row in words}
    membership = load_jsonl(MEMBERSHIP_PATH)
    membership_ids = {row["wordId"] for row in membership}
    words_by_normalized = {
        MATCHER.normalize(row.get("normalized") or row.get("word") or ""): row
        for row in words if row["_id"] in membership_ids
    }
    topics, lines, links, lines_by_id, word_links = build_content(articles, words_by_normalized)
    learning = build_learning(membership, words_by_id, word_links, lines_by_id)
    validate(topics, lines, links, learning, membership, words_by_id)
    write_jsonl(OUT_DIR / "content_topics.json", topics)
    write_jsonl(OUT_DIR / "content_lines.json", lines)
    write_jsonl(OUT_DIR / "content_line_words.json", links)
    write_jsonl(OUT_DIR / "word_learning_content.json", learning)
    REPORT_PATH.write_text(build_report(topics, lines, links, learning), encoding="utf-8")
    print(json.dumps({
        "content_topics": len(topics), "content_lines": len(lines),
        "content_line_words": len(links), "word_learning_content": len(learning),
        "translatedLines": sum(bool(row["translationZh"]) for row in lines),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
