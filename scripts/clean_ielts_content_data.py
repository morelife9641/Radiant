#!/usr/bin/env python3
"""Apply deterministic editorial cleanup to the IELTS content import draft."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp/cloud_import_ielts_content_words"


TRANSLATION_OVERRIDES = {
    "line_plant_scents_15": "这些防御屏障存在于多种植物中，包括玉米、豆类以及模式植物拟南芥（Arabidopsis thaliana）。",
    "line_plant_scents_22": "在雨林下层乔木 Leonardoxa africana 上，Petalomyrmex phylax 蚂蚁会在嫩叶上巡逻，并攻击遇到的任何植食性昆虫。",
    "line_plastics_07": "约翰·韦斯利·海厄特凭借一种名为赛璐珞的材料赢得了这项奖。",
    "line_grey_workers_14": "公司员工伊沃·林瑙表示，原因并不是 SGL 更看重年长员工。",
    "line_gilbert_magnetism_21": "他的著作包括《论磁石、磁体和地球大磁体》。",
    "line_gilbert_magnetism_24": "他甚至创造了 electric（电的）一词。",
    "line_bananas_49": "巴西政府研究机构 EMBRAPA 的首席香蕉病理学家卢阿迪尔·加斯帕罗托说：‘亚马孙地区的大多数香蕉田已经被这种疾病摧毁。’",
    "line_bananas_66": "‘成本非常高昂，而我们一无所获，’主导国际香蕉贸易的三大公司之一奇基塔公司的研究主管罗纳德·罗梅罗说。",
    "line_antikythera_45": "埃德蒙兹说：‘它精巧到不可能是唯一的一台。’",
    "line_endangered_language_32": "欣顿承认：‘现在就称这种语言已经复兴还为时过早。’",
    "line_eco_resort_41": "库兰湾岛度假村并不符合普里多（2000）提出的‘度假村开发谱系’特征。",
    "line_tv_addiction_41": "25 多年前，心理学家坦尼斯·M·麦克贝斯·威廉姆斯开展了一项研究。",
    "line_music_language_24": "戴维·施瓦茨及其同事认为，这两种观点都不正确。",
    "line_megafires_17": "‘曾经的开阔地如今变成了住宅，为火灾提供燃料，使火势燃烧得更加猛烈，’加州林业部门消防员工会的特里·麦克黑尔说。",
    "line_megafires_24": "消防员工会的麦克黑尔先生说。",
    "line_heat_wave_13": "‘这非常不同寻常，’琼斯教授告诉《独立报》。",
    "line_scent_success_02": "从 Hills Hoist 晾衣架到 Cochlear 人工耳蜗，商业成功案例多种多样；除了说创造者抓住了消费者迫不及待想拥有的东西，很难再作进一步概括。",
    "line_scent_success_16": "OzKleen 的转机始于奎因和赫伦聘请一名工业化学家来重振产品线。",
    "line_scent_success_23": "Shower Power 的配方被认为是由他发现的。",
    "line_scent_success_26": "起初，Shower Power 只按商业用量销售；但由于布里斯班附近 Beenleigh 零售店的顾客不断交口称赞，汤姆·奎因决定改用 750 毫升瓶装销售。",
    "line_scent_success_28": "其他人也开始写信给 OzKleen，称赞 Shower Power 的效果。",
    "line_scent_success_32": "‘我们欣喜若狂，’OzKleen 的财务主管贝琳达·麦克唐纳说。",
    "line_scent_success_35": "OzKleen 放弃了其他所有产品，围绕 Shower Power 重建了业务。",
    "line_scent_success_54": "Shower Power 在英国称为 Bath Power；在联邦政府出口发展补助金的帮助下，它于四年前推出。",
    "line_linguistic_change_23": "辅音群经常会被简化。",
}


SOURCE_REVIEWS = {
    "line_ants_16": {
        "status": "needs_source_verification",
        "issueType": "incomplete_sentence",
        "noteZh": "原文止于 presence，语义不完整；未在缺少可靠依据时补写宾语。",
    },
    "line_ants_18": {
        "status": "corrected",
        "issueType": "missing_word",
        "correctedText": "But it allows others to flee to safety.",
        "noteZh": "在 allows others 后补足不定式标记 to。",
    },
    "line_tv_addiction_41": {
        "status": "corrected_across_lines",
        "issueType": "line_break_split_name",
        "correctedText": "More than 25 years ago psychologist Tannis M. MacBeth Williams of the University of British Columbia studied a mountain community that had no television until cable finally arrived.",
        "continuationLineId": "line_tv_addiction_42",
        "noteZh": "姓名与句子被错误拆到下一行；保留原行，另存合并后的校订文本。",
    },
    "line_megafires_24": {
        "status": "corrected_across_lines",
        "issueType": "line_break_split_attribution",
        "correctedText": "says Mr. McHale with the firefighters union.",
        "previousLineId": "line_megafires_23",
        "noteZh": "Mr. 与 McHale 被错误拆行；保留原行，另存合并后的署名片段。",
    },
    "line_gilbert_magnetism_24": {
        "status": "corrected",
        "issueType": "line_break_hyphenation",
        "correctedText": "He even coined the word ‘electric’.",
        "noteZh": "删除版面换行造成的词内连字符。",
    },
    "line_scent_success_54": {
        "status": "corrected",
        "issueType": "ocr_typo",
        "correctedText": "Shower Power, known as Bath Power in Britain, was launched four years ago with the help of an export development grant from the Federal Government.",
        "noteZh": "结合语境将 OCR 结果 grand 校订为 grant。",
    },
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def clean_lines() -> tuple[int, int]:
    path = OUT / "content_lines.json"
    rows = load_jsonl(path)
    by_id = {row["_id"]: row for row in rows}
    missing = (set(TRANSLATION_OVERRIDES) | set(SOURCE_REVIEWS)) - set(by_id)
    if missing:
        raise RuntimeError(f"missing content lines: {sorted(missing)}")

    for line_id, translation in TRANSLATION_OVERRIDES.items():
        row = by_id[line_id]
        row["translationZh"] = translation
        row["translationStatus"] = "ai_second_pass_pending_human_review"
        meta = row.setdefault("translationMeta", {})
        meta.update({
            "reviewStatus": "pending_human_review",
            "secondPassStatus": "completed",
            "secondPassMethod": "editorial_ai_review",
        })

    for line_id, review in SOURCE_REVIEWS.items():
        row = by_id[line_id]
        row["textOriginal"] = row["text"]
        row["sourceReview"] = {key: value for key, value in review.items() if key != "correctedText"}
        if review.get("correctedText"):
            row["correctedText"] = review["correctedText"]

    write_jsonl(path, rows)
    return len(TRANSLATION_OVERRIDES), len(SOURCE_REVIEWS)


def build_relations() -> tuple[int, int]:
    member_ids = {row["wordId"] for row in load_jsonl(OUT / "wordbook_words.json")}
    relation_source = load_jsonl(ROOT / "tmp/import_ready/word_relations.import.json")
    relations = [
        row for row in relation_source
        if row.get("status") == "published"
        and row.get("fromWordId") in member_ids
        and row.get("toWordId") in member_ids
        and row.get("explanationZh")
    ]
    used_groups = {row.get("groupId") for row in relations if row.get("groupId")}
    group_source = load_jsonl(ROOT / "tmp/import_ready/word_relation_groups.import.json")
    groups = [row for row in group_source if row.get("_id") in used_groups and row.get("status") == "published"]
    valid_groups = {row["_id"] for row in groups}
    for relation in relations:
        if relation.get("groupId") not in valid_groups:
            relation["groupId"] = None
    write_jsonl(OUT / "word_relations.json", relations)
    write_jsonl(OUT / "word_relation_groups.json", groups)
    return len(relations), len(groups)


def main() -> None:
    translations, source_reviews = clean_lines()
    relations, groups = build_relations()
    print(json.dumps({
        "translationOverrides": translations,
        "sourceReviews": source_reviews,
        "wordRelations": relations,
        "wordRelationGroups": groups,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
