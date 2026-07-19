#!/usr/bin/env python3
"""Add focused lexical and usage refinements for the IELTS inventory page."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
SUGGESTIONS_PATH = DATA_DIR / "word_lexical_suggestions.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "word_inventory_refinement_report.json"


RELATION_REFINEMENTS = [
    {
        "word": "proceed",
        "targetWord": "recede",
        "relationType": "antonym",
        "strength": 5,
        "explanationZh": "proceed 表示继续前进、继续进行；recede 表示后退、退去或逐渐远离，方向相反。",
        "exampleEn": "The group proceeded along the path as the floodwater began to recede.",
        "exampleZh": "洪水开始退去时，这一行人继续沿路前进。",
        "source": "manual_direction_contrast",
    },
    {
        "word": "proceed",
        "targetWord": "process",
        "relationType": "spelling_confusable",
        "strength": 5,
        "explanationZh": "proceed 是动词，表示“继续进行”；process 多作名词，表示“过程、流程”，也可作动词“处理”。两词开头相似，阅读中容易看错。",
        "exampleEn": "The process was delayed, but the team decided to proceed.",
        "exampleZh": "流程被延误了，但团队决定继续进行。",
        "source": "manual_spelling_confusable",
    },
    {
        "word": "process",
        "targetWord": "proceed",
        "relationType": "spelling_confusable",
        "strength": 5,
        "explanationZh": "process 表示过程、流程或处理；proceed 表示继续进行。两词形近但词性和用法不同。",
        "exampleEn": "The process was delayed, but the team decided to proceed.",
        "exampleZh": "流程被延误了，但团队决定继续进行。",
        "source": "manual_spelling_confusable",
    },
    {
        "word": "access",
        "targetWord": "excess",
        "relationType": "spelling_confusable",
        "strength": 5,
        "explanationZh": "access 表示进入、使用或获取的机会；excess 表示过量、超出。两词形近但意义完全不同。",
        "exampleEn": "Students need access to data, but excess data can make analysis harder.",
        "exampleZh": "学生需要获取数据，但过量数据会让分析更困难。",
        "source": "manual_spelling_confusable",
    },
    {
        "word": "excess",
        "targetWord": "access",
        "relationType": "spelling_confusable",
        "strength": 5,
        "explanationZh": "excess 表示过量；access 表示进入或获取的机会。两词只差一个字母，不能混用。",
        "exampleEn": "Students need access to data, but excess data can make analysis harder.",
        "exampleZh": "学生需要获取数据，但过量数据会让分析更困难。",
        "source": "manual_spelling_confusable",
    },
    {
        "word": "succeed",
        "targetWord": "exceed",
        "relationType": "spelling_confusable",
        "strength": 4,
        "explanationZh": "succeed 表示成功或继任；exceed 表示超过。两词读写相近，但语义不同。",
        "exampleEn": "The project may succeed if costs do not exceed the budget.",
        "exampleZh": "如果成本不超过预算，这个项目可能会成功。",
        "source": "manual_spelling_confusable",
    },
    {
        "word": "exceed",
        "targetWord": "succeed",
        "relationType": "spelling_confusable",
        "strength": 4,
        "explanationZh": "exceed 表示超过；succeed 表示成功或继任。两词形近，阅读时要看清前缀。",
        "exampleEn": "The project may succeed if costs do not exceed the budget.",
        "exampleZh": "如果成本不超过预算，这个项目可能会成功。",
        "source": "manual_spelling_confusable",
    },
]


USAGE_REFINEMENTS = {
    "recover": {
        "collocations": [
            ("recover from illness", "从疾病中恢复"),
            ("recover quickly", "迅速恢复"),
            ("fully recover", "完全恢复"),
            ("recover lost data", "恢复丢失的数据"),
            ("economic recovery", "经济复苏"),
        ],
        "grammarPatterns": [
            {
                "pattern": "recover from + illness / injury / shock",
                "exampleEn": "Patients may need months to recover from a serious injury.",
                "exampleZh": "病人可能需要数月才能从重伤中恢复。",
            },
            {
                "pattern": "recover + object",
                "exampleEn": "Engineers recovered the lost data from the damaged device.",
                "exampleZh": "工程师从受损设备中恢复了丢失的数据。",
            },
        ],
        "commonErrors": [
            {
                "wrong": "recover the illness",
                "correct": "recover from the illness",
                "explanationZh": "表示从疾病中恢复，用 recover from + illness。",
            }
        ],
    },
    "process": {
        "collocations": [
            ("a complex process", "复杂过程"),
            ("the learning process", "学习过程"),
            ("process data", "处理数据"),
            ("go through a process", "经历一个过程"),
        ],
        "grammarPatterns": [
            {
                "pattern": "process + data / information",
                "exampleEn": "The system can process large amounts of data.",
                "exampleZh": "该系统能够处理大量数据。",
            }
        ],
    },
    "recycle": {
        "collocations": [
            ("recycle waste", "回收废弃物"),
            ("recycle plastic", "回收塑料"),
            ("recycling programme", "回收项目"),
        ],
        "grammarPatterns": [
            {
                "pattern": "recycle + material",
                "exampleEn": "Many cities recycle paper, glass and plastic.",
                "exampleZh": "许多城市回收纸张、玻璃和塑料。",
            }
        ],
    },
    "succeed": {
        "collocations": [
            ("succeed in doing sth.", "成功做成某事"),
            ("eventually succeed", "最终成功"),
            ("succeed as leader", "继任为领导者"),
        ],
        "grammarPatterns": [
            {
                "pattern": "succeed in + doing",
                "exampleEn": "The researchers succeeded in identifying the cause.",
                "exampleZh": "研究人员成功找到了原因。",
            }
        ],
    },
    "exceed": {
        "collocations": [
            ("exceed the limit", "超过限制"),
            ("exceed expectations", "超出预期"),
            ("exceed the budget", "超出预算"),
        ],
        "grammarPatterns": [
            {
                "pattern": "exceed + amount / limit / expectation",
                "exampleEn": "The cost should not exceed the original budget.",
                "exampleZh": "成本不应超过原始预算。",
            }
        ],
    },
}


def relation_spec(
    word: str,
    target: str,
    relation_type: str,
    explanation: str,
    example_en: str,
    example_zh: str,
    source: str,
    strength: int = 4,
) -> dict[str, Any]:
    return {
        "word": word,
        "targetWord": target,
        "relationType": relation_type,
        "strength": strength,
        "explanationZh": explanation,
        "exampleEn": example_en,
        "exampleZh": example_zh,
        "source": source,
    }


RELATION_REFINEMENTS.extend(
    [
        relation_spec(
            "except",
            "accept",
            "spelling_confusable",
            "except 表示“除了”；accept 表示“接受”。两词拼写和读音接近，但词义完全不同。",
            "All applications were accepted except the late one.",
            "除了一份迟交的申请外，所有申请都被接受了。",
            "manual_spelling_confusable",
            5,
        ),
        relation_spec(
            "ensure",
            "insure",
            "spelling_confusable",
            "ensure 表示“确保”；insure 表示“投保”。学术写作中表示保证结果通常用 ensure。",
            "The policy aims to ensure safety, while the company insures the equipment.",
            "该政策旨在确保安全，而公司为设备投保。",
            "manual_spelling_confusable",
            5,
        ),
        relation_spec(
            "form",
            "from",
            "spelling_confusable",
            "form 表示“形式；形成”；from 表示“来自”。两词字母顺序接近，阅读时容易扫错。",
            "The material may form a layer from repeated heating.",
            "这种材料可能因反复加热而形成一层结构。",
            "manual_spelling_confusable",
        ),
        relation_spec(
            "economic",
            "economical",
            "spelling_confusable",
            "economic 多指经济、经济学相关；economical 表示节约的、划算的。",
            "Economic growth does not always mean an economical use of resources.",
            "经济增长并不总意味着资源使用节约。",
            "manual_spelling_confusable",
            5,
        ),
        relation_spec(
            "increase",
            "decrease",
            "antonym",
            "increase 表示增加；decrease 表示减少，是数量或程度变化上的反义关系。",
            "If demand increases, supply may decrease in the short term.",
            "如果需求增加，供应短期内可能减少。",
            "manual_antonym",
            5,
        ),
        relation_spec(
            "reduce",
            "increase",
            "antonym",
            "reduce 表示减少、降低；increase 表示增加、提高。",
            "The method can reduce costs and increase efficiency.",
            "这种方法可以降低成本并提高效率。",
            "manual_antonym",
            5,
        ),
        relation_spec(
            "include",
            "exclude",
            "antonym",
            "include 表示包括；exclude 表示排除、不包括。",
            "The survey includes adults but excludes children.",
            "这项调查包括成年人，但不包括儿童。",
            "manual_antonym",
            5,
        ),
        relation_spec(
            "superior",
            "inferior",
            "antonym",
            "superior 表示更好的、上级的；inferior 表示较差的、下级的。",
            "The new material is superior in strength but inferior in flexibility.",
            "这种新材料强度更好，但柔韧性较差。",
            "manual_antonym",
            5,
        ),
        relation_spec(
            "positive",
            "negative",
            "antonym",
            "positive 表示积极的、正面的或阳性的；negative 表示消极的、负面的或阴性的。",
            "The change had a positive effect in one area and a negative effect in another.",
            "这一变化在一个领域产生了正面影响，在另一个领域产生了负面影响。",
            "manual_antonym",
            5,
        ),
        relation_spec(
            "active",
            "inactive",
            "antonym",
            "active 表示活跃的、起作用的；inactive 表示不活跃的、不起作用的。",
            "Some organisms remain inactive until conditions become suitable.",
            "一些生物会保持不活跃，直到条件变得适宜。",
            "manual_antonym",
            5,
        ),
        relation_spec(
            "natural",
            "artificial",
            "antonym",
            "natural 表示自然的；artificial 表示人造的、非自然的。",
            "The study compared natural scents with artificial chemicals.",
            "该研究比较了天然气味和人工化学物质。",
            "manual_antonym",
            5,
        ),
        relation_spec(
            "ancient",
            "modern",
            "antonym",
            "ancient 表示古代的；modern 表示现代的。",
            "Ancient techniques can sometimes inspire modern design.",
            "古代技术有时能启发现代设计。",
            "manual_antonym",
        ),
        relation_spec(
            "prohibit",
            "permit",
            "antonym",
            "prohibit 表示禁止；permit 表示允许，常见于法规和政策语境。",
            "The rule prohibits smoking but permits food in the outdoor area.",
            "这条规定禁止吸烟，但允许在户外区域进食。",
            "manual_antonym",
            5,
        ),
        relation_spec(
            "appear",
            "disappear",
            "antonym",
            "appear 表示出现；disappear 表示消失。",
            "The signal may appear briefly and then disappear.",
            "信号可能短暂出现后消失。",
            "manual_antonym",
            5,
        ),
        relation_spec(
            "emerge",
            "disappear",
            "antonym",
            "emerge 表示出现、浮现；disappear 表示消失。",
            "New patterns emerge as old assumptions disappear.",
            "旧假设消失后，新的模式逐渐显现。",
            "manual_antonym",
        ),
        relation_spec(
            "cause",
            "effect",
            "contrast",
            "cause 是原因；effect 是结果或影响。两词不是普通反义词，而是因果链上的对应关系。",
            "Researchers tried to identify the cause of the effect.",
            "研究人员试图确定这一影响的原因。",
            "manual_semantic_contrast",
            5,
        ),
        relation_spec(
            "access",
            "accessible",
            "word_family",
            "accessible 是 access 的常见派生/同族词，表示可进入的、可获得的。",
            "Better access makes public services more accessible.",
            "更好的获取渠道使公共服务更容易获得。",
            "manual_word_family",
        ),
    ]
)


USAGE_REFINEMENTS.update(
    {
        "access": {
            "collocations": [
                ("access to information", "获取信息的机会"),
                ("easy access", "便利的进入/获取"),
                ("limited access", "有限访问权限"),
                ("gain access to", "获得进入/使用权限"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "access to + noun",
                    "exampleEn": "Students need access to reliable data.",
                    "exampleZh": "学生需要获取可靠数据的渠道。",
                }
            ],
        },
        "affect": {
            "collocations": [
                ("seriously affect", "严重影响"),
                ("directly affect", "直接影响"),
                ("affect behaviour", "影响行为"),
                ("affect the outcome", "影响结果"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "affect + object",
                    "exampleEn": "Temperature can affect the growth of plants.",
                    "exampleZh": "温度会影响植物生长。",
                }
            ],
            "commonErrors": [
                {
                    "wrong": "have affect on",
                    "correct": "have an effect on",
                    "explanationZh": "affect 通常作动词；effect 作名词时用于 have an effect on。",
                }
            ],
        },
        "effect": {
            "collocations": [
                ("a significant effect", "显著影响"),
                ("long-term effects", "长期影响"),
                ("have an effect on", "对……有影响"),
                ("side effect", "副作用"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "effect on + noun",
                    "exampleEn": "The policy had a clear effect on productivity.",
                    "exampleZh": "该政策对生产率产生了明显影响。",
                }
            ],
        },
        "ensure": {
            "collocations": [
                ("ensure safety", "确保安全"),
                ("ensure accuracy", "确保准确性"),
                ("ensure that", "确保……"),
                ("measures to ensure", "用于确保……的措施"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "ensure that + clause",
                    "exampleEn": "The system ensures that records are kept securely.",
                    "exampleZh": "该系统确保记录被安全保存。",
                }
            ],
        },
        "increase": {
            "collocations": [
                ("increase rapidly", "迅速增加"),
                ("increase significantly", "显著增加"),
                ("increase the risk", "增加风险"),
                ("an increase in demand", "需求增加"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "increase in + noun",
                    "exampleEn": "There was an increase in average temperature.",
                    "exampleZh": "平均温度有所上升。",
                }
            ],
        },
        "reduce": {
            "collocations": [
                ("reduce costs", "降低成本"),
                ("reduce the risk", "降低风险"),
                ("reduce emissions", "减少排放"),
                ("significantly reduce", "显著减少"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "reduce + object",
                    "exampleEn": "Better design can reduce energy use.",
                    "exampleZh": "更好的设计可以减少能源使用。",
                }
            ],
        },
        "include": {
            "collocations": [
                ("include evidence", "包括证据"),
                ("include a range of", "包括一系列……"),
                ("the sample includes", "样本包括……"),
                ("include both A and B", "同时包括 A 和 B"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "include + noun / -ing",
                    "exampleEn": "The project includes collecting data from several sites.",
                    "exampleZh": "该项目包括从多个地点收集数据。",
                }
            ],
        },
        "prohibit": {
            "collocations": [
                ("strictly prohibit", "严格禁止"),
                ("prohibit the use of", "禁止使用……"),
                ("law prohibits", "法律禁止"),
                ("prohibit someone from doing", "禁止某人做某事"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "prohibit sb. from doing sth.",
                    "exampleEn": "The rules prohibit visitors from feeding animals.",
                    "exampleZh": "规定禁止游客投喂动物。",
                }
            ],
        },
        "distinguish": {
            "collocations": [
                ("distinguish between A and B", "区分 A 和 B"),
                ("clearly distinguish", "清楚地区分"),
                ("distinguish one thing from another", "把一物与另一物区分开"),
                ("distinguishing feature", "区别性特征"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "distinguish between A and B",
                    "exampleEn": "Readers must distinguish between evidence and opinion.",
                    "exampleZh": "读者必须区分证据和观点。",
                }
            ],
        },
        "maintain": {
            "collocations": [
                ("maintain balance", "保持平衡"),
                ("maintain standards", "维持标准"),
                ("maintain a relationship", "维持关系"),
                ("maintain that", "坚持认为……"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "maintain that + clause",
                    "exampleEn": "Some researchers maintain that climate is a key factor.",
                    "exampleZh": "一些研究人员坚持认为气候是关键因素。",
                }
            ],
        },
        "determine": {
            "collocations": [
                ("determine the cause", "确定原因"),
                ("determine whether", "确定是否……"),
                ("largely determine", "在很大程度上决定"),
                ("factors determine", "因素决定……"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "determine whether / how / why + clause",
                    "exampleEn": "The study tried to determine whether the method was reliable.",
                    "exampleZh": "该研究试图确定这种方法是否可靠。",
                }
            ],
        },
        "conduct": {
            "collocations": [
                ("conduct research", "开展研究"),
                ("conduct a survey", "进行调查"),
                ("conduct an experiment", "进行实验"),
                ("conduct an interview", "进行访谈"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "conduct + research / survey / experiment",
                    "exampleEn": "The team conducted a survey of local residents.",
                    "exampleZh": "团队对当地居民进行了调查。",
                }
            ],
        },
        "assess": {
            "collocations": [
                ("assess the impact", "评估影响"),
                ("assess the risk", "评估风险"),
                ("carefully assess", "仔细评估"),
                ("assessment criteria", "评估标准"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "assess + object",
                    "exampleEn": "Experts assessed the impact of the new policy.",
                    "exampleZh": "专家评估了新政策的影响。",
                }
            ],
        },
        "examine": {
            "collocations": [
                ("examine evidence", "审视证据"),
                ("examine the relationship", "考察关系"),
                ("closely examine", "仔细检查/研究"),
                ("examine whether", "考察是否……"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "examine whether / how + clause",
                    "exampleEn": "The article examines how children acquire language.",
                    "exampleZh": "这篇文章考察儿童如何习得语言。",
                }
            ],
        },
        "emerge": {
            "collocations": [
                ("emerge from", "从……中出现"),
                ("a pattern emerges", "一种模式显现"),
                ("evidence emerges", "证据出现"),
                ("emerge as", "作为……出现/崭露头角"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "emerge from / as + noun",
                    "exampleEn": "A clear pattern emerged from the data.",
                    "exampleZh": "数据中显现出一种清晰模式。",
                }
            ],
        },
        "provide": {
            "collocations": [
                ("provide evidence", "提供证据"),
                ("provide access to", "提供……的访问/获取渠道"),
                ("provide support", "提供支持"),
                ("provide information", "提供信息"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "provide sb. with sth. / provide sth. for sb.",
                    "exampleEn": "The programme provides students with practical guidance.",
                    "exampleZh": "该项目为学生提供实用指导。",
                }
            ],
        },
        "develop": {
            "collocations": [
                ("develop a method", "开发一种方法"),
                ("develop skills", "培养技能"),
                ("develop rapidly", "快速发展"),
                ("develop into", "发展成……"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "develop into + noun",
                    "exampleEn": "The idea developed into a large research project.",
                    "exampleZh": "这个想法发展成了一个大型研究项目。",
                }
            ],
        },
        "apply": {
            "collocations": [
                ("apply a method", "应用一种方法"),
                ("apply to", "适用于……"),
                ("apply for", "申请……"),
                ("widely applied", "被广泛应用"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "apply to + noun / apply for + noun",
                    "exampleEn": "The same principle applies to many social situations.",
                    "exampleZh": "同一原则适用于许多社会情境。",
                }
            ],
        },
    }
)


USAGE_REFINEMENTS.update(
    {
        "economic": {
            "collocations": [
                ("economic growth", "经济增长"),
                ("economic development", "经济发展"),
                ("economic activity", "经济活动"),
                ("economic factor", "经济因素"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "economic + noun",
                    "exampleEn": "Economic growth may increase demand for energy.",
                    "exampleZh": "经济增长可能会增加能源需求。",
                }
            ],
        },
        "climate": {
            "collocations": [
                ("climate change", "气候变化"),
                ("a tropical climate", "热带气候"),
                ("climate conditions", "气候条件"),
                ("global climate", "全球气候"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "climate + noun / adjective + climate",
                    "exampleEn": "Climate conditions affect agricultural productivity.",
                    "exampleZh": "气候条件会影响农业生产率。",
                }
            ],
        },
        "data": {
            "collocations": [
                ("collect data", "收集数据"),
                ("analyse data", "分析数据"),
                ("reliable data", "可靠数据"),
                ("data suggest that", "数据表明……"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "data suggest / show / indicate that + clause",
                    "exampleEn": "The data suggest that the method is effective.",
                    "exampleZh": "数据显示这种方法是有效的。",
                }
            ],
        },
        "environment": {
            "collocations": [
                ("natural environment", "自然环境"),
                ("protect the environment", "保护环境"),
                ("environmental impact", "环境影响"),
                ("a changing environment", "不断变化的环境"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "environmental + noun",
                    "exampleEn": "The project assessed its environmental impact.",
                    "exampleZh": "该项目评估了自身的环境影响。",
                }
            ],
        },
        "productivity": {
            "collocations": [
                ("increase productivity", "提高生产率"),
                ("agricultural productivity", "农业生产率"),
                ("low productivity", "低生产率"),
                ("productivity growth", "生产率增长"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "productivity + noun / adjective + productivity",
                    "exampleEn": "Irrigation can improve agricultural productivity.",
                    "exampleZh": "灌溉可以提高农业生产率。",
                }
            ],
        },
        "advantage": {
            "collocations": [
                ("a clear advantage", "明显优势"),
                ("competitive advantage", "竞争优势"),
                ("take advantage of", "利用……"),
                ("advantage over", "相对于……的优势"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "advantage over + noun / take advantage of + noun",
                    "exampleEn": "The species has an advantage over its competitors.",
                    "exampleZh": "该物种相对于竞争者具有优势。",
                }
            ],
        },
        "condition": {
            "collocations": [
                ("under certain conditions", "在某些条件下"),
                ("living conditions", "生活条件"),
                ("ideal conditions", "理想条件"),
                ("conditions improve", "条件改善"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "under + adjective + conditions",
                    "exampleEn": "The plants grow well under ideal conditions.",
                    "exampleZh": "这些植物在理想条件下生长良好。",
                }
            ],
        },
        "context": {
            "collocations": [
                ("in this context", "在这种背景下"),
                ("social context", "社会背景"),
                ("historical context", "历史背景"),
                ("context of the study", "研究背景"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "in the context of + noun",
                    "exampleEn": "The behaviour is easier to understand in its social context.",
                    "exampleZh": "把这种行为放在社会背景中更容易理解。",
                }
            ],
        },
        "response": {
            "collocations": [
                ("in response to", "作为对……的回应"),
                ("immune response", "免疫反应"),
                ("a rapid response", "快速反应"),
                ("response to stress", "对压力的反应"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "response to + noun",
                    "exampleEn": "The response to stress varies among individuals.",
                    "exampleZh": "个体对压力的反应各不相同。",
                }
            ],
        },
        "effective": {
            "collocations": [
                ("an effective method", "有效方法"),
                ("highly effective", "非常有效"),
                ("effective way to", "……的有效方式"),
                ("effective in doing", "在做某事方面有效"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "effective in + -ing / effective way to do sth.",
                    "exampleEn": "The strategy is effective in reducing waste.",
                    "exampleZh": "这种策略在减少浪费方面有效。",
                }
            ],
        },
        "approach": {
            "collocations": [
                ("a new approach", "一种新方法"),
                ("an alternative approach", "另一种方法"),
                ("approach to a problem", "处理问题的方法"),
                ("adopt an approach", "采用一种方法"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "approach to + noun / -ing",
                    "exampleEn": "The article describes a new approach to teaching vocabulary.",
                    "exampleZh": "文章描述了一种教授词汇的新方法。",
                }
            ],
        },
        "strategy": {
            "collocations": [
                ("develop a strategy", "制定策略"),
                ("effective strategy", "有效策略"),
                ("learning strategy", "学习策略"),
                ("long-term strategy", "长期策略"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "strategy for + noun / -ing",
                    "exampleEn": "Students need a strategy for managing difficult texts.",
                    "exampleZh": "学生需要一种处理难文本的策略。",
                }
            ],
        },
        "essential": {
            "collocations": [
                ("essential for", "对……必不可少"),
                ("an essential part", "重要组成部分"),
                ("essential information", "关键信息"),
                ("it is essential that", "……是必要的"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "essential for + noun / essential to do sth.",
                    "exampleEn": "Accurate data are essential for reliable conclusions.",
                    "exampleZh": "准确数据对于可靠结论必不可少。",
                }
            ],
        },
        "encourage": {
            "collocations": [
                ("encourage students to", "鼓励学生……"),
                ("encourage growth", "促进增长"),
                ("strongly encourage", "强烈鼓励"),
                ("encourage participation", "鼓励参与"),
            ],
            "grammarPatterns": [
                {
                    "pattern": "encourage sb. to do sth.",
                    "exampleEn": "Teachers can encourage students to read more widely.",
                    "exampleZh": "教师可以鼓励学生更广泛地阅读。",
                }
            ],
        },
    }
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def relation_id(word: str, relation_type: str, target: str) -> str:
    return f"lex_word_{word}_{relation_type}_{target}".replace(" ", "_").replace("-", "_").lower()


def refine_relations() -> int:
    suggestions = read_jsonl(SUGGESTIONS_PATH)
    by_id = {row["_id"]: row for row in suggestions}
    wordbook = read_jsonl(DATA_DIR / "wordbook_words.json")
    word_ids = {row["word"]: row["wordId"] for row in wordbook}
    added = 0
    for spec in RELATION_REFINEMENTS:
        if spec["word"] not in word_ids:
            continue
        rid = relation_id(spec["word"], spec["relationType"], spec["targetWord"])
        if rid in by_id:
            continue
        by_id[rid] = {
            "_id": rid,
            "wordId": word_ids[spec["word"]],
            "word": spec["word"],
            "targetWordId": word_ids.get(spec["targetWord"]),
            "targetWord": spec["targetWord"],
            "targetInWordbook": spec["targetWord"] in word_ids,
            "targetInGlobalWords": False,
            "relationType": spec["relationType"],
            "strength": spec["strength"],
            "explanationZh": spec["explanationZh"],
            "exampleEn": spec["exampleEn"],
            "exampleZh": spec["exampleZh"],
            "source": spec["source"],
            "status": "draft",
            "reviewStatus": "ai_suggested_pending_human_review",
            "createdAt": None,
            "updatedAt": None,
        }
        added += 1
    rows = sorted(by_id.values(), key=lambda item: (item["word"], item["relationType"], item["targetWord"]))
    write_jsonl(SUGGESTIONS_PATH, rows)
    return added


def has_text(items: list[dict[str, Any]], key: str, text: str) -> bool:
    return any(str(item.get(key) or "").strip().lower() == text.lower() for item in items)


def refine_learning() -> dict[str, int]:
    rows = read_jsonl(LEARNING_PATH)
    by_word = {row["word"]: row for row in rows}
    stats = {"collocationsAdded": 0, "grammarAdded": 0, "commonErrorsAdded": 0}
    for word, spec in USAGE_REFINEMENTS.items():
        row = by_word.get(word)
        if not row:
            continue
        collocations = row.setdefault("collocations", [])
        for text, translation in spec.get("collocations", []):
            if not has_text(collocations, "text", text):
                collocations.append({"text": text, "translationZh": translation, "status": "draft"})
                stats["collocationsAdded"] += 1
        grammar = row.setdefault("grammarPatterns", [])
        for item in spec.get("grammarPatterns", []):
            if not has_text(grammar, "pattern", item["pattern"]):
                grammar.append({**item, "status": "draft"})
                stats["grammarAdded"] += 1
        errors = row.setdefault("commonErrors", [])
        for item in spec.get("commonErrors", []):
            if not has_text(errors, "wrong", item["wrong"]):
                errors.append({**item, "status": "draft"})
                stats["commonErrorsAdded"] += 1
        provenance = row.setdefault("provenance", {})
        refinements = provenance.setdefault("refinements", [])
        if "focused_inventory_refinement" not in refinements:
            refinements.append("focused_inventory_refinement")
    write_jsonl(LEARNING_PATH, rows)
    return stats


def main() -> None:
    relations_added = refine_relations()
    usage_stats = refine_learning()
    report = {"relationsAdded": relations_added, **usage_stats}
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
