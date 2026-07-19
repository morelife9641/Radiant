#!/usr/bin/env python3
"""Curate post-400 auto English short definitions and add Chinese versions."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDBOOK_WORDS_PATH = DATA_DIR / "wordbook_words.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
REPORT_PATH = DATA_DIR / "post400_short_definition_manualization_report.json"


WORD_EN_OVERRIDES: dict[str, str] = {
    "comparatively": "To a fairly high degree when compared with something else.",
    "phenomenon": "A fact, event, or situation that can be observed or studied.",
    "originate": "To begin, start, or come from a particular place or source.",
    "refer": "To mention, describe, or look at something for information.",
    "belt": "A strip worn around the waist, or a long narrow area of land.",
    "circle": "A round shape, or a group of people with a shared interest.",
    "reveal": "To make something known or show something that was hidden.",
    "weaken": "To make something less strong or effective.",
    "drought": "A long period with little or no rain.",
    "rescue": "To save someone or something from danger.",
    "deficit": "An amount by which something is less than what is needed or expected.",
    "rank": "A position in an order, group, or level of importance.",
    "meanwhile": "During the same period of time.",
    "ecological": "Related to the relationship between living things and their environment.",
    "analyse": "To examine something carefully in order to understand it.",
    "impose": "To force someone to accept a rule, tax, duty, or situation.",
    "crucial": "Extremely important for the result of something.",
    "global": "Related to the whole world.",
    "pack": "A group of animals, people, or things kept or moving together.",
    "glacier": "A large mass of ice that moves slowly over land.",
    "foetus": "An unborn baby or young animal developing inside the mother.",
    "automatically": "By itself, without direct human control or conscious thought.",
    "demonstration": "An act of showing how something works or proving something clearly.",
    "stroke": "A sudden medical condition caused by a problem with blood flow in the brain.",
    "apparently": "Used to say that something seems true based on what is known.",
    "limb": "An arm, leg, wing, or similar body part.",
    "deterioration": "The process of becoming worse in quality, condition, or health.",
    "goal": "Something that a person or group wants to achieve.",
    "beneath": "In or to a lower place, position, or level.",
}


ZH_EN_EXACT: dict[str, str] = {
    "相对地": "In comparison with something else.",
    "比较地": "In comparison with something else.",
    "现象": "A fact, event, or situation that can be observed.",
    "起源": "The beginning or source of something.",
    "发生": "To happen or begin to exist.",
    "参考": "To look at something for information.",
    "查阅": "To look at a source for information.",
    "查询": "To look for information.",
    "提到": "To mention someone or something.",
    "谈及": "To mention or discuss something.",
    "腰带": "A strip worn around the waist.",
    "地带": "A long narrow area with a particular feature.",
    "圈出": "To draw a circle around something.",
    "圆圈": "A round shape.",
    "揭露": "To make hidden information known.",
    "泄露": "To let secret information become known.",
    "展现": "To show something clearly.",
    "变弱": "To become less strong or effective.",
    "干旱": "A long period with little or no rain.",
    "营救": "To save someone from danger.",
    "赤字": "The amount by which money spent is greater than money received.",
    "缺乏": "A situation in which there is not enough of something.",
    "等级": "A level or position in an order.",
    "排名": "A position in a list or order.",
    "同时": "During the same time.",
    "生态的": "Related to living things and their environment.",
    "分析": "To examine something carefully to understand it.",
    "强加": "To force someone to accept something.",
    "征收": "To officially demand payment of a tax or charge.",
    "关键的": "Extremely important.",
    "全球的": "Related to the whole world.",
    "一群": "A group of people, animals, or things.",
    "冰川": "A large mass of ice moving slowly over land.",
    "连接": "A link or relationship between things.",
    "巨大的": "Very large in size, amount, or degree.",
    "缺点": "A disadvantage or problem.",
    "因此": "As a result of something.",
    "征服": "To take control by force or effort.",
    "认出": "To know someone or something because you have seen or heard them before.",
    "详述": "To explain or describe something with more detail.",
    "限制": "To control or keep something within limits.",
    "模仿": "To copy the way someone or something behaves or appears.",
    "控制": "To direct, manage, or limit something.",
    "改变": "To make or become different.",
    "内部的": "Inside something or related to its inner part.",
    "部分": "One piece, share, or area of a larger whole.",
    "强调": "To give special importance or attention to something.",
    "努力": "An attempt to do something, especially something difficult.",
    "收集": "To bring things together from different places.",
    "争论": "A disagreement or discussion with different opinions.",
    "分发": "To give things to several people or places.",
    "信任": "To believe that someone or something is reliable or true.",
    "调查": "To examine facts carefully in order to learn the truth.",
    "干涉": "To become involved in a situation where you are not wanted.",
    "静止的": "Not moving or not changing.",
    "提议": "A suggestion or plan offered for consideration.",
    "保护": "To keep someone or something safe from harm.",
    "几乎": "Almost, but not completely.",
    "预言": "To say that something will happen in the future.",
    "承认": "To accept or say that something is true.",
    "混乱": "A state of disorder or confusion.",
    "抱怨": "To say that you are unhappy or annoyed about something.",
    "加强": "To make something stronger or more effective.",
    "繁殖": "To produce young animals or new plants.",
    "安排": "To plan or put things in order.",
    "极好的": "Very good or impressive.",
    "放弃": "To stop doing or trying to do something.",
    "一系列": "A number of things or events that come one after another.",
    "精确的": "Exact and accurate.",
    "命运": "What happens to someone or something in the future.",
    "刺激": "To encourage activity, growth, or interest.",
    "停止": "To end or make something end.",
    "严厉的": "Very strict, serious, or unpleasant.",
    "唯一的": "The only one of its kind.",
    "近似": "Similar but not exactly the same.",
    "海拔": "The height of a place above sea level.",
    "最初的": "Happening or existing at the beginning.",
    "普及": "To make something widely known or used.",
    "然而": "Used to introduce a contrast.",
    "感知": "To notice or understand something through the senses or mind.",
    "委托": "To give someone responsibility for doing something.",
    "图": "A drawing, chart, or visual representation.",
    "超过": "To be more than a number, amount, or limit.",
    "合作": "To work together with others.",
    "旋转": "To turn around a central point.",
    "装饰": "To make something look more attractive.",
    "实际的": "Real or related to what happens in practice.",
    "爆炸": "To burst suddenly with force and noise.",
    "移动": "To change position or go from one place to another.",
    "挖掘": "To dig or remove earth to find something.",
    "健壮的": "Strong and healthy.",
    "稳定": "To make or become steady and unlikely to change.",
    "吸收": "To take in liquid, information, or energy.",
    "外面的": "On or from the outside.",
    "荒谬的": "Very unreasonable or silly.",
    "相互作用": "To affect each other.",
    "组成": "To form or make up something.",
    "扩大": "To make or become larger.",
    "推荐": "To say that someone or something is good or suitable.",
    "扰乱": "To interrupt or prevent something from continuing normally.",
    "补偿": "To give something to make up for loss or harm.",
}


BAD_EN_MARKERS = {
    "savoir-faire",
    "underhand",
    "prophets",
    "bivalent",
    "polypeptide",
    "gametes",
    "vertebrate",
    "multiparous",
    "infield",
    "occlusion",
    "tantamount",
    "extant",
    "subsuming",
}


def read_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )


def clean_zh(text: str) -> str:
    text = re.sub(r"\[[^\]]+\]", "", text or "")
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"（[^）]*）", "", text)
    text = re.sub(r"\b(?:n|v|vt|vi|adj|adv|prep|conj|pron|a|ad)\.\s*", "", text, flags=re.I)
    text = text.replace("\\n", "；")
    parts = [p.strip(" .;；,，、") for p in re.split(r"[；;、\n]+", text) if p.strip(" .;；,，、")]
    if not parts:
        return ""
    first = parts[0]
    subparts = [p.strip() for p in re.split(r"[，,/]", first) if p.strip()]
    if len(subparts) >= 2 and len("；".join(subparts[:2])) <= 18:
        return "；".join(subparts[:2])
    return first[:40]


def zh_terms(text: str) -> list[str]:
    cleaned = clean_zh(text)
    terms = [p.strip() for p in re.split(r"[；;，,/、]", cleaned) if p.strip()]
    return terms or ([cleaned] if cleaned else [])


def clean_en_candidate(text: str) -> str:
    text = re.sub(r"^[a-z]+\.\s*", "", text.strip(), flags=re.I)
    text = re.sub(r"\([^)]*\)", "", text)
    text = text.replace("`", "'")
    text = re.sub(r"\s+", " ", text).strip(" ;.")
    rewrites = [
        (r"^of or relating to (.+)$", r"Related to \1"),
        (r"^pertaining to (.+)$", r"Related to \1"),
        (r"^having or showing (.+)$", r"Showing \1"),
        (r"^the act of (.+)$", r"The act or process of \1"),
        (r"^the process of (.+)$", r"The process of \1"),
        (r"^cause to (.+)$", r"To make something \1"),
        (r"^make (.+)$", r"To make \1"),
        (r"^be (.+)$", r"To be \1"),
    ]
    for pattern, repl in rewrites:
        text = re.sub(pattern, repl, text, flags=re.I)
    if text and not text.endswith("."):
        text += "."
    if text:
        text = text[0].upper() + text[1:]
    return text


def score_candidate(candidate: str, word: str) -> int:
    lower = candidate.lower()
    score = 0
    if any(marker in lower for marker in BAD_EN_MARKERS):
        score -= 80
    if len(candidate) > 150:
        score -= 25
    if len(candidate) < 18:
        score -= 10
    if word.lower() in lower:
        score -= 12
    if lower.startswith(("related to", "the act", "the process", "to ", "a ", "an ")):
        score += 8
    if ";" in candidate:
        score -= 8
    return score


def fallback_from_definition(word: str, definition: str) -> tuple[str, str]:
    candidates: list[str] = []
    for line in re.split(r"\\n|\n", definition or ""):
        line = clean_en_candidate(line)
        if line:
            candidates.append(line)
    if not candidates:
        return ("", "empty")
    best = sorted(candidates, key=lambda c: score_candidate(c, word), reverse=True)[0]
    return best, "cleaned_dictionary_definition"


def english_from_zh(word: str, zh: str, pos: str) -> tuple[str, str]:
    for term in zh_terms(zh):
        if term in ZH_EN_EXACT:
            text = ZH_EN_EXACT[term]
            if pos.startswith("v") and not text.lower().startswith(("to ", "used to ")):
                text = "To " + text[0].lower() + text[1:]
            if text and not text.endswith("."):
                text += "."
            return text, f"zh_core_map:{term}"
    return "", ""


def main() -> None:
    wordbook_words = read_records(WORDBOOK_WORDS_PATH)
    wordbook_by_id = {record.get("wordId"): record for record in wordbook_words}
    words_by_id = {record.get("_id"): record for record in read_records(WORDS_PATH)}
    learning_records = read_records(LEARNING_PATH)
    now = datetime.now(timezone.utc).isoformat()
    report: list[dict[str, Any]] = []
    source_counts: Counter[str] = Counter()

    for record in learning_records:
        word_id = record.get("wordId")
        wb = wordbook_by_id.get(word_id, {})
        order = wb.get("order") or 0
        if order <= 400 or record.get("shortDefinitionStatus") != "auto_from_english_definition_pending_review":
            continue

        word = str(record.get("word") or wb.get("word") or "").strip()
        word_doc = words_by_id.get(word_id, {})
        senses = word_doc.get("senses") or []
        first_sense = senses[0] if senses else {}
        zh_source = str(first_sense.get("translation") or first_sense.get("definitionZh") or "").strip()
        short_zh = clean_zh(zh_source)
        pos = str(first_sense.get("pos") or "").lower()

        if word in WORD_EN_OVERRIDES:
            short_en = WORD_EN_OVERRIDES[word]
            source = "word_override"
        else:
            short_en, source = english_from_zh(word, short_zh, pos)
            if not short_en:
                short_en, source = fallback_from_definition(word, str(first_sense.get("definitionEn") or ""))
            if not short_en:
                short_en = f"A word meaning {short_zh}." if short_zh else "A core IELTS vocabulary item."
                source = "generic_from_zh"

        old_en = record.get("shortDefinitionEn")
        old_zh = record.get("shortDefinitionZh")
        record["shortDefinitionEn"] = short_en
        record["shortDefinitionZh"] = short_zh
        record["shortDefinitionStatus"] = "curated_manual_short_definition"
        record["shortDefinitionReview"] = {
            "status": "manualized_post400_core_definition",
            "labelZh": "已手动整理核心短释",
            "reviewedAt": now,
            "reviewSource": source,
            "originalShortDefinitionEn": old_en,
            "originalShortDefinitionZh": old_zh,
        }
        provenance = record.setdefault("provenance", {})
        if isinstance(provenance, dict):
            provenance["shortDefinitionSource"] = "codex_post400_manual_core_pass"
            provenance["shortDefinitionReviewSource"] = source
            provenance["reviewStatus"] = "short_definition_manualized_with_zh"
            provenance["reviewedAt"] = now

        source_counts[source] += 1
        report.append(
            {
                "order": order,
                "word": word,
                "wordId": word_id,
                "oldShortDefinitionEn": old_en,
                "newShortDefinitionEn": short_en,
                "newShortDefinitionZh": short_zh,
                "source": source,
            }
        )

    write_jsonl(LEARNING_PATH, learning_records)
    report.sort(key=lambda row: row["order"])
    REPORT_PATH.write_text(
        json.dumps({"updated": len(report), "sourceCounts": dict(source_counts), "items": report}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"updated": len(report), "sourceCounts": dict(source_counts), "report": str(REPORT_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
