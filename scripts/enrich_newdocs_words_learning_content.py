#!/usr/bin/env python3
"""Enrich newdocs-added IELTS words with draft usage and morphology content."""

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
WORDBOOK_PATH = DATA_DIR / "wordbook_words.json"
LINES_PATH = DATA_DIR / "content_lines.json"
LINKS_PATH = DATA_DIR / "content_line_words.json"
REPORT_PATH = DATA_DIR / "newdocs_learning_enrichment_report.json"

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "at", "for", "with",
    "from", "by", "as", "is", "are", "was", "were", "be", "been", "being", "that", "this",
    "these", "those", "it", "its", "their", "his", "her", "our", "your", "they", "he", "she",
    "we", "you", "i", "not", "can", "could", "would", "should", "may", "might", "will",
}

PREFIXES = [
    ("micro", "prefix", "微小；百万分之一", "Greek"),
    ("macro", "prefix", "宏观；大型", "Greek"),
    ("inter", "prefix", "在……之间；相互", "Latin"),
    ("intra", "prefix", "在……内部", "Latin"),
    ("trans", "prefix", "跨越；转变", "Latin"),
    ("super", "prefix", "在上；超越", "Latin"),
    ("under", "prefix", "在下；不足", "Old English"),
    ("over", "prefix", "过度；在上", "Old English"),
    ("anti", "prefix", "反对；抗", "Greek"),
    ("auto", "prefix", "自己；自动", "Greek"),
    ("bio", "prefix", "生命；生物", "Greek"),
    ("geo", "prefix", "地球；土地", "Greek"),
    ("photo", "prefix", "光；照片", "Greek"),
    ("tele", "prefix", "远距离", "Greek"),
    ("multi", "prefix", "多；多个", "Latin"),
    ("semi", "prefix", "半；部分", "Latin"),
    ("non", "prefix", "不；非", "Latin"),
    ("sub", "prefix", "在下；次级", "Latin"),
    ("pre", "prefix", "在前；预先", "Latin"),
    ("post", "prefix", "在后；后期", "Latin"),
    ("pro", "prefix", "向前；支持", "Latin"),
    ("re", "prefix", "再；重新；回", "Latin"),
    ("de", "prefix", "向下；去除；反向", "Latin"),
    ("dis", "prefix", "分开；否定；相反", "Latin"),
    ("en", "prefix", "使成为；进入", "French/Latin"),
    ("ex", "prefix", "向外；以前的", "Latin"),
    ("un", "prefix", "不；反向", "Old English"),
    ("in", "prefix", "不；进入", "Latin"),
    ("im", "prefix", "不；进入", "Latin"),
]

SUFFIXES = [
    ("ization", "suffix", "……化；过程", "Greek/Latin"),
    ("isation", "suffix", "……化；过程", "Greek/Latin"),
    ("tion", "suffix", "行为、过程或结果", "Latin"),
    ("sion", "suffix", "行为、过程或结果", "Latin"),
    ("ment", "suffix", "行为、结果或状态", "Latin/French"),
    ("ness", "suffix", "性质；状态", "Old English"),
    ("ity", "suffix", "性质；状态", "Latin"),
    ("ance", "suffix", "行为；状态；性质", "Latin/French"),
    ("ence", "suffix", "行为；状态；性质", "Latin/French"),
    ("able", "suffix", "能够……的；适合……的", "Latin"),
    ("ible", "suffix", "能够……的；可……的", "Latin"),
    ("less", "suffix", "没有……的", "Old English"),
    ("ful", "suffix", "充满……的", "Old English"),
    ("ous", "suffix", "具有……性质的", "Latin"),
    ("ive", "suffix", "有……倾向的；……性质的", "Latin"),
    ("al", "suffix", "……的；与……有关的", "Latin"),
    ("ic", "suffix", "……的；与……有关的", "Greek/Latin"),
    ("ical", "suffix", "……的；与……有关的", "Greek/Latin"),
    ("ize", "suffix", "使……化", "Greek"),
    ("ise", "suffix", "使……化", "Greek"),
    ("ify", "suffix", "使成为；使……化", "Latin"),
    ("ate", "suffix", "使……；成为", "Latin"),
    ("er", "suffix", "做……的人或物", "Old English"),
    ("or", "suffix", "做……的人或物", "Latin"),
    ("ist", "suffix", "从事……的人；信奉者", "Greek"),
    ("ism", "suffix", "主义；制度；现象", "Greek"),
]

POS_LABEL = {
    "n": "noun",
    "v": "verb",
    "a": "adjective",
    "adj": "adjective",
    "adv": "adverb",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def first_sense(word: dict[str, Any]) -> dict[str, Any]:
    senses = word.get("senses") or []
    return senses[0] if senses else {}


def normalize_pos(pos: str) -> str:
    value = str(pos or "").lower().strip()
    if value in {"adj", "a"}:
        return "a"
    if value in {"vt", "vi"}:
        return "v"
    return value


def token_windows(line: str, start: int, end: int) -> tuple[list[str], list[str]]:
    before = TOKEN_RE.findall(line[:start])
    after = TOKEN_RE.findall(line[end:])
    return before[-3:], after[:3]


def clean_phrase(words: list[str]) -> str:
    return " ".join(word.strip(" ,.;:()[]{}\"“”'").lower() for word in words if word.strip(" ,.;:()[]{}\"“”'"))


def phrase_score(phrase: str, target: str) -> int:
    tokens = phrase.split()
    if len(tokens) < 2 or len(tokens) > 5:
        return -10
    if target not in tokens:
        return -10
    content = [token for token in tokens if token not in STOPWORDS]
    return len(content) * 2 + min(len(tokens), 4)


def collocation_candidates(word: str, pos: str, occurrences: list[tuple[dict[str, Any], dict[str, Any]]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    target = word.lower()
    for line, link in occurrences:
        for position in link.get("positions") or []:
            left, right = token_windows(line.get("text") or "", position.get("start", 0), position.get("end", 0))
            surface = (line.get("text") or "")[position.get("start", 0):position.get("end", 0)].lower() or target
            options = [
                clean_phrase(left[-1:] + [surface] + right[:1]),
                clean_phrase(left[-2:] + [surface]),
                clean_phrase([surface] + right[:2]),
                clean_phrase(left[-1:] + [surface] + right[:2]),
            ]
            for phrase in options:
                if phrase_score(phrase, target) > 0:
                    counts[phrase] += phrase_score(phrase, target)

    items = []
    for phrase, _ in counts.most_common(5):
        items.append({
            "text": phrase,
            "translationZh": "",
            "sourceType": "newdocs_corpus_candidate",
            "status": "draft",
            "reviewStatus": "auto_enriched_pending_review",
        })
    return items


def grammar_patterns(word: str, pos: str, example_line: str) -> list[dict[str, Any]]:
    if pos == "v":
        pattern = f"{word} + object / complement"
    elif pos == "n":
        pattern = f"{word} + of / in / for + noun"
    elif pos == "a":
        pattern = f"be / become + {word}; {word} + noun"
    elif pos == "adv":
        pattern = f"{word} + verb / adjective"
    else:
        return []
    return [{
        "pattern": pattern,
        "exampleEn": example_line,
        "exampleZh": "",
        "sourceType": "newdocs_corpus_candidate",
        "status": "draft",
        "reviewStatus": "auto_enriched_pending_review",
    }]


def morphology(word: str, translation: str) -> dict[str, Any] | None:
    if " " in word or "-" in word:
        return {
            "segments": [{"form": word, "type": "phrase", "meaningZh": translation, "noteZh": "短语按整体表达学习。"}],
            "explanationZh": f"{word} 是短语表达，当前按整体语义学习。",
            "relatedWords": [],
        }

    lower = word.lower()
    prefix = next((item for item in PREFIXES if lower.startswith(item[0]) and len(lower) - len(item[0]) >= 4), None)
    suffix = next((item for item in SUFFIXES if lower.endswith(item[0]) and len(lower) - len(item[0]) >= 4), None)
    if not prefix and not suffix:
        return None

    segments = []
    stem_start = 0
    stem_end = len(lower)
    if prefix:
        form, typ, meaning, origin = prefix
        segments.append({"form": form + "-", "type": typ, "meaningZh": meaning, "origin": origin})
        stem_start = len(form)
    if suffix:
        form, typ, meaning, origin = suffix
        stem_end = len(lower) - len(form)
    root = lower[stem_start:stem_end]
    if root:
        segments.append({"form": root, "type": "base/root", "meaningZh": translation, "noteZh": "此处按词干或核心部分辅助记忆，不强行等同严格词源。"})
    if suffix:
        form, typ, meaning, origin = suffix
        segments.append({"form": "-" + form, "type": typ, "meaningZh": meaning, "origin": origin})
    return {
        "segments": segments,
        "explanationZh": f"{word} 可按 {' + '.join(seg['form'] for seg in segments)} 辅助记忆；具体词源仍需人工复核。",
        "relatedWords": [],
    }


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    words_by_id = {row["_id"]: row for row in words}
    wordbook = read_jsonl(WORDBOOK_PATH)
    new_word_ids = {row["wordId"] for row in wordbook if (row.get("order") or 0) > 1352}
    lines_by_id = {row["_id"]: row for row in read_jsonl(LINES_PATH)}
    links_by_word: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for link in read_jsonl(LINKS_PATH):
        if link.get("wordId") in new_word_ids:
            links_by_word[link["wordId"]].append(link)

    learning_rows = read_jsonl(LEARNING_PATH)
    updated = {"collocations": [], "grammarPatterns": [], "morphology": []}

    for row in learning_rows:
        word_id = row.get("wordId")
        if word_id not in new_word_ids:
            continue
        word_doc = words_by_id.get(word_id) or {}
        sense = first_sense(word_doc)
        word = normalize(row.get("normalized") or row.get("word") or word_doc.get("word") or "")
        pos = normalize_pos(sense.get("pos") or "")
        translation = str(sense.get("translation") or "").strip()
        occurrences = [(lines_by_id[link["lineId"]], link) for link in links_by_word.get(word_id, []) if link.get("lineId") in lines_by_id]
        example_line = occurrences[0][0].get("text") if occurrences else ""

        if not row.get("collocations"):
            candidates = collocation_candidates(word, pos, occurrences)
            if candidates:
                row["collocations"] = candidates
                updated["collocations"].append(word)
        if not row.get("grammarPatterns") and example_line:
            patterns = grammar_patterns(word, pos, example_line)
            if patterns:
                row["grammarPatterns"] = patterns
                updated["grammarPatterns"].append(word)
        current_morph = row.get("morphology") or {}
        kind = (current_morph.get("segments") or [{}])[0].get("type")
        if kind == "base":
            next_morph = morphology(word, translation)
            if next_morph:
                row["morphology"] = next_morph
                updated["morphology"].append(word)

    write_jsonl(LEARNING_PATH, learning_rows)
    report = {
        "newWordCount": len(new_word_ids),
        "updatedCounts": {key: len(value) for key, value in updated.items()},
        "updated": updated,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["updatedCounts"], ensure_ascii=False, indent=2))
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
