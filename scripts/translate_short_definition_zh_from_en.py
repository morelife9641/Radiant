#!/usr/bin/env python3
"""Translate shortDefinitionEn into sentence-level shortDefinitionZh."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "short_definition_zh_retranslated_from_en_report.json"


DIRECT: dict[str, str] = {
    "To change something greatly in form, nature, or appearance.": "在形式、本质或外观上极大地改变某物。",
    "A topic, area of study, or person being discussed or tested.": "正在被讨论或测试的主题、研究领域或对象。",
    "A way or path from one place to another.": "从一个地方到另一个地方的路线或路径。",
    "Used to say that something is probably true based on what is known.": "用于表示根据已知情况判断某事很可能是真的。",
    "To learn something so that you can remember it exactly.": "学习某事物，使自己能够准确记住它。",
    "An important building, place, event, or discovery that is easy to recognize.": "容易被识别的重要建筑、地点、事件或发现。",
    "To touch lightly, or to make use of a source or resource.": "轻轻触碰，或利用某种来源或资源。",
    "To continue doing something or move forward.": "继续做某事，或向前推进。",
    "By that action or as a result of it.": "通过那个行为，或作为其结果。",
    "An object shown in an exhibition or presented as evidence in court.": "在展览中展出的物品，或在法庭上作为证据提交的物品。",
    "To include, require, or make someone take part in something.": "包含、需要，或使某人参与某事。",
    "Information or reaction given about how well something works or is done.": "针对某事运作或完成情况所给出的信息或反应。",
    "Something said or written as a comment.": "作为评论说出或写下的话。",
    "The study of how living things relate to each other and their environment.": "研究生物彼此之间以及与环境之间关系的学科。",
    "A written record, diary, or academic publication.": "书面记录、日记或学术刊物。",
    "A class, direction, or series of events over time.": "课程、方向，或随时间展开的一系列事件。",
    "A statement that explains the meaning of a word or idea.": "解释一个词或概念含义的陈述。",
    "Only, simply, or no more than.": "仅仅、只是，或不超过某个程度。",
    "To get, learn, or develop something over time.": "随着时间获得、学会或发展出某事物。",
    "Help, advice, or direction about what to do.": "关于该做什么的帮助、建议或指引。",
    "To make progress or action difficult.": "使进展或行动变得困难。",
    "A proposal intended to explain certain facts or observations.": "旨在解释某些事实或观察结果的假设性说明。",
    "Based on truth, logic, or accepted rules.": "基于事实、逻辑或公认规则。",
    "To publicly support an idea, policy, or person.": "公开支持某个观点、政策或人。",
    "To hold, move, or support something from one place to another.": "拿着、移动或支撑某物从一处到另一处。",
    "Planned piece of work, study, or activity with a specific aim.": "有特定目标的计划性工作、研究或活动。",
    "To disagree with or act against something.": "不同意某事，或采取行动反对某事。",
    "Used to introduce a contrast or opposite point.": "用于引出转折或相反观点。",
    "Used to emphasize that something is only or simply what is stated.": "用于强调某事只是所说的那样。",
    "A specific kind of something.": "某一类具体的事物。",
    "A warning signal or a feeling of fear caused by possible danger.": "警告信号，或由潜在危险引起的恐惧感。",
    "The state of being present.": "在场或存在的状态。",
    "Careful thought, notice, or mental focus.": "仔细思考、注意或精神集中。",
    "Any animal that lives by preying on other animals.": "靠捕食其他动物为生的动物。",
    "Run away quickly.": "迅速逃离。",
    "To experience something unpleasant as a result of your actions.": "由于自己的行为而遭受不愉快的后果。",
    "Marked by or showing unaffected simplicity and lack of guile or worldly experience.": "表现出单纯、缺乏心机或缺少世故经验。",
    "An advantage, help, or useful effect.": "优势、帮助或有用的效果。",
    "To make it possible for someone to do something.": "使某人能够做某事。",
    "A point or extent in space.": "空间中的某个位置或范围。",
    "From first to last.": "从头到尾；贯穿始终。",
    "To move someone or something from one place, job, or situation to another.": "把某人或某物从一个地方、职位或情境转到另一个。",
    "The amount, standard, or degree of something.": "某事物的数量、标准或程度。",
    "Not including someone or something.": "不包括某人或某物。",
    "To make an action or process easier.": "使某个行动或过程更容易。",
    "Different from one another; of several kinds.": "彼此不同；有若干种类。",
    "A period or step in a process or development.": "过程或发展中的一个阶段或步骤。",
    "To attach to something, or to push a pointed object into something.": "粘在某物上，或把尖状物插入某物。",
    "To find the position or place of something.": "找出某物的位置或地点。",
    "To watch or notice something carefully.": "仔细观察或注意某事物。",
    "Difficult task or problem that tests ability.": "考验能力的困难任务或问题。",
    "Knowledge about something, or sympathy for how someone feels.": "对某事的了解，或对他人感受的体谅。",
    "An idea or explanation based on evidence and reasoning.": "基于证据和推理的想法或解释。",
    "Knowing about a fact, situation, or problem.": "知道某个事实、情况或问题。",
    "Uneducated in general.": "总体上缺乏知识或教育。",
    "To take something away from a place or position.": "把某物从某处或某个位置移走。",
    "Imply as a possibility.": "暗示某事是一种可能。",
    "An unvarying or habitual method or procedure.": "固定不变或习惯性的做法或程序。",
    "A contentious speech act.": "带有争议性的言论行为。",
    "To state or express briefly.": "简短地说明或表达。",
    "Undergo development or evolution.": "经历发展或演变。",
    "Establish after a calculation, investigation, experiment, survey, or study.": "通过计算、调查、实验、调研或研究后确定。",
    "State or assert.": "陈述或坚称。",
    "To act in a particular way.": "以某种特定方式行动或表现。",
    "In an essential manner.": "以必要或必然的方式。",
    "A small flying insect that bites people or animals and drinks blood.": "一种会叮咬人或动物并吸血的小型飞虫。",
    "A product of your creative thinking and work.": "创造性思考和工作的产物。",
    "Short account of an incident (especially a biographical one).": "对某个事件的简短叙述，尤其是传记性事件。",
    "Get or find back.": "重新得到或找回。",
    "Put up with something or somebody unpleasant.": "忍受令人不快的事物或人。",
    "Related to money, trade, industry, or the economy.": "与金钱、贸易、产业或经济有关。",
    "Having an abundant supply of money or possessions of value.": "拥有大量金钱或有价值财产。",
    "Organize (the production of something) into an industry.": "把某物的生产组织成产业。",
    "The distance north or south of the equator, measured in degrees.": "以度数表示的赤道以北或以南的距离。",
    "Completing its life cycle within a year.": "在一年内完成其生命周期。",
    "Mark as different.": "标明某事物是不同的。",
    "To believe especially on uncertain or tentative grounds.": "尤其在依据不确定或试探性的情况下相信或推测。",
    "To break suddenly, or to make a short sharp sound.": "突然断裂，或发出短促清脆的声音。",
    "To be different from something or someone.": "与某事物或某人不同。",
}


PHRASES: list[tuple[str, str]] = [
    ("someone or something", "某人或某物"),
    ("something or someone", "某事物或某人"),
    ("people or groups", "人或群体"),
    ("people, animals, or plants", "人、动物或植物"),
    ("living things", "生物"),
    ("over time", "随着时间"),
    ("in order to", "为了"),
    ("as a result of", "作为……的结果"),
    ("a particular", "某个特定的"),
    ("the process of", "……的过程"),
    ("the act of", "……的行为"),
    ("related to", "与……有关"),
    ("a group of", "一群/一组"),
    ("a series of", "一系列"),
    ("a type of", "一种"),
    ("a kind of", "一种"),
    ("a form of", "一种形式的"),
    ("a part of", "……的一部分"),
    ("the amount of", "……的数量"),
    ("the quality of", "……的性质"),
    ("the state of", "……的状态"),
    ("the ability to", "……的能力"),
    ("a person who", "……的人"),
    ("a device that", "一种用来……的装置"),
    ("a system of", "……的系统"),
    ("a way of", "……的方式"),
    ("to make something", "使某物"),
    ("to make someone", "使某人"),
    ("to become", "变得"),
    ("to show", "显示"),
    ("to use", "使用"),
    ("to give", "给予"),
    ("to take", "拿走/采取"),
    ("to put", "放置"),
    ("to get", "获得"),
    ("to cause", "导致"),
    ("to prevent", "阻止"),
    ("to control", "控制"),
    ("to change", "改变"),
    ("to move", "移动"),
    ("to produce", "产生"),
    ("to describe", "描述"),
    ("to examine", "检查/研究"),
    ("to explain", "解释"),
    ("to support", "支持"),
    ("to continue", "继续"),
    ("to include", "包括"),
    ("to be", "是/处于"),
]


WORDS: list[tuple[str, str]] = [
    ("important", "重要的"),
    ("different", "不同的"),
    ("similar", "相似的"),
    ("possible", "可能的"),
    ("likely", "可能的"),
    ("useful", "有用的"),
    ("harmful", "有害的"),
    ("strong", "强的"),
    ("weak", "弱的"),
    ("large", "大的"),
    ("small", "小的"),
    ("high", "高的"),
    ("low", "低的"),
    ("new", "新的"),
    ("old", "旧的/古老的"),
    ("natural", "自然的"),
    ("human", "人的"),
    ("social", "社会的"),
    ("physical", "身体的/物理的"),
    ("mental", "心理的"),
    ("public", "公共的"),
    ("official", "官方的"),
    ("particular", "特定的"),
    ("general", "一般的"),
    ("specific", "具体的"),
    ("condition", "状况"),
    ("situation", "情况"),
    ("problem", "问题"),
    ("result", "结果"),
    ("effect", "影响"),
    ("reason", "原因"),
    ("method", "方法"),
    ("process", "过程"),
    ("activity", "活动"),
    ("information", "信息"),
    ("idea", "想法"),
    ("rule", "规则"),
    ("system", "系统"),
    ("place", "地方"),
    ("area", "区域"),
    ("time", "时间"),
    ("person", "人"),
    ("people", "人们"),
    ("thing", "事物"),
    ("things", "事物"),
    ("animal", "动物"),
    ("animals", "动物"),
    ("plant", "植物"),
    ("plants", "植物"),
    ("water", "水"),
    ("body", "身体"),
    ("work", "工作"),
    ("study", "研究/学习"),
    ("evidence", "证据"),
    ("knowledge", "知识"),
    ("change", "变化"),
    ("development", "发展"),
    ("growth", "增长/生长"),
    ("value", "价值"),
    ("level", "水平"),
    ("degree", "程度"),
    ("number", "数量"),
    ("amount", "数量"),
    ("quality", "质量/品质"),
    ("feature", "特征"),
    ("part", "部分"),
    ("parts", "部分"),
    ("source", "来源"),
    ("group", "群体"),
    ("groups", "群体"),
    ("event", "事件"),
    ("events", "事件"),
    ("action", "行动"),
    ("actions", "行动"),
    ("material", "材料"),
    ("energy", "能量"),
    ("light", "光"),
    ("sound", "声音"),
    ("air", "空气"),
    ("food", "食物"),
    ("money", "金钱"),
    ("trade", "贸易"),
    ("industry", "产业"),
    ("economy", "经济"),
]


def read_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )


def normalize_zh(value: str) -> str:
    value = re.sub(r"\s+", "", value)
    value = value.replace(",", "，").replace(";", "；").replace(":", "：")
    value = value.replace("..", "。")
    if value and value[-1] not in "。！？":
        value += "。"
    return value


def rule_translate(en: str) -> tuple[str, str]:
    source = "rule"
    text = en.strip()
    if text in DIRECT:
        return DIRECT[text], "direct"

    lower = text.lower().strip(".")
    zh = lower

    for src, dst in sorted(PHRASES, key=lambda item: len(item[0]), reverse=True):
        zh = re.sub(r"\b" + re.escape(src) + r"\b", dst, zh, flags=re.I)
    for src, dst in sorted(WORDS, key=lambda item: len(item[0]), reverse=True):
        zh = re.sub(r"\b" + re.escape(src) + r"\b", dst, zh, flags=re.I)

    # Common sentence shells. These deliberately keep a conservative
    # "指/表示" style when the inner phrase is only partially translated.
    if lower.startswith("to "):
        zh = "指" + zh
    elif lower.startswith(("a ", "an ")):
        zh = "指" + re.sub(r"^(a|an)\s+", "一个", zh, flags=re.I)
    elif lower.startswith("the "):
        zh = "指" + re.sub(r"^the\s+", "该", zh, flags=re.I)
    elif lower.startswith("used to "):
        zh = "用于" + zh.removeprefix("used to ")
    elif lower.startswith("related to ") or lower.startswith("relating to "):
        zh = "与" + re.sub(r"^(related|relating) to\s+", "", zh, flags=re.I) + "有关"
    elif lower.startswith("not "):
        zh = "不" + zh[4:]

    # Clean common leftovers from simple replacement.
    zh = zh.replace(" or ", "或").replace(" and ", "和").replace(" with ", "具有")
    zh = zh.replace(" from ", "从").replace(" into ", "进入/变成").replace(" by ", "通过")
    zh = zh.replace(" of ", "的").replace(" in ", "在").replace(" for ", "为了/用于")
    zh = zh.replace(" that ", "，其").replace(" which ", "，其").replace(" when ", "当")
    zh = zh.replace(" someone ", "某人").replace(" something ", "某事物")
    zh = zh.replace(" someone", "某人").replace(" something", "某事物")

    # If too much English remains, be honest in the provenance but still
    # produce a Chinese explanation wrapper instead of a misleading word tag.
    ascii_letters = sum(1 for ch in zh if ("a" <= ch <= "z") or ("A" <= ch <= "Z"))
    if ascii_letters > 20:
        source = "rule_partial_pending_review"
        zh = f"英文短释大意：{zh}"
    return normalize_zh(zh), source


def main() -> None:
    rows = read_records(LEARNING_PATH)
    now = datetime.now(timezone.utc).isoformat()
    report: list[dict[str, Any]] = []
    source_counts: dict[str, int] = {}

    for row in rows:
        en = str(row.get("shortDefinitionEn") or "").strip()
        if not en:
            continue
        old_zh = row.get("shortDefinitionZh")
        zh, source = rule_translate(en)
        row["shortDefinitionZh"] = zh
        review = row.setdefault("shortDefinitionReview", {})
        if isinstance(review, dict):
            review["shortDefinitionZhRetranslatedAt"] = now
            review["shortDefinitionZhSource"] = f"{source}_translation_of_shortDefinitionEn"
            review["oldShortDefinitionZh"] = old_zh
        provenance = row.setdefault("provenance", {})
        if isinstance(provenance, dict):
            provenance["shortDefinitionZhSource"] = f"{source}_translation_of_shortDefinitionEn"
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
    print(json.dumps({"updated": len(report), "sourceCounts": source_counts, "report": str(REPORT_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
