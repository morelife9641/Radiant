#!/usr/bin/env python3
"""Build a curated high-frequency word relation batch.

This batch fills gaps that the local ECDICT resemble list cannot cover cleanly.
The content is intentionally small and reviewed-by-rule: each group targets
high-frequency IELTS words that remained uncovered after the structured import.
"""

import json
import re
from itertools import permutations
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WORDS_PATH = ROOT / "tmp" / "cloud_import" / "words.ecdict_enriched.import.json"
EXISTING_RELATIONS_PATHS = [
    ROOT / "tmp" / "word_relations_import" / "word_relations.with_sense_id.import.json",
    ROOT / "tmp" / "word_relations_published_balanced_import" / "word_relations.import.json",
    ROOT / "tmp" / "word_relations_priority_import" / "word_relations.import.json",
]
OUT_DIR = ROOT / "tmp" / "word_relations_curated_import"
NOW = 1780732800000


CURATED_GROUPS = [
    {
        "id": "service_assistance_facility",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "service / assistance / facility",
        "summaryZh": "这组词都和“提供帮助或便利”有关，但 service 偏服务行为或体系，assistance 偏具体帮助，facility 偏设施或便利条件。",
        "items": [
            ("service", "服务行为、服务体系，也可指公共服务或维修保养。"),
            ("assistance", "对某人完成事情提供的具体帮助，语气比 service 更聚焦“帮忙”。"),
            ("facility", "让事情更容易进行的设施、设备或便利条件。"),
        ],
    },
    {
        "id": "point_aspect_detail_item",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "point / aspect / detail / item",
        "summaryZh": "这组词都可表示某个组成部分或讨论点，但 point 偏观点/要点，aspect 偏方面，detail 偏细节，item 偏清单中的项目。",
        "items": [
            ("point", "讨论、论证或说明中的要点，也可表示一个具体观点。"),
            ("aspect", "观察或分析某事物时切入的某个方面。"),
            ("detail", "整体中的细小信息或具体细节。"),
            ("item", "列表、议程、清单中的单项内容。"),
        ],
    },
    {
        "id": "authority_administration_leadership",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "authority / administration / leadership",
        "summaryZh": "这组词都和“管理或权力”有关，但 authority 偏权力或权威，administration 偏行政管理机构，leadership 偏领导能力或领导层。",
        "items": [
            ("authority", "合法权力、管辖权，也可指权威人士或官方机构。"),
            ("administration", "行政管理过程，或负责管理的政府/机构班子。"),
            ("leadership", "领导能力、领导方式，或一个组织中的领导层。"),
        ],
    },
    {
        "id": "available_accessible_suitable",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "available / accessible / suitable",
        "summaryZh": "这组词都可能表示“可用/适合”，但 available 强调可获得，accessible 强调可接近或可进入，suitable 强调适合某目的。",
        "items": [
            ("available", "现在能被使用、获得或安排出来。"),
            ("accessible", "容易到达、进入、使用或理解。"),
            ("suitable", "适合某个目的、场景或对象。"),
        ],
    },
    {
        "id": "community_population",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "community / population",
        "summaryZh": "这组词都可指一群人，但 community 强调共同生活、身份或联系，population 强调某地区或类别的人口数量。",
        "items": [
            ("community", "有共同地域、身份、兴趣或联系的人群/社区。"),
            ("population", "某地区、国家或类别中的人口数量或总体。"),
        ],
    },
    {
        "id": "process_procedure_stage",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "process / procedure / stage",
        "summaryZh": "这组词都和“步骤或过程”有关，但 process 强调整体进程，procedure 强调固定操作步骤，stage 强调发展中的某一阶段。",
        "items": [
            ("process", "从开始到结果的一整套过程或变化进程。"),
            ("procedure", "为完成某事而规定好的步骤、手续或流程。"),
            ("stage", "过程中的某个阶段，常表示发展顺序上的位置。"),
        ],
    },
    {
        "id": "security_defence",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "security / defence",
        "summaryZh": "这组词都和“保护”有关，但 security 偏安全状态或安保体系，defence 偏防御行为、国防或辩护。",
        "items": [
            ("security", "安全、保障、安保措施，也可指金融证券。"),
            ("defence", "防御、防卫、国防，也可指法律或论证中的辩护。"),
        ],
    },
    {
        "id": "attempt_effort_endeavour",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "attempt / effort / endeavour",
        "summaryZh": "这组词都和“尝试或努力”有关，但 attempt 偏一次尝试，effort 偏付出的力气，endeavour 偏正式、持续而认真的努力。",
        "items": [
            ("attempt", "为达成某事而进行的尝试，结果不一定成功。"),
            ("effort", "完成某事所付出的努力或精力。"),
            ("endeavour", "正式用词，强调认真、持续、带有决心的努力。"),
        ],
    },
    {
        "id": "concern_issue",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "concern / issue",
        "summaryZh": "这组词都能表示需要关注的问题，但 concern 偏担忧或利害关系，issue 偏需要讨论或解决的议题。",
        "items": [
            ("concern", "关心、担忧，或与某人/某组织有利害关系的事情。"),
            ("issue", "有争议、待讨论或待解决的问题/议题。"),
        ],
    },
    {
        "id": "fund_finance_grant",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "fund / finance / grant",
        "summaryZh": "这组词都和“资金”有关，但 fund 偏专款或基金，finance 偏资金安排或融资，grant 偏正式拨款或补助。",
        "items": [
            ("fund", "为特定目的准备或管理的一笔钱，也可作动词表示资助。"),
            ("finance", "资金、财务安排，作动词时表示为项目提供资金。"),
            ("grant", "政府、机构等正式给予的拨款、补助或许可。"),
        ],
    },
    {
        "id": "attack_assault_offensive",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "attack / assault / offensive",
        "summaryZh": "这组词都和“进攻”有关，但 attack 最普通，assault 强调突然猛烈，offensive 常指较大规模或有计划的攻势。",
        "items": [
            ("attack", "普通用词，可指军事攻击、言语抨击或疾病发作。"),
            ("assault", "突然、猛烈的攻击，也常用于人身攻击。"),
            ("offensive", "军事上的攻势或进攻行动，也可作形容词表示冒犯的。"),
        ],
    },
    {
        "id": "military_defence",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "military / defence",
        "summaryZh": "这组词都和军事有关，但 military 偏军队或军事属性，defence 偏防御、国防或防卫行为。",
        "items": [
            ("military", "与军队、军人或军事活动有关的。"),
            ("defence", "防御、防卫、国防体系或辩护。"),
        ],
    },
    {
        "id": "operate_manipulate",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "operate / manipulate",
        "summaryZh": "这组词都可表示“操作”，但 operate 偏操作机器/系统或运转，manipulate 偏熟练控制，也可含操纵他人的负面意思。",
        "items": [
            ("operate", "操作机器、系统，经营，运转，或进行手术。"),
            ("manipulate", "熟练控制或处理，也可表示为私利操纵人或局面。"),
        ],
    },
    {
        "id": "independent_separate",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "independent / separate",
        "summaryZh": "这组词都和“不依附”有关，但 independent 强调自主独立，separate 强调分开、不连在一起。",
        "items": [
            ("independent", "自主的、独立的，不受他人或外部控制。"),
            ("separate", "分开的、独立存在的，强调物理或概念上的分离。"),
        ],
    },
    {
        "id": "stock_inventory_supply",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "stock / inventory / supply",
        "summaryZh": "这组词都和“储备物品”有关，但 stock 偏库存或股票，inventory 偏详细库存清单，supply 偏可供使用的一批物资。",
        "items": [
            ("stock", "商店或组织持有的库存，也可指股票。"),
            ("inventory", "库存清单，或清单上记录的全部库存。"),
            ("supply", "可提供、可消耗的一批物资或供应量。"),
        ],
    },
    {
        "id": "host_sponsor",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "host / sponsor",
        "summaryZh": "这组词都和活动组织有关，但 host 偏主办或接待，sponsor 偏赞助或支持。",
        "items": [
            ("host", "主办、主持或接待活动/客人。"),
            ("sponsor", "为活动、项目或个人提供资金或正式支持。"),
        ],
    },
    {
        "id": "therefore_hence_consequently",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "therefore / hence / consequently",
        "summaryZh": "这组词都表示“因此”，但 therefore 最常见，hence 更正式且常强调由此得出，consequently 更强调结果。",
        "items": [
            ("therefore", "常用连接词，表示根据前文推出结论。"),
            ("hence", "较正式，表示“因此/由此”，常带推理色彩。"),
            ("consequently", "强调前因导致的结果。"),
        ],
    },
    {
        "id": "management_administration_leadership",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "management / administration / leadership",
        "summaryZh": "这组词都和“管理”有关，但 management 偏经营管理，administration 偏行政管理，leadership 偏领导力或领导层。",
        "items": [
            ("management", "组织、企业或任务的管理，也可指管理层。"),
            ("administration", "行政管理、政府任期或负责执行管理的机构。"),
            ("leadership", "领导能力、领导风格或领导层。"),
        ],
    },
    {
        "id": "data_evidence",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "data / evidence",
        "summaryZh": "这组词都可用于论证，但 data 偏收集到的数据资料，evidence 偏用来证明观点或事实的证据。",
        "items": [
            ("data", "经过收集、记录或统计的数据/资料。"),
            ("evidence", "支持判断、结论或指控的证据。"),
        ],
    },
    {
        "id": "theory_principle",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "theory / principle",
        "summaryZh": "这组词都和解释或规则有关，但 theory 偏理论体系，principle 偏基本原理、原则或行为准则。",
        "items": [
            ("theory", "用于解释现象的一套理论、学说或观点。"),
            ("principle", "基本原理、原则，也可指道德或行为准则。"),
        ],
    },
    {
        "id": "board_committee",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "board / committee",
        "summaryZh": "这组词都可指组织内的一群决策者，但 board 通常是董事会/委员会等高层机构，committee 偏为特定事务成立的委员会。",
        "items": [
            ("board", "董事会、理事会等负责监督或决策的机构。"),
            ("committee", "为研究、管理或处理某项事务而设立的委员会。"),
        ],
    },
    {
        "id": "opportunity_occasion",
        "type": "confusing_set",
        "relationType": "confusing",
        "title": "opportunity / occasion",
        "summaryZh": "这组词都和“时机”有关，但 opportunity 偏有利机会，occasion 偏某个具体场合、事件或时间点。",
        "items": [
            ("opportunity", "有利于做成某事的机会。"),
            ("occasion", "某个场合、事件或特定时刻。"),
        ],
    },
    {
        "id": "occur_appear_emerge",
        "type": "synonym_set",
        "relationType": "near_synonym",
        "idRelationType": "confusing",
        "title": "occur / appear / emerge",
        "summaryZh": "这组词都可表示“出现”，但 occur 偏事件发生，appear 偏被看见或显现，emerge 偏从隐藏状态逐渐出现。",
        "items": [
            ("occur", "事件发生、情况出现。"),
            ("appear", "进入视野、公开出现，或看起来似乎如此。"),
            ("emerge", "从隐藏、不明显或早期状态中显现出来。"),
        ],
    },
]


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")
    return re.sub(r"_+", "_", slug)


def load_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            file.write("\n")


def first_sense(word):
    senses = word.get("senses") or []
    return senses[0] if senses else {}


def main():
    words = load_jsonl(WORDS_PATH)
    by_word = {str(word.get("word") or "").lower(): word for word in words}
    by_normalized = {str(word.get("normalized") or word.get("word") or "").lower(): word for word in words}
    existing_relation_ids = set()
    for path in EXISTING_RELATIONS_PATHS:
        existing_relation_ids.update(row["_id"] for row in load_jsonl(path))

    groups = []
    relations = []
    skipped = []
    seen_relation_ids = set(existing_relation_ids)

    for spec in CURATED_GROUPS:
        members = []
        missing = []
        item_map = {}
        for term, text in spec["items"]:
            word = by_normalized.get(term.lower()) or by_word.get(term.lower())
            if not word:
                missing.append(term)
                continue
            members.append(word)
            item_map[word["_id"]] = text
        if len(members) < 2:
            skipped.append({"id": spec["id"], "missing": missing, "reason": "not_enough_members"})
            continue

        group_id = f"group_curated_{slugify(spec['id'])}"
        groups.append({
            "_id": group_id,
            "type": spec["type"],
            "title": spec["title"],
            "memberWordIds": [word["_id"] for word in members],
            "members": [
                {
                    "wordId": word["_id"],
                    "word": word["word"],
                    "role": "member",
                    "shortZh": item_map[word["_id"]][:80]
                }
                for word in members
            ],
            "summaryEn": "",
            "summaryZh": spec["summaryZh"],
            "dimensions": [
                {
                    "key": "usage_difference",
                    "nameZh": "用法区别",
                    "items": [{"wordId": word["_id"], "textZh": item_map[word["_id"]]} for word in members]
                }
            ],
            "examples": [],
            "source": {
                "type": "manual_curated",
                "note": "High-frequency IELTS relation batch generated from current uncovered-word report."
            },
            "status": "published",
            "createdAt": NOW,
            "updatedAt": NOW
        })

        for left, right in permutations(members, 2):
            left_sense = first_sense(left)
            right_sense = first_sense(right)
            relation_id = (
                f"rel_{left['_id']}_{left_sense.get('senseId') or 'any'}_"
                f"{right['_id']}_{right_sense.get('senseId') or 'any'}_{spec.get('idRelationType') or spec['relationType']}"
            )
            if relation_id in seen_relation_ids:
                continue
            seen_relation_ids.add(relation_id)
            relations.append({
                "_id": relation_id,
                "fromWordId": left["_id"],
                "fromWord": left["word"],
                "toWordId": right["_id"],
                "toWord": right["word"],
                "relationType": spec["relationType"],
                "groupId": group_id,
                "direction": "bidirectional",
                "strength": 4,
                "senseScope": {
                    "pos": left_sense.get("pos") or "",
                    "fromSenseId": left_sense.get("senseId") or "any",
                    "toSenseId": right_sense.get("senseId") or "any"
                },
                "explanationEn": "",
                "explanationZh": f"{left['word']}: {item_map[left['_id']]}; {right['word']}: {item_map[right['_id']]}",
                "exampleEn": "",
                "exampleZh": "",
                "tags": ["ielts", "manual_curated", spec["relationType"]],
                "status": "published",
                "createdAt": NOW,
                "updatedAt": NOW
            })

    write_jsonl(OUT_DIR / "word_relation_groups.import.json", groups)
    write_jsonl(OUT_DIR / "word_relations.import.json", relations)
    write_jsonl(OUT_DIR / "skipped.preview.json", skipped)
    report = {
        "groups": len(groups),
        "relations": len(relations),
        "skipped": len(skipped),
        "outputDir": str(OUT_DIR)
    }
    (OUT_DIR / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
