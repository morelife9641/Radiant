#!/usr/bin/env python3
"""Auto-bind lexical suggestions to source word senses where possible."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
SUGGESTIONS_PATH = DATA_DIR / "word_lexical_suggestions.json"
REPORT_PATH = DATA_DIR / "auto_bound_lexical_suggestion_senses_report.json"


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
    "class": "n",
    "lesson": "n",
    "lecture": "n",
}


SOURCE_TARGET_OVERRIDES = {
    ("course", "class"): "course_n_study_01",
    ("course", "lesson"): "course_n_study_01",
    ("course", "lecture"): "course_n_study_01",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def normalize_pos(pos: str) -> str:
    value = str(pos or "").lower().strip().rstrip(".")
    if value in {"adj", "a"}:
        return "a"
    if value in {"vt", "vi"}:
        return "v"
    return value


def text_for_suggestion(item: dict[str, Any]) -> str:
    return " ".join(
        str(item.get(key) or "")
        for key in ("targetWord", "groupTitle", "groupSummaryZh", "explanationZh", "exampleZh", "exampleEn")
    ).lower()


def text_for_sense(sense: dict[str, Any]) -> str:
    return " ".join(
        str(sense.get(key) or "")
        for key in ("translation", "definitionZh", "definitionEn")
    ).lower()


def cjk_ngrams(text: str) -> set[str]:
    grams: set[str] = set()
    for seq in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        for n in (2, 3, 4):
            for i in range(0, max(0, len(seq) - n + 1)):
                grams.add(seq[i : i + n])
    return grams


def en_terms(text: str) -> set[str]:
    return {term for term in re.findall(r"[a-z][a-z-]{3,}", text.lower()) if term not in {"something", "someone", "thing", "used"}}


def hinted_pos(item: dict[str, Any], words_by_id: dict[str, dict[str, Any]]) -> str:
    target = str(item.get("targetWord") or "").lower()
    if target in COMMON_TARGET_POS:
        return COMMON_TARGET_POS[target]
    target_doc = words_by_id.get(str(item.get("targetWordId") or ""))
    poses = {
        normalize_pos(str(sense.get("pos") or ""))
        for sense in (target_doc or {}).get("senses") or []
        if sense.get("pos")
    }
    poses.discard("")
    if len(poses) == 1:
        return next(iter(poses))
    text = text_for_suggestion(item)
    if any(term in text for term in ("主题", "话题", "题目", "主语", "宾语", "课程", "课", "展览", "交易会")):
        return "n"
    if any(term in text for term in ("倾向于", "易于", "容易", "易受", "公平的", "相同的", "连续的")):
        return "a"
    if any(term in text for term in ("做", "进行", "使", "改变", "移动", "处理", "提供", "发布")):
        return "v"
    return ""


def choose_sense(item: dict[str, Any], word_doc: dict[str, Any], words_by_id: dict[str, dict[str, Any]]) -> tuple[str, int, str]:
    senses = word_doc.get("senses") or []
    valid = {str(sense.get("senseId") or "") for sense in senses}
    override = SOURCE_TARGET_OVERRIDES.get((str(item.get("word") or "").lower(), str(item.get("targetWord") or "").lower()))
    if override in valid:
        return override, 999, "override"
    if len(senses) == 1:
        return str(senses[0].get("senseId") or ""), 500, "single_sense"

    suggestion_text = text_for_suggestion(item)
    suggestion_grams = cjk_ngrams(suggestion_text)
    suggestion_terms = en_terms(suggestion_text)
    pos_hint = hinted_pos(item, words_by_id)

    scored: list[tuple[int, str, str]] = []
    for sense in senses:
        sid = str(sense.get("senseId") or "")
        sense_text = text_for_sense(sense)
        sense_grams = cjk_ngrams(sense_text)
        sense_terms = en_terms(sense_text)
        score = 0
        for gram in sense_grams:
            if gram in suggestion_grams:
                score += min(8, len(gram) * 2)
        for term in sense_terms:
            if term in suggestion_terms:
                score += min(6, len(term))
        if pos_hint and normalize_pos(str(sense.get("pos") or "")) == pos_hint:
            score += 6
        if sid and sid in suggestion_text:
            score += 20
        scored.append((score, sid, str(sense.get("translation") or "")))

    scored.sort(reverse=True)
    if not scored:
        return "", 0, "no_senses"
    best_score, best_sid, _ = scored[0]
    if best_score <= 0:
        # Last resort: if a POS hint selects exactly one source sense, use it.
        matching = [sense for sense in senses if normalize_pos(str(sense.get("pos") or "")) == pos_hint]
        if len(matching) == 1:
            return str(matching[0].get("senseId") or ""), 1, "pos_last_resort"
        return str(senses[0].get("senseId") or ""), 0, "fallback_first_sense"
    return best_sid, best_score, "semantic_score"


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    suggestions = read_jsonl(SUGGESTIONS_PATH)
    words_by_id = {row["_id"]: row for row in words}
    bound: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for item in suggestions:
        if item.get("relationType") != "near_synonym":
            continue
        word_doc = words_by_id.get(str(item.get("wordId") or ""))
        if not word_doc:
            skipped.append({"id": item.get("_id"), "reason": "missing_word"})
            continue
        sid, score, method = choose_sense(item, word_doc, words_by_id)
        if not sid:
            skipped.append({"id": item.get("_id"), "reason": method})
            continue
        scope = item.get("senseScope") if isinstance(item.get("senseScope"), dict) else {}
        scope["fromSenseId"] = sid
        item["senseScope"] = scope
        item["senseBinding"] = {
            "method": method,
            "score": score,
            "status": "auto_bound_pending_review",
        }
        bound.append({"id": item.get("_id"), "word": item.get("word"), "targetWord": item.get("targetWord"), "fromSenseId": sid, "score": score, "method": method})

    write_jsonl(SUGGESTIONS_PATH, suggestions)
    REPORT_PATH.write_text(
        json.dumps({"boundCount": len(bound), "skippedCount": len(skipped), "bound": bound, "skipped": skipped}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"bound: {len(bound)}")
    print(f"skipped: {len(skipped)}")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
