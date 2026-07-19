#!/usr/bin/env python3
"""Build wordbook_words for the IELTS authentic reading-context wordbook."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PDF = Path("/Users/chengtingwei/Downloads/IELTS-Reading-Actual-Tests-2016-2017.pdf")
IELTS_WORDBOOK = ROOT / "miniprogram/assets/data/wordbooks/ielts.json"
WORDS_IMPORT = ROOT / "tmp/import_ready/words.import.json"
OUT_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
REPORT_PATH = ROOT / "docs/IELTS真题语境词书-wordbook_words导入说明.md"
BOOK_ID = "ielts_content_words"

MATCHER_SPEC = importlib.util.spec_from_file_location(
    "matcher", ROOT / "scripts/match_pdf_to_ielts_wordbook.py"
)
MATCHER = importlib.util.module_from_spec(MATCHER_SPEC)
assert MATCHER_SPEC.loader
MATCHER_SPEC.loader.exec_module(MATCHER)

# Ordered exactly as the 10 tests x 3 sections appear in the PDF.
TOPICS = [
    (1, 1, "Ants Could Teach Ants", "ants"),
    (1, 2, "Wealth in a cold climate", "cold_climate"),
    (1, 3, "Compliance or Noncompliance for children", "child_compliance"),
    (2, 1, "Plant Scents", "plant_scents"),
    (2, 2, "The Development of Plastics", "plastics"),
    (2, 3, "Global Warming in New Zealand", "nz_global_warming"),
    (3, 1, "Grey Workers", "grey_workers"),
    (3, 2, "The history of salt", "salt"),
    (3, 3, "Designed to Last", "designed_to_last"),
    (4, 1, "William Gilbert and Magnetism", "gilbert_magnetism"),
    (4, 2, "Seed Hunting", "seed_hunting"),
    (4, 3, "The Power of Nothing", "placebo"),
    (5, 1, "Going Bananas", "bananas"),
    (5, 2, "Computer Provides More Questions Than Answers", "antikythera"),
    (5, 3, "Save Endangered Language", "endangered_language"),
    (6, 1, "Eco-Resort Management Practices", "eco_resort"),
    (6, 2, "TV Addiction", "tv_addiction"),
    (6, 3, "Music: Language We All Speak", "music_language"),
    (7, 1, "California’s age of Megafires", "megafires"),
    (7, 2, "European Heat Wave", "heat_wave"),
    (7, 3, "The concept of childhood in the western countries", "childhood"),
    (8, 1, "Natural Pesticide in India", "natural_pesticide"),
    (8, 2, "Numeracy: Can animals tell numbers?", "animal_numeracy"),
    (8, 3, "Multitasking Debate", "multitasking"),
    (9, 1, "Organic farming and chemical fertilisers", "organic_farming"),
    (9, 2, "The Pearl", "pearl"),
    (9, 3, "Scent of success", "scent_success"),
    (10, 1, "Coastal Archaeology of Britain", "coastal_archaeology"),
    (10, 2, "Activities for Children", "children_activities"),
    (10, 3, "Mechanisms of Linguistic Change", "linguistic_change"),
]

BOOK = {
    "_id": BOOK_ID,
    "name": "雅思真题语境词汇",
    "category": "exam",
    "language": "en",
    "cefrLevel": "B1-C1",
    "description": "词汇来自雅思阅读、听力、写作及口语语料，并提供真实出处和语境例句",
    "cover": {
        "letter": "C",
        "color": "#234E52",
        "image": "https://word-content-assets-1411800061.cos.ap-guangzhou.myqcloud.com/covers/wordbooks/ielts_content_words.png",
    },
    "totalWords": 0,
    "status": "draft",
    "version": 1,
    "schemaVersion": 1,
    "contentVersion": 1,
    "source": {
        "name": "IELTS Authentic Content",
        "types": ["reading", "listening", "writing", "speaking"],
        "importedAt": None,
    },
    "createdAt": None,
    "updatedAt": None,
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def extract_pdf_lines() -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-layout", str(PDF), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def section_ranges(lines: list[str]) -> list[tuple[int, int]]:
    starts = [index for index, line in enumerate(lines) if re.match(r"^SECTION\s+[123]\s*$", line.strip())]
    if len(starts) != 30:
        raise RuntimeError(f"expected 30 reading sections, found {len(starts)}")
    return [(start, starts[index + 1] if index + 1 < len(starts) else len(lines)) for index, start in enumerate(starts)]


def clean_body(lines: list[str]) -> str:
    kept = []
    for raw in lines:
        value = raw.strip().replace("\f", "")
        if (not value or re.fullmatch(r"[A-J]", value)
                or re.fullmatch(r"\d+\s*\|\s*P\s*a\s*g\s*e", value, flags=re.I)):
            continue
        value = re.sub(r"^[A-J]\s+(?=[A-Z\"“])", "", value)
        kept.append(value)
    text = " ".join(kept)
    text = text.replace("，", ",").replace("一", "-")
    text = text.replace("presence .Sounding", "presence. Sounding")
    return re.sub(r"\s+", " ", text).strip()


def extract_articles(lines: list[str]) -> list[dict]:
    articles = []
    for topic, (start, end) in zip(TOPICS, section_ranges(lines)):
        test, section, title, line_prefix = topic
        chunk = lines[start:end]
        title_index = next((index for index, line in enumerate(chunk) if line.strip() == title), None)
        if title_index is None:
            raise RuntimeError(f"title not found in section: {title}")
        question_index = next(
            (index for index in range(title_index + 1, len(chunk)) if re.match(r"^Questions?\s+\d", chunk[index].strip(), re.I)),
            None,
        )
        if question_index is None:
            raise RuntimeError(f"question boundary not found: {title}")
        body = clean_body(chunk[title_index + 1:question_index])
        if len(body) < 500:
            raise RuntimeError(f"article body unexpectedly short ({len(body)} chars): {title}")
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        articles.append({
            "test": test,
            "section": section,
            "title": title,
            "topicId": f"ielts-reading-{slug}",
            "linePrefix": line_prefix,
            "body": body,
        })
    return articles


def split_sentences(text: str) -> list[str]:
    # Keep the ordinal stable: every sentence in the article counts, whether or not it has a match.
    parts = re.split(r"(?<=[.!?])(?:[”’\"])?\s+(?=[“\"A-Z0-9])", text)
    return [part.strip() for part in parts if part.strip()]


def line_id(article: dict, sentence_index: int) -> str:
    return f"line_{article['linePrefix']}_{sentence_index:02d}"


def should_skip_proper_noun(raw: str, token_index: int, key: str, surface: str) -> bool:
    # Prevent names and named-entity terms such as Franks, Curry and Storey from
    # entering the vocabulary. Sentence-initial capitalisation remains valid.
    return token_index > 0 and raw[:1].isupper()


def build_memberships(articles: list[dict], words_by_normalized: dict[str, dict], phrases: set[str]) -> list[dict]:
    stats = defaultdict(lambda: {
        "occurrenceCount": 0,
        "topicIds": set(),
        "firstArticle": None,
        "firstTopicId": None,
        "primaryLineId": None,
        "firstSeen": None,
    })
    single_words = set(words_by_normalized) - phrases
    sequence = 0

    for article_index, article in enumerate(articles):
        for sentence_index, sentence in enumerate(split_sentences(article["body"]), 1):
            raw_tokens = MATCHER.WORD_RE.findall(sentence)
            normalized_tokens = [MATCHER.normalize(token) for token in raw_tokens]
            normalized_sentence = " ".join(normalized_tokens)

            for phrase in phrases:
                count = len(re.findall(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", normalized_sentence))
                if not count:
                    continue
                entry = stats[phrase]
                if entry["firstSeen"] is None:
                    sequence += 1
                    entry["firstSeen"] = sequence
                    entry["firstArticle"] = article["title"]
                    entry["firstTopicId"] = article["topicId"]
                    entry["primaryLineId"] = line_id(article, sentence_index)
                entry["occurrenceCount"] += count
                entry["topicIds"].add(article["topicId"])

            for token_index, (raw, surface) in enumerate(zip(raw_tokens, normalized_tokens)):
                key = surface if surface in single_words else next(
                    (candidate for candidate in MATCHER.lemma_candidates(surface) if candidate in single_words),
                    None,
                )
                if key is None or should_skip_proper_noun(raw, token_index, key, surface):
                    continue
                entry = stats[key]
                if entry["firstSeen"] is None:
                    sequence += 1
                    entry["firstSeen"] = sequence
                    entry["firstArticle"] = article["title"]
                    entry["firstTopicId"] = article["topicId"]
                    entry["primaryLineId"] = line_id(article, sentence_index)
                entry["occurrenceCount"] += 1
                entry["topicIds"].add(article["topicId"])

    rows = []
    ordered = sorted(stats.items(), key=lambda pair: pair[1]["firstSeen"])
    for order, (normalized, data) in enumerate(ordered, 1):
        word = words_by_normalized[normalized]
        word_id = word["_id"]
        rows.append({
            "_id": f"{BOOK_ID}:{word_id}",
            "bookId": BOOK_ID,
            "wordId": word_id,
            "word": word["word"],
            "normalized": normalized,
            "order": order,
            "chapter": data["firstArticle"],
            "important": bool(word.get("important")),
            "bookSenseOverride": None,
            "sourceStats": {
                "occurrenceCount": data["occurrenceCount"],
                "articleCount": len(data["topicIds"]),
                "firstTopicId": data["firstTopicId"],
                "primaryLineId": data["primaryLineId"],
            },
            "createdAt": None,
            "updatedAt": None,
        })
    return rows


def validate(rows: list[dict], articles: list[dict], valid_word_ids: set[str]) -> None:
    ids = [row["_id"] for row in rows]
    orders = [row["order"] for row in rows]
    topic_ids = {article["topicId"] for article in articles}
    titles = {article["title"] for article in articles}
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate wordbook_words _id")
    if orders != list(range(1, len(rows) + 1)):
        raise RuntimeError("orders are not contiguous")
    for row in rows:
        if row["wordId"] not in valid_word_ids:
            raise RuntimeError(f"missing words foreign key: {row['wordId']}")
        if row["_id"] != f"{row['bookId']}:{row['wordId']}":
            raise RuntimeError(f"invalid membership _id: {row['_id']}")
        if row["chapter"] not in titles:
            raise RuntimeError(f"unknown chapter: {row['chapter']}")
        stats = row["sourceStats"]
        if stats["firstTopicId"] not in topic_ids or stats["articleCount"] < 1 or stats["occurrenceCount"] < 1:
            raise RuntimeError(f"invalid sourceStats: {row['_id']}")
        if not stats["primaryLineId"].startswith("line_"):
            raise RuntimeError(f"invalid primaryLineId: {row['_id']}")


def build_report(rows: list[dict], articles: list[dict]) -> str:
    important = sum(row["important"] for row in rows)
    occurrences = sum(row["sourceStats"]["occurrenceCount"] for row in rows)
    multi_article = sum(row["sourceStats"]["articleCount"] > 1 for row in rows)
    chapter_counts = defaultdict(int)
    for row in rows:
        chapter_counts[row["chapter"]] += 1
    out = [
        "# 雅思真题语境词书 wordbook_words 导入说明",
        "",
        "## 产物",
        "",
        "- `tmp/cloud_import_ielts_content_words/wordbooks.json`：更新 `totalWords` 后的词书文档（JSONL）。",
        "- `tmp/cloud_import_ielts_content_words/wordbook_words.json`：词书与单词关联记录（JSONL，每行一条）。",
        "- `tmp/cloud_import_ielts_content_words/wordbook_words.pretty.json`：同一批记录的格式化 JSON 数组，便于检查。",
        "- `tmp/cloud_import_ielts_content_words/articles.json`：30 篇正文的 title、topicId 与句子 ID 前缀映射。",
        "",
        "## 统计",
        "",
        f"- 词书 ID：`{BOOK_ID}`",
        f"- 阅读文章：{len(articles)} 篇",
        f"- 独立词条：{len(rows):,} 条",
        f"- important：{important:,} 条",
        f"- 正文累计命中：{occurrences:,} 次",
        f"- 出现在多篇文章中的词：{multi_article:,} 条",
        "",
        "## 口径",
        "",
        "- 只匹配 30 篇 Reading Passage 正文，不统计目录、题目、选项、答案和页眉页脚。",
        "- 精确匹配忽略大小写；常见复数、过去式和现在分词采用保守词形还原。",
        "- 句中大写专名匹配会被排除，例如 `Franks`、`Curry`、`Storey` 不会误算成普通词条。",
        "- `order` 按词条首次在正文出现的顺序生成；`chapter` 为首次出现的文章标题。",
        "- `important` 继承现有 IELTS 词库；`bookSenseOverride` 显式写入 `null`。",
        "- `primaryLineId` 使用对应文章的句子顺序，可与后续 `content_lines` 导入保持一致。",
        "",
        "## 首次出处分布",
        "",
        "| Test | Passage | 文章 | topicId | 首次出现词条 |",
        "|---:|---:|---|---|---:|",
    ]
    for article in articles:
        out.append(
            f"| {article['test']} | {article['section']} | {article['title']} | "
            f"`{article['topicId']}` | {chapter_counts[article['title']]:,} |"
        )
    out.extend(["", "## 样例", "", "```json", json.dumps(rows[0], ensure_ascii=False, indent=2), "```", ""])
    return "\n".join(out)


def main() -> None:
    ielts_payload = json.loads(IELTS_WORDBOOK.read_text(encoding="utf-8"))
    important_by_normalized = {
        MATCHER.normalize(row["word"]): bool(row.get("important")) for row in ielts_payload["words"]
    }
    cloud_words = load_jsonl(WORDS_IMPORT)
    words_by_normalized = {}
    for row in cloud_words:
        normalized = MATCHER.normalize(row.get("normalized") or row.get("word") or "")
        if normalized not in important_by_normalized:
            continue
        words_by_normalized[normalized] = {
            "_id": row["_id"],
            "word": row.get("word") or normalized,
            "important": important_by_normalized[normalized],
        }
    phrases = {normalized for normalized in words_by_normalized if " " in normalized}
    articles = extract_articles(extract_pdf_lines())
    rows = build_memberships(articles, words_by_normalized, phrases)
    validate(rows, articles, {row["_id"] for row in cloud_words})

    book = dict(BOOK)
    book["totalWords"] = len(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT_DIR / "wordbooks.json", [book])
    write_jsonl(OUT_DIR / "wordbook_words.json", rows)
    (OUT_DIR / "wordbook_words.pretty.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    article_rows = [{key: article[key] for key in ("test", "section", "title", "topicId", "linePrefix")} for article in articles]
    (OUT_DIR / "articles.json").write_text(
        json.dumps(article_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(build_report(rows, articles), encoding="utf-8")
    print(json.dumps({
        "articles": len(articles),
        "totalWords": len(rows),
        "important": sum(row["important"] for row in rows),
        "occurrences": sum(row["sourceStats"]["occurrenceCount"] for row in rows),
        "output": str(OUT_DIR),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
