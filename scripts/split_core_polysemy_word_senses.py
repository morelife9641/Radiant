#!/usr/bin/env python3
"""Apply semantic-level splits to high-value polysemous IELTS words.

The goal is B-level splitting: not merely n/v, but the sense granularity that
matters for synonym groups, antonym axes, and learning pages. Low-frequency or
dictionary-noise senses are left for manual review instead of being forced into
the main data.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
CANDIDATES_PATH = DATA_DIR / "remaining_mixed_pos_sense_candidates.json"
REPORT_PATH = DATA_DIR / "core_polysemy_sense_split_report.json"
MANUAL_REVIEW_PATH = DATA_DIR / "semantic_sense_manual_review.json"


def sense(sense_id: str, pos: str, translation: str, definition_en: str, definition_zh: str) -> dict[str, Any]:
    return {
        "senseId": sense_id,
        "pos": pos,
        "translation": translation,
        "definitionEn": definition_en,
        "definitionZh": definition_zh,
    }


CORE_SPLITS: dict[str, list[dict[str, Any]]] = {
    "course": [
        sense("course_n_study_01", "n", "课程；教程", "A series of lessons or studies on a particular subject.", "围绕某一学科或主题安排的一系列课程、学习内容。"),
        sense("course_n_process_01", "n", "过程；进程；发展方向", "The way in which something develops or proceeds over time.", "事情随时间推进、发展或变化的过程与方向。"),
        sense("course_n_route_01", "n", "路线；航线；路径；方针", "A route, path, or direction followed by a person, vehicle, or action.", "人、交通工具或行动所遵循的路线、路径、航线或方针。"),
        sense("course_v_flow_01", "v", "流动；快速移动", "To flow or move quickly in a particular direction.", "液体、血液等流动；或人、动物、车辆朝某方向快速移动。此义相对少见。"),
    ],
    "point": [
        sense("point_n_idea_01", "n", "要点；论点；观点；意义", "A particular idea, argument, detail, or purpose in speech or writing.", "话语或文章中的要点、论点、细节、目的或意义。"),
        sense("point_n_position_01", "n", "点；地点；时刻；阶段", "A particular place, moment, stage, or position.", "某个具体地点、时刻、阶段或位置。"),
        sense("point_n_score_01", "n", "分数；得分；点数", "A unit used in scoring, measurement, or calculation.", "用于评分、计量或计算的单位、分数或点数。"),
        sense("point_n_tip_01", "n", "尖端；尖头", "The sharp or narrow end of something.", "某物尖锐或狭窄的一端。"),
        sense("point_v_direct_01", "v", "指向；瞄准；指出", "To direct attention, a finger, or an object toward someone or something.", "把注意力、手指或物体朝向某人或某物；指出、指明。"),
    ],
    "range": [
        sense("range_n_scope_01", "n", "范围；幅度；领域", "The limits within which something varies or is included.", "某事物变化、覆盖或包含的范围、幅度或领域。"),
        sense("range_n_series_01", "n", "一系列；一套", "A set or series of different things of the same general kind.", "同一类别下的一系列或一套不同事物。"),
        sense("range_n_land_01", "n", "山脉；靶场；牧场", "A line of mountains, an area for shooting practice, or open land for animals.", "山脉；射击练习场；或牲畜放牧的开阔土地。"),
        sense("range_v_vary_01", "v", "变化；变动；涵盖", "To vary between limits or include different things within a set.", "在一定界限内变化；或涵盖一组不同事物。"),
        sense("range_v_arrange_01", "v", "排列；分布", "To arrange or be spread out in a particular way.", "按某种方式排列、分布或延伸。"),
    ],
    "feature": [
        sense("feature_n_characteristic_01", "n", "特征；特色；特点", "An important or noticeable quality, part, or characteristic of something.", "某物重要或显著的特征、部分或特点。"),
        sense("feature_n_media_01", "n", "专题节目；特写；故事片", "A special article, programme, or full-length film.", "专题文章、节目、特写，或故事片。"),
        sense("feature_v_include_01", "v", "以……为特色；由……主演；占重要位置", "To include someone or something as an important part.", "把某人或某物作为重要部分、特色或主演呈现。"),
    ],
    "contract": [
        sense("contract_n_agreement_01", "n", "合同；契约", "A formal legal agreement between people or organizations.", "个人或组织之间正式的法律协议或契约。"),
        sense("contract_v_agree_01", "v", "订约；签约；承包", "To make a formal agreement to do work or provide a service.", "正式签订协议、承包工作或提供服务。"),
        sense("contract_v_shrink_01", "v", "收缩；缩小；感染", "To become smaller, tighter, or shorter; or to get a disease.", "变小、变紧或缩短；也可指感染疾病。"),
    ],
    "level": [
        sense("level_n_amount_01", "n", "水平；程度；等级", "The amount, standard, or degree of something.", "某事物的数量、标准、程度或等级。"),
        sense("level_n_surface_01", "n", "水平面；高度；楼层", "A flat position, height, or floor.", "水平位置、高度、平面或楼层。"),
        sense("level_adj_flat_01", "a", "平的；水平的；同等的", "Flat, horizontal, or at the same height or standard.", "平坦的、水平的，或处于相同高度、标准的。"),
        sense("level_v_flatten_01", "v", "使变平；夷平；瞄准", "To make something flat or equal, destroy a building, or aim something.", "使某物变平或相等；夷平建筑；也可指瞄准。"),
    ],
    "scale": [
        sense("scale_n_size_01", "n", "规模；范围；程度", "The size, extent, or level of something.", "某事物的规模、范围或程度。"),
        sense("scale_n_measure_01", "n", "刻度；等级；比例尺", "A system of marks, levels, or proportions used for measuring or comparing.", "用于测量或比较的刻度、等级、比例尺或尺度。"),
        sense("scale_n_weighing_01", "n", "磅秤；天平", "A device used for weighing people or things.", "用于称量人或物的设备。"),
        sense("scale_n_animal_01", "n", "鳞片；鳞", "A small thin plate on the skin of a fish or reptile.", "鱼类或爬行动物皮肤上的小薄片。"),
        sense("scale_v_climb_01", "v", "攀登；爬越", "To climb to the top of something high or steep.", "攀登或爬越高而陡的物体。"),
    ],
    "figure": [
        sense("figure_n_number_01", "n", "数字；数值；金额", "A number, amount, or statistic.", "数字、数量、金额或统计数据。"),
        sense("figure_n_person_01", "n", "人物；人士", "A person, especially someone important or well-known.", "人物，尤其是重要或知名人士。"),
        sense("figure_n_shape_01", "n", "身材；轮廓；图形；图表", "A shape, body outline, diagram, or illustration.", "身体轮廓、身材、图形、插图或图表。"),
        sense("figure_v_think_01", "v", "认为；估计；计算", "To think, judge, estimate, or calculate.", "认为、判断、估计或计算。"),
    ],
    "charge": [
        sense("charge_n_cost_01", "n", "费用；价钱", "The amount of money asked for goods or services.", "商品或服务所收取的费用、价钱。"),
        sense("charge_n_accusation_01", "n", "指控；控告", "An official statement that someone may be guilty of a crime or wrong action.", "正式指称某人可能犯错或犯罪的控告、指控。"),
        sense("charge_n_responsibility_01", "n", "掌管；照管；责任", "Responsibility for looking after or managing someone or something.", "照管、管理某人或某物的责任。"),
        sense("charge_n_electricity_01", "n", "电荷；电量", "Electricity stored in something or carried by a particle.", "某物储存的电量或粒子携带的电荷。"),
        sense("charge_v_cost_01", "v", "收费；要价", "To ask someone to pay a particular amount of money.", "要求某人支付某一金额。"),
        sense("charge_v_accuse_01", "v", "指控；控告", "To officially accuse someone of a crime or wrong action.", "正式指控某人犯罪或做错事。"),
        sense("charge_v_power_01", "v", "充电；使充满", "To put electricity into a battery or device.", "给电池或设备补充电能。"),
    ],
    "process": [
        sense("process_n_steps_01", "n", "过程；步骤；程序", "A series of actions, changes, or steps that produce a result.", "产生某种结果的一系列行动、变化或步骤。"),
        sense("process_v_handle_01", "v", "处理；办理；加工", "To deal with information, documents, materials, or food in a systematic way.", "系统地处理信息、文件、材料或食品；办理、加工。"),
    ],
    "design": [
        sense("design_n_plan_01", "n", "设计；方案；构想", "A plan or drawing showing how something will be made or arranged.", "说明某物如何制作、安排或建造的方案、图样或构想。"),
        sense("design_n_pattern_01", "n", "图案；样式", "A pattern, decoration, or visual arrangement.", "图案、装饰样式或视觉安排。"),
        sense("design_n_intention_01", "n", "意图；图谋", "A purpose or intention, often one that is hidden.", "目的或意图，常可指隐藏的图谋。"),
        sense("design_v_create_01", "v", "设计；构思；规划", "To create or plan how something will look, work, or be made.", "设计或规划某物的外观、运作方式或制作方式。"),
    ],
    "form": [
        sense("form_n_type_01", "n", "形式；类型；形态", "A type, kind, shape, or way in which something exists or appears.", "某物存在或呈现的形式、类型、形态或样子。"),
        sense("form_n_document_01", "n", "表格", "A document with spaces for writing information.", "带有空格、用于填写信息的文件。"),
        sense("form_v_create_01", "v", "形成；组成；建立", "To create, develop, or become something.", "形成、组成、建立，或发展成为某物。"),
    ],
    "effect": [
        sense("effect_n_result_01", "n", "影响；结果；效果", "A change, result, or influence caused by something.", "由某事引起的变化、结果、影响或效果。"),
        sense("effect_v_cause_01", "v", "实现；使发生；引起", "To make something happen or bring it about.", "使某事发生、实现或产生。此义较正式。"),
    ],
    "match": [
        sense("match_n_competition_01", "n", "比赛；竞赛", "A sports game or competition.", "体育比赛或竞赛。"),
        sense("match_n_equal_01", "n", "相配的人或物；对手", "A person or thing that is equal to or suitable for another.", "与另一人或物相当、匹配或合适的人或物；也可指对手。"),
        sense("match_n_fire_01", "n", "火柴", "A small stick used for making fire.", "用于点火的小木棒或纸棒。"),
        sense("match_v_correspond_01", "v", "匹配；相称；相符合", "To be the same as, suitable for, or correspond to something.", "与某物相同、适合、相称或对应。"),
    ],
    "position": [
        sense("position_n_place_01", "n", "位置；方位；姿势", "The place where someone or something is, or the way the body is arranged.", "某人或某物所在的位置、方位；或身体姿势。"),
        sense("position_n_job_01", "n", "职位；职务", "A job or role in an organization.", "组织中的工作岗位、职位或职务。"),
        sense("position_n_opinion_01", "n", "立场；观点", "An opinion, attitude, or stance on an issue.", "对某个问题的观点、态度或立场。"),
        sense("position_v_place_01", "v", "安放；定位；安排", "To put someone or something in a particular place or situation.", "把某人或某物放在特定位置、情境或角色中。"),
    ],
    "survey": [
        sense("survey_n_research_01", "n", "调查；民意调查", "A set of questions used to collect information from people.", "通过问题向人群收集信息的调查。"),
        sense("survey_n_inspection_01", "n", "勘察；测量；审视", "An examination of land, buildings, or a situation.", "对土地、建筑或情况进行的勘察、测量或审视。"),
        sense("survey_v_research_01", "v", "调查；检视；测量；俯瞰", "To ask questions, examine something, measure land, or look over an area.", "进行问卷调查；检视某物；测量土地；或俯瞰某一区域。"),
    ],
    "surface": [
        sense("surface_n_outer_01", "n", "表面；外表", "The outer or top layer of something.", "某物的外层、表层或外表。"),
        sense("surface_v_appear_01", "v", "浮出水面；显露；浮现", "To appear after being hidden, unknown, or under water.", "从水下、隐藏处或未知状态中出现、显露。"),
        sense("surface_v_cover_01", "v", "给……铺面；给……加表层", "To put a surface layer on a road, floor, or object.", "给道路、地板或物体加上表层、铺面。"),
    ],
    "challenge": [
        sense("challenge_n_difficulty_01", "n", "挑战；艰巨任务；难题", "A difficult task or problem that tests ability.", "考验能力的困难任务、挑战或难题。"),
        sense("challenge_n_question_01", "n", "质疑；挑战；异议", "A questioning of whether something is true, legal, or acceptable.", "对某事真实性、合法性或可接受性的质疑、挑战。"),
        sense("challenge_v_question_01", "v", "质疑；挑战；反对", "To question whether something is true, legal, or acceptable.", "质疑某事是否真实、合法或可接受。"),
        sense("challenge_v_invite_01", "v", "向……挑战", "To invite someone to compete or fight.", "邀请或要求某人与自己竞争、比赛或对抗。"),
    ],
    "demand": [
        sense("demand_n_need_01", "n", "需求；需要", "The need or desire for goods, services, or action.", "对商品、服务或行动的需要、需求。"),
        sense("demand_n_request_01", "n", "要求；强烈要求", "A firm request for something.", "对某事的坚定要求、强烈要求。"),
        sense("demand_v_require_01", "v", "要求；需要", "To need something or ask for it firmly.", "需要某物；或强硬地要求某事。"),
    ],
    "supply": [
        sense("supply_n_amount_01", "n", "供应量；供给；储备", "The amount of something available or provided.", "可获得或被提供的数量、供应量或储备。"),
        sense("supply_n_goods_01", "n", "补给品；必需品", "Goods or materials needed for a particular purpose.", "为某一目的所需的物资、补给品或必需品。"),
        sense("supply_v_provide_01", "v", "供应；提供；满足", "To provide something that is needed or wanted.", "提供所需或想要的东西；供应、满足需要。"),
    ],
    "interest": [
        sense("interest_n_attention_01", "n", "兴趣；关注", "A feeling of wanting to know about or take part in something.", "想了解或参与某事的兴趣、关注。"),
        sense("interest_n_benefit_01", "n", "利益；利害关系", "An advantage, concern, or share in something.", "利益、利害关系或权益。"),
        sense("interest_n_money_01", "n", "利息", "Money paid for borrowing money or earned from saving it.", "借款需支付或存款可获得的钱，即利息。"),
        sense("interest_v_attract_01", "v", "使感兴趣；吸引", "To make someone want to know more about something.", "使某人想进一步了解某事；吸引兴趣。"),
    ],
    "advance": [
        sense("advance_n_progress_01", "n", "进展；进步；增长", "Progress, improvement, or movement forward.", "向前发展、改善、提高或增长。"),
        sense("advance_n_payment_01", "n", "预付款；预支", "Money paid before it is due or before work is completed.", "到期前或工作完成前预先支付的钱。"),
        sense("advance_adj_early_01", "a", "预先的；先行的", "Done, given, or arranged before something happens.", "在某事发生前完成、给予或安排的。"),
        sense("advance_v_move_01", "v", "前进；推进；取得进展", "To move forward, develop, or make progress.", "向前移动、推进、发展或取得进展。"),
    ],
    "stock": [
        sense("stock_n_goods_01", "n", "库存；储备品；存货", "Goods or materials kept for future use or sale.", "为将来使用或销售而保存的商品、材料或存货。"),
        sense("stock_n_share_01", "n", "股票；股份", "A share in the ownership of a company.", "公司所有权中的一份，即股票或股份。"),
        sense("stock_n_animals_01", "n", "家畜；牲畜", "Farm animals kept for use or breeding.", "饲养用于生产或繁殖的农场动物。"),
        sense("stock_v_store_01", "v", "储备；存有；进货", "To keep or provide goods for sale or use.", "保存、提供或进货以供销售或使用。"),
        sense("stock_adj_standard_01", "a", "常备的；标准的；普通的", "Standard, usual, or regularly kept.", "标准的、通常的、常备的。"),
    ],
    "grant": [
        sense("grant_n_money_01", "n", "补助金；拨款；助学金", "Money given by an organization for a particular purpose.", "组织为特定目的提供的补助金、拨款或助学金。"),
        sense("grant_n_permission_01", "n", "授予；授权", "The act of giving permission, rights, or property.", "给予许可、权利或财产的行为。"),
        sense("grant_v_give_01", "v", "给予；授予；准许", "To officially give money, rights, or permission.", "正式给予资金、权利或许可。"),
        sense("grant_v_admit_01", "v", "承认；同意", "To admit that something is true, often unwillingly.", "承认某事属实，常带有勉强意味。"),
    ],
    "balance": [
        sense("balance_n_stability_01", "n", "平衡；均衡", "A steady state in which different forces or parts are equal or properly arranged.", "不同力量或部分相等、协调时的稳定状态。"),
        sense("balance_n_money_01", "n", "余额；结余", "The amount of money remaining in an account.", "账户中剩余的钱，即余额、结余。"),
        sense("balance_v_keep_01", "v", "使平衡；权衡", "To keep steady, or consider different factors fairly.", "保持稳定、使平衡；或公平考虑不同因素。"),
    ],
    "core": [
        sense("core_n_centre_01", "n", "核心；中心部分；要点", "The central, most important, or essential part of something.", "某物中心、最重要或最本质的部分。"),
        sense("core_n_fruit_01", "n", "果心；果核", "The hard central part of a fruit containing seeds.", "水果中含有种子的硬质中心部分。"),
        sense("core_v_remove_01", "v", "去核", "To remove the core from a fruit.", "去掉水果的果心或果核。"),
    ],
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def build_sense(template: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    row = deepcopy(template)
    row.update(spec)
    row.setdefault("collinsEn", "")
    row.setdefault("collinsZh", "")
    row.setdefault("synonyms", [])
    row.setdefault("antonyms", [])
    row.setdefault("gamingLink", None)
    return row


def manual_review_reason(candidate: dict[str, Any]) -> str:
    word = candidate.get("word", "")
    low_priority_words = {
        "genetic", "physical", "commercial", "cooperative", "valuable", "exclusive",
        "original", "static", "continental", "multinational", "ritual", "resident",
        "arable", "hybrid", "characteristic", "spectacular", "component", "household",
        "saline", "inferior", "academic", "intellectual", "joint", "ongoing",
    }
    function_words = {"nevertheless", "otherwise", "except", "apart", "opposite", "contrary"}
    if word in low_priority_words:
        return "附带名词义或形容词义较边缘，需确认是否值得进入雅思词书主 sense。"
    if word in function_words:
        return "词典词性标签混杂，但学习上未必需要拆成多个核心 sense。"
    return "多义较明显，但需要结合文章语境决定是否细拆到语义层。"


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    candidates = read_json(CANDIDATES_PATH, [])
    candidate_ids = {row.get("wordId") for row in candidates if isinstance(row, dict)}
    changed: list[dict[str, Any]] = []

    for row in words:
        if row["_id"] not in candidate_ids:
            continue
        specs = CORE_SPLITS.get(row["word"])
        if not specs:
            continue
        old_senses = row.get("senses") or [{}]
        template = old_senses[0] if old_senses else {}
        row["senses"] = [build_sense(template, spec) for spec in specs]
        changed.append(
            {
                "word": row["word"],
                "wordId": row["_id"],
                "oldSenseIds": [item.get("senseId") for item in old_senses],
                "newSenseIds": [item["senseId"] for item in row["senses"]],
            }
        )

    changed_ids = {item["wordId"] for item in changed}
    manual_review = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        if candidate.get("wordId") in changed_ids:
            continue
        item = dict(candidate)
        item["reviewFlag"] = "needs_human_sense_review"
        item["reasonZh"] = manual_review_reason(candidate)
        manual_review.append(item)

    write_jsonl(WORDS_PATH, words)
    REPORT_PATH.write_text(
        json.dumps(
            {
                "changedCount": len(changed),
                "manualReviewCount": len(manual_review),
                "changedWords": changed,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    MANUAL_REVIEW_PATH.write_text(json.dumps(manual_review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"semantic split words: {len(changed)}")
    print(f"manual review words: {len(manual_review)}")
    print(REPORT_PATH)
    print(MANUAL_REVIEW_PATH)


if __name__ == "__main__":
    main()
