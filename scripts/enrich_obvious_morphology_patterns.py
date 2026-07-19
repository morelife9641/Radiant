#!/usr/bin/env python3
"""Enrich obvious morphology patterns that the conservative baseline missed."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "obvious_morphology_patterns_report.json"

COMBINING_FORMS = {
    "zoo": ("zoo- / zo-", "动物", "Greek", "zoological 可理解为与动物学或动物有关。"),
    "bio": ("bio-", "生命；生物", "Greek", "biological 表示与生命或生物学有关。"),
    "geo": ("geo-", "地球；土地；地理", "Greek", "geo- 常见于 geography/geology/geological。"),
    "geograph": ("geo- + graph", "地理；描绘地球", "Greek", "geographical 与 geography 同族，geo 表示地球，graph 表示书写/描绘。"),
    "eco": ("eco-", "生态；环境", "Greek", "eco- 在 ecological 中表示生态、环境。"),
    "psycho": ("psycho-", "心理；精神", "Greek", "psycho- 常见于 psychology/psychological。"),
    "astro": ("astro-", "星；天体", "Greek", "astro- 常见于 astrology/astronomy。"),
    "mechan": ("mechan-", "机器；机械；机制", "Greek", "mechanical 与机器、机械或机制有关。"),
    "techn": ("techn-", "技术；工艺", "Greek", "technical 与技术、专门技能有关。"),
    "clinic": ("clinic-", "临床；诊所", "Greek", "clinical 表示临床的、诊所相关的。"),
    "clin": ("clin-", "床；临床", "Greek", "clinical 本义与病床旁诊治、临床观察有关。"),
    "medic": ("medic-", "医学；治疗", "Latin", "medical 表示医学或治疗相关。"),
    "chem": ("chem-", "化学", "Arabic/Greek", "chemical 表示化学的、化学物质。"),
    "electr": ("electr-", "电；电的", "Greek", "electrical 表示与电有关。"),
    "phys": ("phys-", "自然；身体；物理", "Greek", "physical 可指身体的、物理的或自然的。"),
    "typ": ("typ-", "类型；样式", "Greek", "typical 表示具有某类典型特征。"),
    "ident": ("ident-", "相同；身份", "Latin", "identical 表示完全相同。"),
    "scept": ("scept- / skeptic-", "怀疑", "Greek", "sceptical 表示持怀疑态度。"),
    "eth": ("eth- / ethos", "习俗；品格；伦理", "Greek", "ethical 与伦理、道德原则有关。"),
    "critic": ("critic-", "判断；评论", "Greek", "critical 可表示批判的、关键的。"),
    "practic": ("practice", "实践；实际操作", "Greek/Latin", "practical 表示实际的、可操作的。"),
    "classic": ("classic", "经典；古典", "Latin", "classical 表示古典的、经典传统相关的。"),
    "vert": ("vert", "转；转向", "Latin", "vertical 与转向上方、垂直方向有关。"),
}

SPECIAL = {
    "tropical": {
        "segments": [
            {"form": "tropic", "type": "base/root", "meaningZh": "热带；回归线", "origin": "Greek"},
            {"form": "-al", "type": "suffix", "meaningZh": "……的；与……有关的", "origin": "Latin"},
        ],
        "explanationZh": "tropical = tropic（热带、回归线）+ -al（……的），表示热带的。",
    },
    "medical": {
        "segments": [
            {"form": "medic-", "type": "base/root", "meaningZh": "医学；治疗", "origin": "Latin"},
            {"form": "-al", "type": "suffix", "meaningZh": "……的；与……有关的", "origin": "Latin"},
        ],
        "explanationZh": "medical = medic（医学、治疗）+ -al（……的），表示医学的、医疗的。",
    },
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def first_sense(word: dict[str, Any]) -> dict[str, Any]:
    senses = word.get("senses") or []
    return senses[0] if senses else {}


def word_maps() -> tuple[dict[str, dict[str, Any]], set[str]]:
    words = read_jsonl(WORDS_PATH)
    global_by_norm = {str(row.get("normalized") or row.get("word") or "").lower(): row for row in words}
    wordbook_norms = {
        str(row.get("normalized") or row.get("word") or "").lower()
        for row in read_jsonl(DATA_DIR / "wordbook_words.json")
    }
    return global_by_norm, wordbook_norms


def related_item(candidate: str, global_by_norm: dict[str, dict[str, Any]], wordbook_norms: set[str], note: str) -> dict[str, Any] | None:
    doc = global_by_norm.get(candidate)
    if not doc:
        return None
    sense = first_sense(doc)
    return {
        "wordId": doc["_id"],
        "word": doc.get("word") or candidate,
        "pos": sense.get("pos") or "",
        "translationZh": sense.get("translation") or "",
        "connectionZh": note,
        "clickable": True,
        "referenceStatus": "in_wordbook" if candidate in wordbook_norms else "global_word_doc",
        "status": "draft",
        "reviewStatus": "auto_enriched_pending_review",
    }


def logy_morphology(word: str) -> dict[str, Any] | None:
    lower = word.lower()
    if lower == "astrology":
        display, meaning, origin, note = COMBINING_FORMS["astro"]
        return {
            "segments": [
                {"form": display, "type": "combining_form", "meaningZh": meaning, "origin": origin, "noteZh": note},
                {"form": "-logy", "type": "root/suffix", "meaningZh": "学科；研究", "origin": "Greek"},
            ],
            "explanationZh": "astrology = astro-（星、天体）+ -logy（学科/研究），表示占星学。",
            "relatedWords": [],
        }
    if lower.endswith("logical"):
        stem = lower[: -len("logical")]
        form = COMBINING_FORMS.get(stem)
        if not form:
            return None
        display, meaning, origin, note = form
        return {
            "segments": [
                {"form": display, "type": "combining_form", "meaningZh": meaning, "origin": origin, "noteZh": note},
                {"form": "-logy", "type": "root/suffix", "meaningZh": "学科；研究", "origin": "Greek"},
                {"form": "-ical", "type": "suffix", "meaningZh": "……的；与……有关的", "origin": "Greek/Latin"},
            ],
            "explanationZh": f"{word} 可理解为 {display}（{meaning}）+ -logy（学科/研究）+ -ical（……的），表示与该领域或性质有关。",
            "relatedWords": [],
        }
    if lower.endswith("ology"):
        stem = lower[: -len("ology")]
        form = COMBINING_FORMS.get(stem)
        if not form:
            return None
        display, meaning, origin, note = form
        return {
            "segments": [
                {"form": display, "type": "combining_form", "meaningZh": meaning, "origin": origin, "noteZh": note},
                {"form": "-logy", "type": "root/suffix", "meaningZh": "学科；研究", "origin": "Greek"},
            ],
            "explanationZh": f"{word} 可理解为 {display}（{meaning}）+ -logy（学科/研究）。",
            "relatedWords": [],
        }
    return None


def ical_morphology(word: str) -> dict[str, Any] | None:
    lower = word.lower()
    if lower in SPECIAL:
        return dict(SPECIAL[lower])
    if lower == "geographical":
        return {
            "segments": [
                {"form": "geo-", "type": "combining_form", "meaningZh": "地球；土地；地理", "origin": "Greek"},
                {"form": "graph", "type": "root", "meaningZh": "书写；描绘", "origin": "Greek"},
                {"form": "-ical", "type": "suffix", "meaningZh": "……的；与……有关的", "origin": "Greek/Latin"},
            ],
            "explanationZh": "geographical 可理解为 geo-（地球/地理）+ graph（描绘）+ -ical（……的），表示地理的。",
            "relatedWords": [],
        }
    if not lower.endswith("ical"):
        return None
    stem = lower[: -len("ical")]
    form = COMBINING_FORMS.get(stem)
    if not form:
        return None
    display, meaning, origin, note = form
    return {
        "segments": [
            {"form": display, "type": "combining_form", "meaningZh": meaning, "origin": origin, "noteZh": note},
            {"form": "-ical", "type": "suffix", "meaningZh": "……的；与……有关的", "origin": "Greek/Latin"},
        ],
        "explanationZh": f"{word} 可理解为 {display}（{meaning}）+ -ical（……的），表示与该概念有关。",
        "relatedWords": [],
    }


def main() -> None:
    rows = read_jsonl(LEARNING_PATH)
    global_by_norm, wordbook_norms = word_maps()
    updated: list[str] = []
    related_added = 0

    for row in rows:
        word = str(row.get("normalized") or row.get("word") or "").lower()
        current = row.get("morphology") or {}
        first_type = ((current.get("segments") or [{}])[0].get("type") or "")
        if first_type not in {"base", "base/root"}:
            continue
        next_morph = logy_morphology(word) or ical_morphology(word)
        if not next_morph:
            continue

        related = next_morph.setdefault("relatedWords", [])
        base_candidates = []
        if word.endswith("logical"):
            base_candidates = [word[: -len("logical")] + "logy", word[: -len("logical")] + "logical"]
        elif word.endswith("ology"):
            base_candidates = [word[: -len("ology")] + "ological"]
        elif word.endswith("ical"):
            base_candidates = [word[: -len("ical")] + "ic", word[: -len("ical")] + "ics"]
        for candidate in base_candidates:
            if candidate == word:
                continue
            item = related_item(candidate, global_by_norm, wordbook_norms, f"{candidate} 与 {word} 共享同一构词基础。")
            if item:
                related.append(item)
                related_added += 1

        row["morphology"] = next_morph
        provenance = row.setdefault("provenance", {})
        refinements = provenance.setdefault("refinements", [])
        if "obvious_morphology_patterns" not in refinements:
            refinements.append("obvious_morphology_patterns")
        updated.append(word)

    write_jsonl(LEARNING_PATH, rows)
    report = {"updatedCount": len(updated), "relatedWordsAdded": related_added, "updated": updated}
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
