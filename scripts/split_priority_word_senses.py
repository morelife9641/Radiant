#!/usr/bin/env python3
"""Split high-impact mixed-POS word senses for IELTS content words.

This is intentionally curated, not a broad automatic parser. A noisy broad
split would pollute relation review more than it helps.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
RELATIONS_PATH = DATA_DIR / "word_relations.json"
REPORT_PATH = DATA_DIR / "sense_split_report.json"


SENSE_SPLITS: dict[str, list[dict[str, Any]]] = {
    "abstract": [
        {
            "senseId": "abstract_adj_01",
            "pos": "a",
            "translation": "抽象的；理论性的",
            "definitionEn": "Existing as an idea, quality, or concept rather than as a physical object.",
            "definitionZh": "作为观念、性质或概念存在，而不是具体可触摸的事物。",
        },
        {
            "senseId": "abstract_n_01",
            "pos": "n",
            "translation": "摘要；梗概；抽象概念",
            "definitionEn": "A short summary of a longer text, especially an academic article; an abstract idea.",
            "definitionZh": "较长文本，尤其是学术文章的简短摘要；也可指抽象概念。",
        },
        {
            "senseId": "abstract_v_01",
            "pos": "v",
            "translation": "提取；抽象出；写摘要",
            "definitionEn": "To remove or separate something, or to summarize the main points of a text.",
            "definitionZh": "提取或分离某物；也指概括文本要点、写成摘要。",
        },
    ],
    "conduct": [
        {
            "senseId": "conduct_n_01",
            "pos": "n",
            "translation": "行为；举止；管理方式",
            "definitionEn": "The way a person behaves, or the way an activity is organized and managed.",
            "definitionZh": "一个人的行为举止；也可指一项活动被组织和管理的方式。",
        },
        {
            "senseId": "conduct_v_01",
            "pos": "v",
            "translation": "进行；实施；管理；指挥；传导",
            "definitionEn": "To carry out an activity, manage a process, direct music, or allow heat or electricity to pass through.",
            "definitionZh": "进行或实施活动；管理过程；指挥音乐；也指传导热或电。",
        },
    ],
    "content": [
        {
            "senseId": "content_n_01",
            "pos": "n",
            "translation": "内容；所含之物；含量",
            "definitionEn": "The information, ideas, or material contained in something; the amount of a substance contained in something.",
            "definitionZh": "某物包含的信息、思想或材料；也指某种成分的含量。",
        },
        {
            "senseId": "content_adj_01",
            "pos": "a",
            "translation": "满意的；满足的",
            "definitionEn": "Satisfied with what one has or with a situation.",
            "definitionZh": "对已有的东西或当前情况感到满意、满足。",
        },
        {
            "senseId": "content_v_01",
            "pos": "v",
            "translation": "使满足；使满意",
            "definitionEn": "To make someone feel satisfied, often in a limited or modest way.",
            "definitionZh": "使某人感到满足或满意，常带有限度或勉强的意味。",
        },
    ],
    "contrast": [
        {
            "senseId": "contrast_n_01",
            "pos": "n",
            "translation": "对比；差异；反差",
            "definitionEn": "A clear difference between two or more things that is noticeable when they are compared.",
            "definitionZh": "两个或多个事物比较时显出的明显差异或反差。",
        },
        {
            "senseId": "contrast_v_01",
            "pos": "v",
            "translation": "对比；形成对照",
            "definitionEn": "To compare two things in order to show their differences, or to be noticeably different.",
            "definitionZh": "比较两个事物以显示差异；或指彼此形成明显对照。",
        },
    ],
    "display": [
        {
            "senseId": "display_n_01",
            "pos": "n",
            "translation": "展示；陈列；显示；显示器",
            "definitionEn": "An arrangement or presentation of things for people to see; a screen or visual output.",
            "definitionZh": "供人观看的展示或陈列；也指屏幕、显示器或显示内容。",
        },
        {
            "senseId": "display_v_01",
            "pos": "v",
            "translation": "展示；陈列；显示；表现",
            "definitionEn": "To show information, objects, qualities, or feelings clearly.",
            "definitionZh": "清楚地展示信息、物品、特征或情感。",
        },
    ],
    "exhibit": [
        {
            "senseId": "exhibit_n_01",
            "pos": "n",
            "translation": "展品；陈列品；证物",
            "definitionEn": "An object shown in an exhibition or presented as evidence in court.",
            "definitionZh": "展览中展出的物品；也指法庭上出示的证物。",
        },
        {
            "senseId": "exhibit_v_01",
            "pos": "v",
            "translation": "展出；陈列；显示；表现",
            "definitionEn": "To show something publicly, or to show a quality, feeling, or ability.",
            "definitionZh": "公开展出某物；也指显示某种特征、情感或能力。",
        },
    ],
    "fair": [
        {
            "senseId": "fair_adj_01",
            "pos": "a",
            "translation": "公平的；合理的；尚可的；晴朗的",
            "definitionEn": "Treating people equally; reasonable; acceptable but not excellent; clear and bright in weather.",
            "definitionZh": "公平对待的；合理的；还可以但不出色的；也可指天气晴朗。",
        },
        {
            "senseId": "fair_adv_01",
            "pos": "adv",
            "translation": "公平地；公正地",
            "definitionEn": "In a fair or just way.",
            "definitionZh": "以公平、公正的方式。",
        },
        {
            "senseId": "fair_n_01",
            "pos": "n",
            "translation": "集市；展览会；交易会",
            "definitionEn": "An event where goods, services, animals, or products are displayed, sold, or promoted.",
            "definitionZh": "展示、销售或推广商品、服务、动物或产品的集会、展览会或交易会。",
        },
        {
            "senseId": "fair_v_01",
            "pos": "v",
            "translation": "（天气）转晴；使表面平顺",
            "definitionEn": "To become fair in weather, or to make surfaces blend smoothly.",
            "definitionZh": "天气转晴；或使表面衔接平顺。此义较少见。",
        },
    ],
    "function": [
        {
            "senseId": "function_n_01",
            "pos": "n",
            "translation": "功能；作用；职责；函数",
            "definitionEn": "The purpose or role of something; a duty; in mathematics, a relation between values.",
            "definitionZh": "某物的功能、作用或职责；数学中指函数关系。",
        },
        {
            "senseId": "function_v_01",
            "pos": "v",
            "translation": "运转；起作用；发挥功能",
            "definitionEn": "To work or operate in the expected way.",
            "definitionZh": "按预期方式运转、起作用或发挥功能。",
        },
    ],
    "impact": [
        {
            "senseId": "impact_n_01",
            "pos": "n",
            "translation": "影响；作用；冲击",
            "definitionEn": "A strong effect or influence; the force or moment of one object hitting another.",
            "definitionZh": "强烈的影响或作用；也指物体撞击时的力量或瞬间。",
        },
        {
            "senseId": "impact_v_01",
            "pos": "v",
            "translation": "影响；冲击；撞击",
            "definitionEn": "To have a strong effect on something, or to hit something with force.",
            "definitionZh": "对某事产生强烈影响；或用力撞击某物。",
        },
    ],
    "issue": [
        {
            "senseId": "issue_n_01",
            "pos": "n",
            "translation": "问题；议题；争论点",
            "definitionEn": "An important subject or problem that people discuss or disagree about.",
            "definitionZh": "人们讨论、争议或需要解决的重要问题或议题。",
        },
        {
            "senseId": "issue_n_02",
            "pos": "n",
            "translation": "一期；期号；发行物",
            "definitionEn": "One edition in a series of newspapers, magazines, or similar publications.",
            "definitionZh": "报纸、杂志等连续出版物中的一期或一个期号。",
        },
        {
            "senseId": "issue_v_01",
            "pos": "v",
            "translation": "发布；发行；颁布；分发",
            "definitionEn": "To officially give, publish, or distribute something.",
            "definitionZh": "正式发布、发行、颁布或分发某物。",
        },
        {
            "senseId": "issue_v_02",
            "pos": "v",
            "translation": "流出；发出",
            "definitionEn": "To come out or flow out from somewhere.",
            "definitionZh": "从某处流出、发出或传出。",
        },
    ],
    "object": [
        {
            "senseId": "object_n_01",
            "pos": "n",
            "translation": "物体；对象；目标；宾语",
            "definitionEn": "A thing that can be seen or touched; a target or focus; in grammar, the receiver of an action.",
            "definitionZh": "可见或可触摸的物体；目标或对象；语法中动作承受者即宾语。",
        },
        {
            "senseId": "object_v_01",
            "pos": "v",
            "translation": "反对；不赞成",
            "definitionEn": "To say that one disagrees with or opposes something.",
            "definitionZh": "表示不同意或反对某事。",
        },
    ],
    "project": [
        {
            "senseId": "project_n_01",
            "pos": "n",
            "translation": "项目；计划；课题；工程",
            "definitionEn": "A planned piece of work, study, or activity with a specific aim.",
            "definitionZh": "有明确目标的一项计划、研究、活动或工程。",
        },
        {
            "senseId": "project_v_01",
            "pos": "v",
            "translation": "预计；投射；放映；突出；表达",
            "definitionEn": "To estimate for the future, show on a screen, send outward, stick out, or present an image of oneself.",
            "definitionZh": "预测未来；投射或放映；向外伸出；也指呈现某种形象。",
        },
    ],
    "secure": [
        {
            "senseId": "secure_adj_01",
            "pos": "a",
            "translation": "安全的；可靠的；稳固的；放心的",
            "definitionEn": "Safe from danger or failure; firmly fixed; feeling confident and not anxious.",
            "definitionZh": "没有危险或失败风险的；固定牢靠的；也指内心安心、有把握。",
        },
        {
            "senseId": "secure_v_01",
            "pos": "v",
            "translation": "获得；确保；保护；固定",
            "definitionEn": "To obtain something, make something safe, or fasten it firmly.",
            "definitionZh": "获得某物；确保或保护某物；也指把某物固定牢。",
        },
    ],
    "subject": [
        {
            "senseId": "subject_n_01",
            "pos": "n",
            "translation": "主题；题目；学科；主语；研究对象",
            "definitionEn": "A topic being discussed or studied; a school subject; a grammatical subject; a person or thing being studied.",
            "definitionZh": "讨论或研究的主题；学校学科；语法主语；也指实验或观察的对象。",
        },
        {
            "senseId": "subject_adj_01",
            "pos": "a",
            "translation": "受……支配的；易受……影响的；取决于……的",
            "definitionEn": "Likely to be affected by something, or dependent on a condition or rule.",
            "definitionZh": "常与 to 连用，表示容易受某事影响，或取决于某条件、规则。",
        },
        {
            "senseId": "subject_v_01",
            "pos": "v",
            "translation": "使遭受；使服从；使受制于",
            "definitionEn": "To make someone or something experience or be affected by something, often unpleasant.",
            "definitionZh": "使某人或某物经历、承受或受某事影响，常指不愉快的事。",
        },
    ],
    "yield": [
        {
            "senseId": "yield_n_01",
            "pos": "n",
            "translation": "产量；收益；产出",
            "definitionEn": "The amount produced, or the profit or return from an investment or activity.",
            "definitionZh": "生产出的数量；也指投资或活动带来的收益、产出。",
        },
        {
            "senseId": "yield_v_01",
            "pos": "v",
            "translation": "产生；出产；让出；屈服",
            "definitionEn": "To produce a result, give way, or stop resisting.",
            "definitionZh": "产生结果或出产某物；让出；停止抵抗、屈服。",
        },
    ],
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def build_sense(template: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    sense = deepcopy(template)
    sense.update(spec)
    sense.setdefault("collinsEn", "")
    sense.setdefault("collinsZh", "")
    sense.setdefault("synonyms", [])
    sense.setdefault("antonyms", [])
    sense.setdefault("gamingLink", None)
    return sense


def split_words(rows: list[dict[str, Any]]) -> dict[str, Any]:
    changed: list[dict[str, Any]] = []
    for row in rows:
        specs = SENSE_SPLITS.get(row.get("word"))
        if not specs:
            continue
        old_senses = row.get("senses") or [{}]
        template = old_senses[0] if old_senses else {}
        row["senses"] = [build_sense(template, spec) for spec in specs]
        changed.append(
            {
                "word": row["word"],
                "wordId": row["_id"],
                "oldSenseIds": [s.get("senseId") for s in old_senses],
                "newSenseIds": [s["senseId"] for s in row["senses"]],
            }
        )
    return {"changedWords": changed}


def target_sense_for_relation(word: str, old_sense_id: str, relation: dict[str, Any]) -> str | None:
    if word not in SENSE_SPLITS:
        return None

    scope = relation.get("senseScope") or {}
    pos = str(scope.get("pos") or "").lower()
    explanation = f"{relation.get('explanationEn') or ''} {relation.get('explanationZh') or ''}".lower()
    other_word = relation.get("toWord") if relation.get("fromWord") == word else relation.get("fromWord")

    if word == "fair" and old_sense_id == "fair_adj_adv_01":
        if other_word in {"display", "exhibit", "exhibition"} or any(term in explanation for term in ["fair:", "展览会", "交易会", "exhibition"]):
            return "fair_n_01"
        if "adv" in pos:
            return "fair_adv_01"
        return "fair_adj_01"
    if word == "function" and old_sense_id == "function_v_01":
        if pos in {"n", "noun"} or any(term in explanation for term in ["function is what", "功能", "作用", "purpose"]):
            return "function_n_01"
        return "function_v_01"
    if word == "display" and old_sense_id == "display_n_v_01":
        if pos in {"v", "vt", "vi"}:
            return "display_v_01"
        return "display_n_01"
    if word == "issue" and old_sense_id == "issue_n_01":
        if other_word == "distribute" or any(term in explanation for term in ["发行", "发布", "分发", "officially", "distribute"]):
            return "issue_v_01"
        return "issue_n_01"
    if word == "abstract" and old_sense_id == "abstract_adj_01":
        if other_word in {"summary", "resume", "digest", "outline"} or any(term in explanation for term in ["摘要", "summary", "abstract: 指论文"]):
            return "abstract_n_01"
        if pos in {"v", "vt", "vi"}:
            return "abstract_v_01"
        return "abstract_adj_01"
    if word == "conduct" and old_sense_id == "conduct_n_01":
        if any(term in explanation for term in ["指引导", "指挥", "管理", "lead", "direct"]) or pos in {"v", "vt", "vi"}:
            return "conduct_v_01"
        return "conduct_n_01"
    if word == "secure" and old_sense_id == "secure_v_01":
        if pos in {"a", "adj"} or any(term in explanation for term in ["安全的", "可靠的", "safe from"]):
            return "secure_adj_01"
        return "secure_v_01"

    coarse_to_default = {
        "yield_n_01": "yield_v_01" if pos in {"v", "vt", "vi"} else "yield_n_01",
        "contrast_n_01": "contrast_v_01" if pos in {"v", "vt", "vi"} else "contrast_n_01",
        "content_n_01": "content_adj_01" if pos in {"a", "adj"} else ("content_v_01" if pos in {"v", "vt", "vi"} else "content_n_01"),
        "object_n_01": "object_v_01" if pos in {"v", "vt", "vi"} else "object_n_01",
        "project_n_01": "project_v_01" if pos in {"v", "vt", "vi"} else "project_n_01",
        "impact_n_01": "impact_v_01" if pos in {"v", "vt", "vi"} else "impact_n_01",
        "exhibit_n_01": "exhibit_v_01" if pos in {"v", "vt", "vi"} else "exhibit_n_01",
        "subject_n_01": "subject_adj_01" if pos in {"a", "adj"} else ("subject_v_01" if pos in {"v", "vt", "vi"} else "subject_n_01"),
    }
    return coarse_to_default.get(old_sense_id)


def update_relation_sense_scopes(relations: list[dict[str, Any]]) -> dict[str, Any]:
    updates: list[dict[str, str]] = []
    for rel in relations:
        scope = rel.get("senseScope")
        if not isinstance(scope, dict):
            continue
        for side in ("from", "to"):
            word_key = f"{side}Word"
            sense_key = f"{side}SenseId"
            word = rel.get(word_key)
            old = scope.get(sense_key)
            if not word or not old:
                continue
            new = target_sense_for_relation(str(word), str(old), rel)
            if new and new != old:
                scope[sense_key] = new
                updates.append(
                    {
                        "relationId": rel.get("_id", ""),
                        "word": str(word),
                        "field": sense_key,
                        "old": str(old),
                        "new": new,
                    }
                )
    return {"relationSenseUpdates": updates}


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    relations = read_jsonl(RELATIONS_PATH)

    report = {}
    report.update(split_words(words))
    report.update(update_relation_sense_scopes(relations))

    write_jsonl(WORDS_PATH, words)
    write_jsonl(RELATIONS_PATH, relations)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"split words: {len(report['changedWords'])}")
    print(f"relation sense updates: {len(report['relationSenseUpdates'])}")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
