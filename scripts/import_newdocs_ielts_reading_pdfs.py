#!/usr/bin/env python3
"""Incrementally import standalone IELTS reading PDFs from Downloads/newdocs."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
PDF_DIR = Path("/Users/chengtingwei/Downloads/newdocs")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
REPORT_PATH = DATA_DIR / "newdocs_import_report.json"
BOOK_ID = "ielts_content_words"

MATCHER_SPEC = importlib.util.spec_from_file_location(
    "matcher", ROOT / "scripts/match_pdf_to_ielts_wordbook.py"
)
MATCHER = importlib.util.module_from_spec(MATCHER_SPEC)
assert MATCHER_SPEC.loader
MATCHER_SPEC.loader.exec_module(MATCHER)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def slugify(value: str) -> str:
    value = value.lower().replace("’", "'")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-") or "untitled"


def normalize_title(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def normalize_text(value: str) -> str:
    return " ".join(MATCHER.normalize(token) for token in MATCHER.WORD_RE.findall(value))


def read_pdf_text(path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.replace("\f", "\n")


def title_from_filename(path: Path) -> tuple[str, str, str]:
    stem = path.stem
    stem = re.sub(r"^\d+\.\s*", "", stem)
    passage = ""
    match = re.match(r"(P\d(?:\(.*?\))?)\s*-\s*(.+)", stem)
    if match:
        passage = match.group(1)
        stem = match.group(2)
    english = re.sub(r"[\u4e00-\u9fff].*$", "", stem).strip()
    english = english.replace("_", "?").strip(" -")
    zh = stem[len(english):].strip(" -") if english and stem.startswith(english) else ""
    return english or stem, zh, passage


def clean_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    return line


def is_noise(line: str) -> bool:
    if not line:
        return True
    patterns = [
        r"^READING PASSAGE\s+\d+",
        r"^You should spend about",
        r"^Reading Passage \d+",
        r"^Questions?\s+\d+",
        r"^Choose\b",
        r"^Write\b",
        r"^In boxes?\b",
        r"^TRUE\s+if\b",
        r"^FALSE\s+if\b",
        r"^NOT GIVEN\s+if\b",
        r"^Disclaimer$",
        r"^Compiled, formatted",
        r"^All copyright",
        r"^No affiliation",
        r"^For non-commercial",
        r"^Available free",
    ]
    return any(re.search(pattern, line, flags=re.I) for pattern in patterns)


def extract_body(path: Path) -> dict[str, Any]:
    title, title_zh, passage = title_from_filename(path)
    text = read_pdf_text(path)
    raw_lines = [clean_line(line) for line in text.splitlines()]
    lines = [line for line in raw_lines if line]

    title_norm = normalize_title(title)
    title_index = -1
    for index, line in enumerate(lines):
        if normalize_title(line) == title_norm:
            title_index = index
            break
    if title_index < 0:
        loose = title_norm.replace(" ", "")
        for index, line in enumerate(lines):
            if normalize_title(line).replace(" ", "") == loose:
                title_index = index
                break

    start = title_index + 1 if title_index >= 0 else 0
    body_lines: list[str] = []
    seen_body = False
    for line in lines[start:]:
        if re.match(r"^Questions?\s+\d+", line, flags=re.I) and seen_body:
            break
        if re.match(r"^Disclaimer$", line, flags=re.I):
            break
        if is_noise(line):
            continue
        if re.fullmatch(r"[A-Z]", line):
            continue
        # Keep paragraph letters by removing the marker.
        line = re.sub(r"^([A-H])\s+", "", line)
        if len(MATCHER.WORD_RE.findall(line)) < 3:
            continue
        seen_body = True
        body_lines.append(line)

    body = " ".join(body_lines)
    body = re.sub(r"\s+", " ", body).strip()
    return {"title": title, "titleZh": title_zh, "passage": passage, "body": body, "sourceFile": path.name}


def split_sentences(body: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'])", body)
    sentences = [piece.strip() for piece in pieces if len(MATCHER.WORD_RE.findall(piece)) >= 5]
    return sentences


def match_line(sentence: str, topic_id: str, line_id: str, words_by_normalized: dict[str, dict[str, Any]], phrases: set[str]):
    hits: dict[str, dict[str, Any]] = defaultdict(lambda: {"positions": [], "surfaces": [], "modes": set()})
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
            (candidate for candidate in MATCHER.lemma_candidates(surface) if candidate in single),
            None,
        )
        if key is None or should_skip_proper_noun(raw, token_index, key, surface):
            continue
        hits[key]["positions"].append({"start": match.start(), "end": match.end()})
        hits[key]["surfaces"].append(raw)
        hits[key]["modes"].add("exact" if key == surface else "lemma")

    links = []
    for normalized, data in hits.items():
        word = words_by_normalized[normalized]
        links.append({
            "_id": f"{line_id}:{word['_id']}",
            "topicId": topic_id,
            "lineId": line_id,
            "wordId": word["_id"],
            "normalized": normalized,
            "surface": data["surfaces"][0],
            "positions": data["positions"],
            "matchType": "+".join(sorted(data["modes"])),
            "createdAt": None,
        })
    return links


def should_skip_proper_noun(raw: str, token_index: int, key: str, surface: str) -> bool:
    if token_index == 0 or not raw[:1].isupper() or surface == key:
        return False
    # Reuse the conservative idea from the existing importer: avoid matching
    # sentence-internal names as common lower-case words.
    return key in {"brown", "black", "white", "charles", "alexis", "mark", "will"}


def first_translation(word: dict[str, Any]) -> str:
    senses = word.get("senses") or []
    return str((senses[0] if senses else {}).get("translation") or "").strip()


def baseline_learning(word: dict[str, Any], membership: dict[str, Any], topic_ids: list[str]) -> dict[str, Any]:
    normalized = membership["normalized"]
    translation = first_translation(word)
    return {
        "_id": word["_id"],
        "wordId": word["_id"],
        "word": word.get("word") or normalized,
        "normalized": normalized,
        "primaryLineId": membership["sourceStats"]["primaryLineId"],
        "preferredTopicIds": topic_ids[:5],
        "morphology": {
            "segments": [{
                "form": normalized,
                "type": "base",
                "meaningZh": translation,
                "noteZh": "当前仅建立整体词基线；构词分析待词典编辑审核。",
            }],
            "explanationZh": f"{normalized} 当前按整体词学习，不自动推断词根词缀。",
            "relatedWords": [],
        },
        "collocations": [],
        "grammarPatterns": [],
        "commonErrors": [],
        "examProfile": {
            "skills": ["reading"],
            "topics": topic_ids,
            "priority": 4 if membership.get("important") else 3,
            "writingValue": 3 if membership.get("important") else 2,
        },
        "sourceStats": membership["sourceStats"],
        "provenance": {
            "dictionarySources": ["words", "ECDICT"],
            "corpusSource": "Standalone IELTS reading PDFs",
            "generationMethod": "dictionary_baseline",
            "reviewStatus": "pending_human_review",
        },
        "status": "draft",
        "contentStage": "generated_baseline",
        "createdAt": None,
        "updatedAt": None,
    }


def load_important_words() -> set[str]:
    path = ROOT / "miniprogram/assets/data/wordbooks/ielts.json"
    if not path.exists():
        return set()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {MATCHER.normalize(row["word"]) for row in payload.get("words", []) if row.get("important")}


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    words = read_jsonl(WORDS_PATH)
    words_by_id = {row["_id"]: row for row in words}
    words_by_normalized = {
        MATCHER.normalize(row.get("normalized") or row.get("word") or ""): row
        for row in words
    }
    phrases = {value for value in words_by_normalized if " " in value}
    important_norms = load_important_words()

    topics = read_jsonl(DATA_DIR / "content_topics.json")
    lines = read_jsonl(DATA_DIR / "content_lines.json")
    links = read_jsonl(DATA_DIR / "content_line_words.json")
    memberships = read_jsonl(DATA_DIR / "wordbook_words.json")
    learning = read_jsonl(DATA_DIR / "word_learning_content.json")

    existing_title_norms = {normalize_title(row.get("name") or "") for row in topics}
    line_ids = {row["_id"] for row in lines}
    link_ids = {row["_id"] for row in links}
    membership_by_word = {row["wordId"]: row for row in memberships}
    learning_by_word = {row["wordId"]: row for row in learning}
    order_next = max([row.get("order") or 0 for row in memberships] or [0]) + 1

    word_topic_ids: dict[str, list[str]] = defaultdict(list)
    word_occurrences = Counter()
    for link in links:
        word_occurrences[link["wordId"]] += len(link.get("positions") or [1])
        if link["topicId"] not in word_topic_ids[link["wordId"]]:
            word_topic_ids[link["wordId"]].append(link["topicId"])

    report = {
        "sourceDir": str(PDF_DIR),
        "pdfCount": 0,
        "addedTopics": [],
        "skippedExistingTopics": [],
        "lowTextPdfs": [],
        "addedLines": 0,
        "addedLinks": 0,
        "newWordbookWords": [],
        "updatedWordbookWords": 0,
    }

    for pdf in sorted(PDF_DIR.glob("*.pdf"), key=lambda p: p.name):
        report["pdfCount"] += 1
        article = extract_body(pdf)
        title_norm = normalize_title(article["title"])
        if title_norm in existing_title_norms:
            report["skippedExistingTopics"].append({"file": pdf.name, "title": article["title"]})
            continue
        sentences = split_sentences(article["body"])
        if len(sentences) < 3:
            report["lowTextPdfs"].append({"file": pdf.name, "title": article["title"], "sentenceCount": len(sentences)})
            continue

        topic_id = f"ielts-reading-newdocs-{slugify(article['title'])}"
        base_topic_id = topic_id
        suffix = 2
        while any(row["_id"] == topic_id for row in topics):
            topic_id = f"{base_topic_id}-{suffix}"
            suffix += 1
        prefix = slugify(article["title"]).replace("-", "_")[:48]

        topic_links = []
        matched_line_count = 0
        for index, sentence in enumerate(sentences, 1):
            line_id = f"line_newdocs_{prefix}_{index:02d}"
            if line_id in line_ids:
                continue
            matched = match_line(sentence, topic_id, line_id, words_by_normalized, phrases)
            line = {
                "_id": line_id,
                "topicId": topic_id,
                "articleTitle": article["title"],
                "text": sentence,
                "normalizedText": normalize_text(sentence),
                "translationZh": "",
                "translationStatus": "pending_machine_translation",
                "speaker": {"name": "Narrator", "type": "narrator"},
                "scene": {
                    "section": article["passage"] or "Standalone Reading Passage",
                    "season": "newdocs",
                    "episode": article["sourceFile"],
                    "timestampMs": None,
                },
                "source": {
                    "name": "Standalone IELTS Reading PDF Collection",
                    "sourceFile": article["sourceFile"],
                    "locator": f"{article['title']}#sentence-{index:02d}",
                    "sourceUrl": "",
                },
                "tokenCount": len(MATCHER.WORD_RE.findall(sentence)),
                "matchedWordCount": len(matched),
                "status": "draft",
                "createdAt": None,
                "updatedAt": None,
            }
            lines.append(line)
            line_ids.add(line_id)
            report["addedLines"] += 1
            if matched:
                matched_line_count += 1
            for link in matched:
                if link["_id"] in link_ids:
                    continue
                links.append(link)
                link_ids.add(link["_id"])
                topic_links.append(link)
                report["addedLinks"] += 1
                word_id = link["wordId"]
                word_occurrences[word_id] += len(link.get("positions") or [1])
                if topic_id not in word_topic_ids[word_id]:
                    word_topic_ids[word_id].append(topic_id)

        topics.append({
            "_id": topic_id,
            "name": article["title"],
            "nameZh": article["titleZh"],
            "type": "ielts_reading",
            "description": f"Standalone IELTS Reading {article['passage']}".strip(),
            "language": "en",
            "cover": {"image": "", "color": "#234E52"},
            "status": "draft",
            "source": {
                "name": "Standalone IELTS Reading PDF Collection",
                "sourceFile": article["sourceFile"],
                "licenseNote": "For learning use. Verify publication rights before commercial release.",
            },
            "meta": {"sourceBatch": "newdocs", "passage": article["passage"], "titleZh": article["titleZh"]},
            "stats": {
                "lineCount": len(sentences),
                "audioCount": 0,
                "matchedLineCount": matched_line_count,
                "wordLinkCount": len(topic_links),
                "uniqueWordCount": len({link["wordId"] for link in topic_links}),
            },
            "createdAt": None,
            "updatedAt": None,
        })
        existing_title_norms.add(title_norm)
        report["addedTopics"].append({
            "file": pdf.name,
            "topicId": topic_id,
            "title": article["title"],
            "sentences": len(sentences),
            "wordLinks": len(topic_links),
            "uniqueWords": len({link["wordId"] for link in topic_links}),
        })

    first_link_by_word = {}
    for link in links:
        first_link_by_word.setdefault(link["wordId"], link)

    for word_id, topic_ids in sorted(word_topic_ids.items(), key=lambda item: (first_link_by_word[item[0]]["lineId"], item[0])):
        word = words_by_id.get(word_id)
        if not word:
            continue
        normalized = MATCHER.normalize(word.get("normalized") or word.get("word") or "")
        first_link = first_link_by_word[word_id]
        if word_id in membership_by_word:
            membership = membership_by_word[word_id]
            stats = membership.setdefault("sourceStats", {})
            before_topics = set(stats.get("topicIds") or [])
            stats["occurrenceCount"] = word_occurrences[word_id]
            stats["articleCount"] = len(topic_ids)
            stats["topicIds"] = topic_ids
            if not stats.get("firstTopicId"):
                stats["firstTopicId"] = first_link["topicId"]
            if not stats.get("primaryLineId"):
                stats["primaryLineId"] = first_link["lineId"]
            if set(topic_ids) != before_topics:
                report["updatedWordbookWords"] += 1
            if word_id in learning_by_word:
                learning_row = learning_by_word[word_id]
                learning_row["sourceStats"] = stats
                learning_row["preferredTopicIds"] = topic_ids[:5]
            continue

        membership = {
            "_id": f"{BOOK_ID}:{word_id}",
            "bookId": BOOK_ID,
            "wordId": word_id,
            "word": word.get("word") or normalized,
            "normalized": normalized,
            "order": order_next,
            "chapter": next((topic["name"] for topic in topics if topic["_id"] == first_link["topicId"]), ""),
            "important": normalized in important_norms,
            "bookSenseOverride": None,
            "sourceStats": {
                "occurrenceCount": word_occurrences[word_id],
                "articleCount": len(topic_ids),
                "firstTopicId": first_link["topicId"],
                "primaryLineId": first_link["lineId"],
                "topicIds": topic_ids,
            },
            "createdAt": None,
            "updatedAt": None,
        }
        order_next += 1
        memberships.append(membership)
        membership_by_word[word_id] = membership
        learning_row = baseline_learning(word, membership, topic_ids)
        learning.append(learning_row)
        learning_by_word[word_id] = learning_row
        report["newWordbookWords"].append({"word": membership["word"], "wordId": word_id, "order": membership["order"]})

    book_path = DATA_DIR / "wordbooks.json"
    books = read_jsonl(book_path)
    for book in books:
        if book.get("_id") == BOOK_ID:
            book["totalWords"] = len(memberships)
            book.setdefault("source", {}).setdefault("types", ["reading"])

    write_jsonl(DATA_DIR / "content_topics.json", topics)
    write_jsonl(DATA_DIR / "content_lines.json", lines)
    write_jsonl(DATA_DIR / "content_line_words.json", links)
    write_jsonl(DATA_DIR / "wordbook_words.json", sorted(memberships, key=lambda row: row.get("order") or 999999))
    write_jsonl(DATA_DIR / "word_learning_content.json", learning)
    if books:
        write_jsonl(book_path, books)

    report["totalTopics"] = len(topics)
    report["totalLines"] = len(lines)
    report["totalLinks"] = len(links)
    report["totalWordbookWords"] = len(memberships)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "pdfCount": report["pdfCount"],
        "addedTopics": len(report["addedTopics"]),
        "skippedExistingTopics": len(report["skippedExistingTopics"]),
        "lowTextPdfs": len(report["lowTextPdfs"]),
        "addedLines": report["addedLines"],
        "addedLinks": report["addedLinks"],
        "newWordbookWords": len(report["newWordbookWords"]),
        "updatedWordbookWords": report["updatedWordbookWords"],
        "totalTopics": report["totalTopics"],
        "totalLines": report["totalLines"],
        "totalLinks": report["totalLinks"],
        "totalWordbookWords": report["totalWordbookWords"],
        "report": str(REPORT_PATH),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
