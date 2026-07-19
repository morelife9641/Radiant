#!/usr/bin/env python3
"""Translate shortDefinitionEn to Chinese with manual overrides plus Argos."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from argostranslate import translate

from translate_short_definition_zh_from_en import DIRECT


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "short_definition_zh_argos_translation_report.json"


EXTRA_DIRECT: dict[str, str] = {
    "A fact, event, or situation that can be observed.": "可以被观察到的事实、事件或情况。",
    "To happen or begin to exist.": "发生，或开始存在。",
    "To look at something for information.": "查看某物以获取信息。",
    "To mention someone or something.": "提到某人或某事物。",
    "A strip worn around the waist.": "系在腰部的带状物。",
    "A long narrow area with a particular feature.": "具有某种特征的狭长地带。",
    "To make hidden information known.": "使隐藏的信息为人所知。",
    "To become less strong or effective.": "变得不那么强或不那么有效。",
    "A long period with little or no rain.": "长时间少雨或无雨的时期。",
    "To save someone from danger.": "把某人从危险中救出。",
    "A group of people, animals, or plants living together in one place.": "生活在同一地点的一群人、动物或植物。",
    "A quality, feature, or possession that belongs to someone or something.": "属于某人或某物的性质、特征或所有物。",
    "To say firmly that something is true or must happen.": "坚定地说某事是真的或必须发生。",
    "To stay in the same place or condition, or to be left after others are gone.": "停留在同一地点或状态，或在其他人/物离开后留下。",
    "Already known, accepted, or provided in a particular situation.": "在特定情境中已经知道、接受或提供的。",
    "To fight against someone or something, especially a problem or danger.": "与某人或某事物斗争，尤其是问题或危险。",
    "Related to the usual weather conditions of an area over a long time.": "与某地区长期通常天气状况有关。",
    "Having a lot of money, goods, or resources.": "拥有大量金钱、物品或资源。",
    "To train plants or animals so that people can use or live with them.": "训练或培育植物、动物，使人们能够使用它们或与其共同生活。",
    "The act of spreading information, ideas, or knowledge to many people.": "向许多人传播信息、观点或知识的行为。",
    "To talk with too much pride about what you have or can do.": "过于自豪地谈论自己拥有的东西或能做的事。",
    "Existing in nature, or happening without being made or controlled by people.": "存在于自然中，或不是由人制造或控制而发生的。",
    "A condition or quality that makes success easier or gives someone a benefit.": "使成功更容易或给某人带来好处的条件或品质。",
    "Certain or likely to happen, or tied and unable to move freely.": "确定或可能发生的；或被绑住而不能自由移动的。",
    "To prefer, support, or help one person, idea, or choice more than another.": "相比另一个人、观点或选择，更偏爱、支持或帮助某一个。",
    "Care taken to avoid danger, mistakes, or unwanted results.": "为避免危险、错误或不良结果而采取的谨慎。",
    "The state that someone or something is in, or a requirement that must be met.": "某人或某物所处的状态，或必须满足的条件。",
    "A series of actions, changes, or steps that lead to a result.": "通向某个结果的一系列行动、变化或步骤。",
    "Something more important than other things and dealt with first.": "比其他事情更重要并优先处理的事。",
    "Clearly different from something else, or easy to recognize.": "与其他事物明显不同，或容易识别。",
    "Good, useful, or showing agreement, confidence, or certainty.": "好的、有用的，或表示同意、信心或确定性。",
    "Not enough or not good enough for a particular purpose.": "对特定目的而言数量不足或质量不够好。",
    "The sale of goods directly to customers, or to sell goods this way.": "直接向顾客销售商品，或以这种方式销售商品。",
    "Existing, happening, or coming before something else.": "在其他事物之前存在、发生或出现。",
    "A state of confusion, lack of order, or illness.": "混乱、缺乏秩序或疾病的状态。",
    "General rather than specific, or shared by a whole group.": "一般性的而非具体的，或为整个群体共有的。",
    "Numbers collected and studied to understand facts or trends.": "为了解事实或趋势而收集和研究的数字。",
    "To answer or react to something.": "回答或回应某事。",
    "An animal that feeds its young with milk from the mother's body.": "用母体乳汁哺育幼崽的动物。",
    "To collect information from different places and put it together.": "从不同地方收集信息并汇总。",
    "A chance to do something or make progress.": "做某事或取得进展的机会。",
    "To try to win or be more successful than others.": "努力获胜或比他人更成功。",
    "A small part or fact, or to describe something fully.": "小的部分或事实；或完整描述某事。",
    "A problem or condition that makes success more difficult.": "使成功更困难的问题或条件。",
    "To run after someone or something in order to catch it.": "为了抓住某人或某物而追赶。",
    "Completely correct, accurate, or precise.": "完全正确、准确或精确。",
    "A visual display of information, often using lines, bars, or symbols.": "用线条、条形或符号等方式展示信息的视觉图表。",
}


BAD_TRANSLATION_FIXES: dict[str, str] = {
    "令众生得成就.": "使某人能够做某事。",
}


def read_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )


def normalize_zh(value: str) -> str:
    value = re.sub(r"\s+", "", value.strip())
    value = value.replace(",", "，").replace(";", "；").replace(":", "：")
    value = value.replace(".", "。").replace("?", "？").replace("!", "！")
    value = value.replace("某物", "某事物")
    value = re.sub(r"。+", "。", value)
    return value


def main() -> None:
    rows = read_records(LEARNING_PATH)
    translator = translate.get_translation_from_codes("en", "zh")
    if translator is None:
        raise RuntimeError("Argos en->zh model is not installed")

    cache: dict[str, tuple[str, str]] = {}
    now = datetime.now(timezone.utc).isoformat()
    report: list[dict[str, Any]] = []
    source_counts: dict[str, int] = {}

    for row in rows:
        en = str(row.get("shortDefinitionEn") or "").strip()
        if not en:
            continue
        if en not in cache:
            if en in DIRECT:
                zh = DIRECT[en]
                source = "manual_direct"
            elif en in EXTRA_DIRECT:
                zh = EXTRA_DIRECT[en]
                source = "manual_direct"
            else:
                zh = translator.translate(en)
                zh = BAD_TRANSLATION_FIXES.get(zh, zh)
                source = "argos_translate_en_zh"
            cache[en] = (normalize_zh(zh), source)
        zh, source = cache[en]
        old_zh = row.get("shortDefinitionZh")
        row["shortDefinitionZh"] = zh
        review = row.setdefault("shortDefinitionReview", {})
        if isinstance(review, dict):
            review["shortDefinitionZhRetranslatedAt"] = now
            review["shortDefinitionZhSource"] = source
            review["oldShortDefinitionZh"] = old_zh
        provenance = row.setdefault("provenance", {})
        if isinstance(provenance, dict):
            provenance["shortDefinitionZhSource"] = source
            provenance["shortDefinitionZhTranslatedAt"] = now
        source_counts[source] = source_counts.get(source, 0) + 1
        report.append(
            {
                "wordId": row.get("wordId"),
                "word": row.get("word"),
                "shortDefinitionEn": en,
                "oldShortDefinitionZh": old_zh,
                "newShortDefinitionZh": zh,
                "source": source,
            }
        )

    write_jsonl(LEARNING_PATH, rows)
    REPORT_PATH.write_text(
        json.dumps({"updated": len(report), "sourceCounts": source_counts, "items": report}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"updated": len(report), "uniqueDefinitions": len(cache), "sourceCounts": source_counts, "report": str(REPORT_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
