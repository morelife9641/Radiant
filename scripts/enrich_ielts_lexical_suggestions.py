#!/usr/bin/env python3
"""Add high-confidence lexical relation suggestions for the IELTS wordbook.

This creates a reviewable sidecar file instead of forcing every suggestion into
published word_relations. Some targets are outside the current wordbook/global
words import, so the sidecar keeps targetWord text even when targetWordId is
not available.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
ECDICT_PATH = ROOT / "ECDICT-master/ecdict.csv"
OUT_PATH = DATA_DIR / "word_lexical_suggestions.json"
REPORT_PATH = DATA_DIR / "word_lexical_suggestions_report.json"


NEGATIVE_PREFIX_PAIRS = {
    "valid": ["invalid"],
    "appropriate": ["inappropriate"],
    "effective": ["ineffective"],
    "efficient": ["inefficient"],
    "legal": ["illegal"],
    "reliable": ["unreliable"],
}

NEGATIVE_PAIR_CONTENT = {
    ("valid", "invalid"): {
        "explanationZh": "valid 表示理由、证据、票据或方法“有效、成立、有根据”；invalid 表示“无效、站不住脚、不成立”。",
        "exampleEn": "The ticket is valid today, but it will become invalid after midnight.",
        "exampleZh": "这张票今天有效，但午夜之后就会失效。",
    },
    ("appropriate", "inappropriate"): {
        "explanationZh": "appropriate 表示“合适、得体、符合场景”；inappropriate 表示“不合适、不得体、不适合该场景”。",
        "exampleEn": "Formal language is appropriate in an academic essay, while slang may be inappropriate.",
        "exampleZh": "正式语言适合学术作文，而俚语可能不合适。",
    },
    ("effective", "ineffective"): {
        "explanationZh": "effective 表示“有效果、能达到目的”；ineffective 表示“无效、效果差、不能达到目的”。",
        "exampleEn": "The policy was effective in reducing waste, but the earlier campaign was ineffective.",
        "exampleZh": "这项政策有效减少了浪费，但早先的宣传活动效果不佳。",
    },
    ("efficient", "inefficient"): {
        "explanationZh": "efficient 表示“高效、少浪费”；inefficient 表示“低效、浪费时间或资源”。",
        "exampleEn": "Public transport can be efficient in dense cities, but inefficient in remote areas.",
        "exampleZh": "公共交通在高密度城市可能很高效，但在偏远地区可能效率低。",
    },
    ("legal", "illegal"): {
        "explanationZh": "legal 表示“合法的、法律允许的”；illegal 表示“非法的、法律禁止的”。",
        "exampleEn": "The trade is legal with a permit, but illegal without one.",
        "exampleZh": "有许可证时这种交易是合法的，没有许可证则是非法的。",
    },
    ("reliable", "unreliable"): {
        "explanationZh": "reliable 表示“可靠、可信赖”；unreliable 表示“不可靠、不能稳定信任”。",
        "exampleEn": "A reliable source can support the claim, but an unreliable source weakens it.",
        "exampleZh": "可靠来源可以支持这个说法，不可靠来源会削弱它。",
    },
}

MANUAL_RELATIONS = [
    {
        "word": "landmark",
        "targetWord": "milestone",
        "relationType": "near_synonym",
        "strength": 5,
        "explanationZh": "landmark 可指地标，也可指历史或发展中的“里程碑事件”；milestone 更直接表示人生、项目或历史进程中的重要节点。",
        "exampleEn": "The discovery was a landmark in medical research and a milestone for the whole project.",
        "exampleZh": "这一发现是医学研究中的标志性事件，也是整个项目的重要里程碑。",
        "source": "manual_curated",
    },
    {
        "word": "valid",
        "targetWord": "legitimate",
        "relationType": "near_synonym",
        "strength": 4,
        "explanationZh": "valid 和 legitimate 都可表示“正当、成立、可接受”。valid 更常说理由、证据、票据或方法有效；legitimate 更强调符合法律、规则或正当性。",
        "exampleEn": "The complaint is valid because it is based on evidence, and legitimate because the rules allow it.",
        "exampleZh": "这个投诉有证据支撑，所以 valid；规则允许提出，所以也具有 legitimate 的正当性。",
        "source": "manual_curated",
    },
    {
        "word": "valid",
        "targetWord": "reasonable",
        "relationType": "near_synonym",
        "strength": 3,
        "explanationZh": "valid 强调逻辑、证据或法律上成立；reasonable 强调合情合理、不过分。valid reason 和 reasonable reason 都可说，但侧重点不同。",
        "exampleEn": "The reason is valid in law, but the request also needs to be reasonable in practice.",
        "exampleZh": "这个理由在法律上成立，但这个请求在实际操作中也需要合理。",
        "source": "manual_curated",
    },
    {
        "word": "valid",
        "targetWord": "unreliable",
        "relationType": "contrast",
        "strength": 3,
        "explanationZh": "valid 强调论证、证据、票据或方法“有效、有根据”；unreliable 强调信息、来源或方法“不可靠”。二者常在 evidence/data/source 语境中形成对比，但不是所有语境下的严格反义。",
        "exampleEn": "A valid conclusion needs reliable evidence; unreliable data can make the conclusion questionable.",
        "exampleZh": "有效的结论需要可靠证据；不可靠的数据会让结论变得可疑。",
        "source": "manual_curated",
    },
    {
        "word": "valid",
        "targetWord": "unstable",
        "relationType": "context_contrast",
        "strength": 2,
        "explanationZh": "valid 说的是结论、理由、票据或方法是否成立；unstable 说的是系统、状态或结果是否稳定。它们有时都可用于评价研究结果，但语义焦点不同。",
        "exampleEn": "The method may be valid, but the results are unstable across repeated trials.",
        "exampleZh": "这个方法可能是有效的，但结果在重复试验中并不稳定。",
        "source": "manual_curated",
    },
    {
        "word": "subject",
        "targetWord": "object",
        "relationType": "contrast",
        "strength": 5,
        "explanationZh": "subject 和 object 在语法中分别指“主语”和“宾语”；在哲学或认知语境中，subject 偏主体，object 偏客体/对象。",
        "exampleEn": "In the sentence, the subject performs the action, while the object receives it.",
        "exampleZh": "在句子中，主语发出动作，而宾语承受动作。",
        "source": "manual_curated",
        "bidirectional": True,
    },
]

SPELLING_CONFUSABLES = [
    {
        "word": "content",
        "targetWord": "contend",
        "explanationZh": "content 可作“内容”，也可表示“满意”；contend 表示“声称、争辩、竞争”。两词拼写接近，但词义和读音重音不同。",
        "exampleEn": "The article's content is clear, but critics contend that its evidence is weak.",
        "exampleZh": "这篇文章的内容很清楚，但批评者声称它的证据不足。",
    },
    {
        "word": "affect",
        "targetWord": "effect",
        "explanationZh": "affect 多作动词，表示“影响”；effect 多作名词，表示“影响、效果”，也可作动词表示“实现”。",
        "exampleEn": "The weather can affect mood, and the effect may last all day.",
        "exampleZh": "天气会影响情绪，而这种影响可能持续一整天。",
    },
    {
        "word": "adapt",
        "targetWord": "adopt",
        "explanationZh": "adapt 表示“适应、改编”；adopt 表示“采纳、收养”。两词只差一个字母，雅思阅读中很容易看错。",
        "exampleEn": "Schools may adapt materials for local needs and adopt a new policy later.",
        "exampleZh": "学校可能会根据本地需求改编材料，之后再采纳一项新政策。",
    },
    {
        "word": "principle",
        "targetWord": "principal",
        "explanationZh": "principle 是“原则、原理”；principal 可作“主要的”，也可指“校长、本金”。",
        "exampleEn": "The principal explained the principle behind the school rule.",
        "exampleZh": "校长解释了这条校规背后的原则。",
    },
    {
        "word": "cite",
        "targetWord": "site",
        "explanationZh": "cite 表示“引用、引证”；site 表示“地点、场址、网站”。两词读音相同，拼写和含义不同。",
        "exampleEn": "Researchers cite the report when describing the archaeological site.",
        "exampleZh": "研究者在描述这个考古遗址时引用了那份报告。",
    },
    {
        "word": "cite",
        "targetWord": "sight",
        "explanationZh": "cite 表示“引用”；sight 表示“视力、景象”。两词读音相同，需按语境区分。",
        "exampleEn": "The guide may cite old records, but the ruins are still an impressive sight.",
        "exampleZh": "导游可能会引用旧记录，但这些遗迹本身仍是一番壮观景象。",
    },
]


CURATED_NEAR_SYNONYMS = {
    "presumably": ["probably", "possibly", "maybe", "apparently"],
    "memorise": ["memorize", "remember", "learn by heart"],
    "thereby": ["thus", "therefore", "consequently"],
    "feedback": ["response", "reaction", "comment", "input", "outcome"],
    "ecology": ["environmental science", "ecosystem study"],
    "merely": ["only", "simply", "just"],
    "guidance": ["advice", "direction", "instruction"],
    "mere": ["simple", "only", "bare"],
    "alarm": ["warning", "alert", "signal"],
    "presence": ["existence", "appearance", "attendance"],
    "attention": ["focus", "notice", "awareness"],
    "predator": ["hunter", "carnivore"],
    "incur": ["suffer", "bring upon oneself", "be subject to"],
    "naive": ["inexperienced", "unsophisticated", "innocent"],
    "enable": ["allow", "permit", "make possible"],
    "throughout": ["during", "all through", "across"],
    "facilitate": ["help", "assist", "enable"],
    "locate": ["find", "place", "situate"],
    "challenge": ["difficulty", "problem", "test"],
    "understanding": ["comprehension", "insight", "awareness"],
    "routine": ["regular", "usual", "standard"],
    "evolve": ["develop", "progress", "change"],
    "behave": ["act", "conduct oneself", "function"],
    "necessarily": ["inevitably", "unavoidably", "certainly"],
    "mosquito": ["gnat", "biting insect"],
    "inspiration": ["motivation", "stimulus", "idea"],
    "anecdote": ["story", "account", "episode"],
    "epidemic": ["outbreak", "pandemic", "spread"],
    "industrialise": ["industrialize", "develop industry"],
    "latitude": ["parallel", "geographical latitude"],
    "annual": ["yearly", "once-a-year"],
    "otherwise": ["or else", "if not", "differently"],
    "organism": ["living thing", "life form"],
    "abundance": ["plenty", "profusion", "large amount"],
    "workforce": ["staff", "employees", "labour force"],
    "academic": ["scholarly", "educational", "university-related"],
    "climate": ["weather pattern", "atmosphere", "conditions"],
    "impoverished": ["poor", "deprived", "destitute"],
    "minimum": ["least", "lowest", "smallest"],
    "limited": ["restricted", "finite", "narrow"],
    "chill": ["cold", "coolness", "cool"],
    "inactive": ["dormant", "idle", "not active"],
    "seasonal": ["periodic", "cyclical", "season-related"],
    "tropical": ["equatorial", "hot-climate"],
    "superior": ["better", "higher", "greater"],
    "colony": ["settlement", "community", "group"],
    "institution": ["organisation", "establishment", "body"],
    "access": ["entry", "approach", "availability"],
    "improvement": ["enhancement", "progress", "advance"],
    "environment": ["surroundings", "habitat", "conditions"],
    "beyond": ["past", "outside", "more than"],
    "given": ["provided", "specified", "particular"],
    "gear": ["equipment", "apparatus", "kit"],
    "agriculture": ["farming", "cultivation"],
    "provided": ["if", "on condition that", "supplied"],
    "irrigation": ["watering", "water supply"],
    "productivity": ["output", "efficiency", "yield"],
    "poverty": ["deprivation", "destitution", "need"],
    "climatic": ["climate-related", "meteorological"],
    "zoological": ["animal-related", "zoology-related"],
    "affluent": ["wealthy", "prosperous", "rich"],
    "domesticate": ["tame", "cultivate", "adapt for human use"],
    "dissemination": ["spread", "distribution", "circulation"],
    "livestock": ["farm animals", "cattle", "stock"],
    "motive": ["reason", "incentive", "motivation"],
    "correlation": ["relationship", "association", "connection"],
    "geographical": ["spatial", "regional", "geographic"],
    "equator": ["zero latitude", "equatorial line"],
    "hemisphere": ["half sphere", "half of the earth"],
    "avoid": ["prevent", "evade", "escape"],
    "priority": ["precedence", "importance", "preference"],
    "affect": ["influence", "impact", "change"],
    "maternal": ["motherly", "maternal-related"],
    "context": ["setting", "background", "circumstances"],
    "observation": ["watching", "monitoring", "remark"],
    "commit": ["devote", "pledge", "carry out"],
    "agenda": ["schedule", "programme", "plan"],
    "endorse": ["support", "approve", "back"],
    "emphasize": ["stress", "highlight", "underline"],
    "acceptable": ["satisfactory", "permissible", "adequate"],
    "parental": ["parent-related", "maternal or paternal"],
    "emotional": ["affective", "feeling-related"],
    "physical": ["bodily", "material", "tangible"],
    "response": ["reaction", "reply", "answer"],
    "advanced": ["developed", "sophisticated", "high-level"],
    "refusal": ["rejection", "denial", "decline"],
    "viewpoint": ["perspective", "opinion", "standpoint"],
    "strategy": ["plan", "approach", "method"],
    "ultimately": ["finally", "eventually", "in the end"],
    "reinforcement": ["strengthening", "support", "consolidation"],
    "floral": ["flower-related", "botanical"],
    "attract": ["draw", "appeal to", "interest"],
    "pollinate": ["fertilise", "transfer pollen"],
    "biological": ["living", "life-related", "organic"],
    "emit": ["release", "give off", "discharge"],
    "organic": ["natural", "biological", "carbon-based"],
    "pine": ["pine tree", "conifer"],
    "burrow": ["tunnel", "hole", "dig"],
    "oxygen": ["O2"],
    "ancient": ["old", "historic", "archaic"],
    "deter": ["discourage", "prevent", "inhibit"],
    "profile": ["outline", "description", "portrait"],
    "nocturnal": ["night-active", "night-time"],
    "herbivore": ["plant eater"],
    "mite": ["tiny arachnid", "small parasite"],
    "predatory": ["hunting", "carnivorous"],
    "prey": ["victim", "quarry"],
    "signature": ["distinctive mark", "identifying feature"],
    "hatch": ["emerge", "incubate", "come out"],
    "similarly": ["likewise", "in the same way", "equally"],
    "onslaught": ["attack", "assault", "invasion"],
    "antiseptic": ["disinfectant", "sterile agent"],
    "efficiency": ["effectiveness", "productivity", "performance"],
    "optimum": ["best", "ideal", "optimal"],
    "emission": ["release", "discharge", "output"],
    "considerable": ["substantial", "significant", "large"],
    "introduce": ["present", "bring in", "launch"],
    "exacerbate": ["worsen", "aggravate", "intensify"],
    "breed": ["reproduce", "raise", "produce"],
    "solution": ["answer", "remedy", "resolution"],
    "adequate": ["sufficient", "enough", "acceptable"],
    "drawback": ["disadvantage", "weakness", "downside"],
    "genetic": ["hereditary", "inherited", "gene-related"],
    "consequent": ["resulting", "following", "subsequent"],
    "enhance": ["improve", "strengthen", "increase"],
    "spray": ["mist", "sprinkle", "jet"],
    "toxic": ["poisonous", "harmful", "venomous"],
    "manipulate": ["control", "handle", "influence"],
    "frequency": ["rate", "regularity", "occurrence"],
    "ornamental": ["decorative", "adorned"],
    "aesthetic": ["artistic", "visual", "beauty-related"],
    "unfortunately": ["regrettably", "sadly"],
    "traditional": ["conventional", "customary", "established"],
    "sacrifice": ["give up", "forgo", "surrender"],
    "desirable": ["attractive", "wanted", "preferable"],
    "target": ["aim", "goal", "objective"],
    "preliminary": ["initial", "early", "introductory"],
    "technical": ["specialised", "technological", "practical"],
    "threshold": ["limit", "boundary", "cutoff"],
    "organ": ["body part", "instrument", "agency"],
    "gland": ["secretory organ"],
    "supersede": ["replace", "displace", "succeed"],
    "creation": ["formation", "production", "making"],
    "derive": ["obtain", "come from", "deduce"],
    "handle": ["manage", "deal with", "control"],
    "frame": ["structure", "framework", "shape"],
    "resistant": ["immune", "impervious", "opposed"],
    "switch": ["change", "shift", "toggle"],
    "household": ["domestic", "family", "home"],
    "electrical": ["electric", "power-related"],
    "waterproof": ["water-resistant", "impermeable"],
    "friction": ["resistance", "rubbing"],
    "domestic": ["household", "home", "internal"],
    "insulation": ["protection", "padding", "thermal barrier"],
    "fibre": ["fiber", "strand", "filament"],
    "pump": ["push", "circulate", "device"],
    "stretch": ["extend", "lengthen", "expand"],
    "glossy": ["shiny", "polished", "lustrous"],
    "recycle": ["reuse", "reprocess", "recover"],
    "treatment": ["therapy", "handling", "processing"],
    "apart": ["separate", "aside", "away"],
    "disintegrate": ["break down", "fall apart", "decompose"],
    "stem": ["stalk", "source", "originate"],
    "comparatively": ["relatively", "fairly", "somewhat"],
    "refer": ["mention", "allude", "direct"],
    "weaken": ["undermine", "reduce", "impair"],
    "drought": ["dry spell", "water shortage"],
    "deficit": ["shortfall", "deficiency", "lack"],
    "meanwhile": ["meantime", "at the same time"],
    "ecological": ["environmental", "ecosystem-related"],
    "analyse": ["analyze", "examine", "study"],
    "impose": ["enforce", "place", "inflict"],
    "global": ["worldwide", "international", "planetary"],
    "glacier": ["ice sheet", "ice mass"],
    "due": ["because of", "expected", "owed"],
    "crisis": ["emergency", "turning point"],
    "decade": ["ten years"],
    "cumulative": ["accumulated", "combined", "total"],
    "mass": ["amount", "body", "bulk"],
    "volume": ["amount", "quantity", "capacity"],
    "dynamic": ["changing", "active", "energetic"],
    "undoubtedly": ["certainly", "definitely", "surely"],
    "atmospheric": ["air-related", "meteorological"],
    "sector": ["area", "field", "industry"],
    "therefore": ["thus", "consequently", "hence"],
    "counter": ["oppose", "respond", "offset"],
    "upgrade": ["improve", "update", "enhance"],
    "for instance": ["for example", "such as"],
    "tackle": ["address", "handle", "deal with"],
    "resilience": ["toughness", "resistance", "capacity to recover"],
    "ecosystem": ["ecological system", "habitat network"],
    "adaptation": ["adjustment", "modification"],
    "ratio": ["proportion", "rate"],
    "productive": ["fruitful", "efficient", "useful"],
    "spite": ["malice", "ill will"],
    "insurance": ["coverage", "protection"],
    "advertise": ["promote", "publicise", "market"],
    "agency": ["organisation", "bureau", "firm"],
    "percentage": ["proportion", "share", "rate"],
    "corporate": ["company", "business", "commercial"],
    "lower": ["reduce", "decrease", "drop"],
    "proportion": ["ratio", "share", "percentage"],
    "judgment": ["assessment", "decision", "opinion"],
    "graduate": ["alumnus", "complete studies"],
    "scale": ["size", "level", "range"],
    "attractive": ["appealing", "desirable", "beautiful"],
    "innovation": ["invention", "new idea", "novelty"],
    "intellectual": ["academic", "mental", "scholarly"],
    "tempt": ["entice", "attract", "lure"],
    "transition": ["change", "shift", "conversion"],
    "survive": ["endure", "remain alive", "persist"],
    "compare": ["contrast", "evaluate", "liken"],
    "deposit": ["layer", "sediment", "put down"],
    "impossible": ["unachievable", "not possible"],
    "mineral": ["ore", "inorganic substance"],
    "concentration": ["amount", "density", "focus"],
    "commercial": ["business", "market-oriented"],
    "textile": ["fabric", "cloth"],
    "detergent": ["cleanser", "washing agent"],
    "influential": ["powerful", "important", "persuasive"],
    "portable": ["movable", "transportable"],
    "surface": ["outer layer", "exterior"],
    "image": ["picture", "impression", "representation"],
    "fuel": ["energy source", "power source"],
    "construction": ["building", "creation", "structure"],
    "religion": ["faith", "belief system"],
    "ritual": ["ceremony", "custom", "rite"],
    "purify": ["cleanse", "filter", "make pure"],
    "elaborate": ["detailed", "complex", "develop"],
    "malevolent": ["evil", "malicious", "hostile"],
    "restriction": ["limit", "constraint", "control"],
    "reference": ["mention", "citation", "source"],
    "deficiency": ["lack", "shortage", "deficit"],
    "highlight": ["emphasize", "stress", "underline"],
    "inadequate": ["insufficient", "poor", "not enough"],
    "healing": ["recovery", "curing", "repair"],
    "resistance": ["opposition", "resilience", "friction"],
    "senior": ["older", "higher-ranking", "advanced"],
    "sustainable": ["lasting", "viable", "eco-friendly"],
    "consumer": ["buyer", "customer", "user"],
    "durable": ["long-lasting", "hard-wearing", "strong"],
    "entail": ["involve", "require", "mean"],
    "inevitable": ["unavoidable", "certain", "inescapable"],
    "disposal": ["removal", "throwing away", "management"],
    "resource": ["asset", "supply", "material"],
    "underlying": ["basic", "fundamental", "hidden"],
    "symbolism": ["symbolic meaning", "representation"],
    "specialist": ["expert", "professional"],
    "manufacturer": ["producer", "maker"],
    "connection": ["link", "relationship", "association"],
    "irresistible": ["compelling", "tempting", "overwhelming"],
    "renew": ["restore", "restart", "revive"],
    "excitement": ["enthusiasm", "thrill", "stimulation"],
    "utility": ["usefulness", "function", "service"],
    "depletion": ["reduction", "exhaustion", "drain"],
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def load_ecdict_words() -> set[str]:
    words: set[str] = set()
    with ECDICT_PATH.open(encoding="utf-8", errors="ignore", newline="") as file:
        for row in csv.DictReader(file):
            word = (row.get("word") or "").strip().lower()
            if word:
                words.add(word)
    return words


def normalize_term(term: str) -> str:
    term = term.strip().lower()
    term = term.replace("（", "(").replace("）", ")")
    term = re.sub(r"\([^)]*\)", "", term)
    term = term.strip(" .;:，,、")
    return re.sub(r"\s+", " ", term)


def split_group_terms(text: str) -> list[str]:
    text = text.replace("（", "(").replace("）", ")")
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
        if ch in {",", "，", "、"} and depth == 0:
            part = "".join(buf).strip()
            if part:
                parts.append(part)
            buf = []
        else:
            buf.append(ch)
    last = "".join(buf).strip()
    if last:
        parts.append(last)

    raw_terms: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        raw_terms.append(part)
        match = re.search(r"\(([^)]*)\)", part)
        if match:
            raw_terms.extend([item.strip() for item in re.split(r"[,，、]", match.group(1)) if item.strip()])
    out: list[str] = []
    seen: set[str] = set()
    for item in raw_terms:
        norm = normalize_term(item)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
    return out


def parse_resemble_groups(path: Path) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for index, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("%"):
            if current and len(current.get("terms", [])) >= 2:
                groups.append(current)
            title = stripped.lstrip("%").strip()
            current = {
                "sourceIndex": index,
                "title": title,
                "terms": split_group_terms(title),
                "notes": {},
                "summaryZh": "",
            }
            continue
        if current is None:
            continue
        if stripped.startswith("-") and ":" in stripped:
            word, note = stripped[1:].split(":", 1)
            norm = normalize_term(word)
            if norm:
                current["notes"][norm] = note.strip().rstrip("。；;") + "。"
        elif "这组词" in stripped and not current.get("summaryZh"):
            current["summaryZh"] = stripped
    if current and len(current.get("terms", [])) >= 2:
        groups.append(current)
    return groups


def make_id(word: str, relation_type: str, target: str) -> str:
    raw = f"lex_word_{word}_{relation_type}_{target}".lower()
    return re.sub(r"[^a-z0-9]+", "_", raw).strip("_")


def make_relation(
    word: str,
    target: str,
    relation_type: str,
    words_by_norm: dict[str, dict[str, Any]],
    wordbook_by_norm: dict[str, dict[str, Any]],
    explanation_zh: str,
    example_en: str,
    example_zh: str,
    source: str,
    strength: int = 4,
) -> dict[str, Any]:
    word_doc = words_by_norm.get(word)
    target_doc = words_by_norm.get(target)
    return {
        "_id": make_id(word, relation_type, target),
        "wordId": (wordbook_by_norm.get(word) or {}).get("wordId") or (word_doc or {}).get("_id") or f"word_{word}",
        "word": word,
        "targetWordId": (target_doc or {}).get("_id"),
        "targetWord": target,
        "targetInWordbook": target in wordbook_by_norm,
        "targetInGlobalWords": bool(target_doc),
        "relationType": relation_type,
        "strength": strength,
        "explanationZh": explanation_zh,
        "exampleEn": example_en,
        "exampleZh": example_zh,
        "source": source,
        "status": "draft",
        "reviewStatus": "ai_suggested_pending_human_review",
        "createdAt": None,
        "updatedAt": None,
    }


def main() -> None:
    wordbook_words = read_jsonl(DATA_DIR / "wordbook_words.json")
    global_words = read_jsonl(WORDS_PATH)
    ecdict_words = load_ecdict_words()

    wordbook_by_norm = {row["normalized"].lower(): row for row in wordbook_words}
    words_by_norm = {row.get("normalized", row.get("word", "")).lower(): row for row in global_words}

    suggestions: dict[str, dict[str, Any]] = {}

    resemble_groups = parse_resemble_groups(ECDICT_PATH.with_name("resemble.txt"))
    resemble_added = 0
    for group in resemble_groups:
        if "这组词" not in (group.get("summaryZh") or ""):
            continue
        terms = [term for term in group["terms"] if term]
        wordbook_terms = [term for term in terms if term in wordbook_by_norm]
        if not wordbook_terms:
            continue
        for word in wordbook_terms:
            for target in terms:
                if target == word:
                    continue
                note_word = group["notes"].get(word, "")
                note_target = group["notes"].get(target, "")
                explanation = (
                    f"{word}: {note_word or '与本组词语义接近，需结合语境区分。'}"
                    f"{target}: {note_target or '与本组词语义接近，需结合语境区分。'}"
                )
                relation = make_relation(
                    word=word,
                    target=target,
                    relation_type="near_synonym",
                    words_by_norm=words_by_norm,
                    wordbook_by_norm=wordbook_by_norm,
                    explanation_zh=explanation,
                    example_en=f"Compare \"{word}\" with \"{target}\" in this word family; the exact choice depends on context.",
                    example_zh=f"{word} 和 {target} 属于近义/同类表达，阅读中要根据具体语境区分。",
                    source=f"ecdict_resemble:{group['sourceIndex']}",
                    strength=3,
                )
                relation["groupTitle"] = group["title"]
                relation["groupSummaryZh"] = group.get("summaryZh") or ""
                suggestions.setdefault(relation["_id"], relation)
                resemble_added += 1

    for word, targets in NEGATIVE_PREFIX_PAIRS.items():
        if word not in wordbook_by_norm:
            continue
        for target in targets:
            if target not in ecdict_words and target not in words_by_norm:
                continue
            relation = make_relation(
                word=word,
                target=target,
                relation_type="antonym",
                words_by_norm=words_by_norm,
                wordbook_by_norm=wordbook_by_norm,
                explanation_zh=NEGATIVE_PAIR_CONTENT.get((word, target), {}).get(
                    "explanationZh",
                    f"{word} 表示肯定意义；{target} 表示对应的否定意义。",
                ),
                example_en=NEGATIVE_PAIR_CONTENT.get((word, target), {}).get(
                    "exampleEn",
                    f"Use {word} for the positive form and {target} for the negative form.",
                ),
                example_zh=NEGATIVE_PAIR_CONTENT.get((word, target), {}).get(
                    "exampleZh",
                    f"{word} 是肯定形式，{target} 是对应的否定形式。",
                ),
                source="negative_prefix_rule",
                strength=5,
            )
            suggestions[relation["_id"]] = relation

    for spec in MANUAL_RELATIONS:
        word = spec["word"]
        target = spec["targetWord"]
        if word not in wordbook_by_norm:
            continue
        relation = make_relation(
            word=word,
            target=target,
            relation_type=spec["relationType"],
            words_by_norm=words_by_norm,
            wordbook_by_norm=wordbook_by_norm,
            explanation_zh=spec["explanationZh"],
            example_en=spec["exampleEn"],
            example_zh=spec["exampleZh"],
            source=spec["source"],
            strength=spec.get("strength", 4),
        )
        suggestions[relation["_id"]] = relation
        if spec.get("bidirectional") and target in wordbook_by_norm:
            reverse = make_relation(
                word=target,
                target=word,
                relation_type=spec["relationType"],
                words_by_norm=words_by_norm,
                wordbook_by_norm=wordbook_by_norm,
                explanation_zh=spec["explanationZh"],
                example_en=spec["exampleEn"],
                example_zh=spec["exampleZh"],
                source=spec["source"],
                strength=spec.get("strength", 4),
            )
            suggestions[reverse["_id"]] = reverse

    for word, targets in CURATED_NEAR_SYNONYMS.items():
        if word not in wordbook_by_norm:
            continue
        for target in targets:
            relation = make_relation(
                word=word,
                target=target,
                relation_type="near_synonym",
                words_by_norm=words_by_norm,
                wordbook_by_norm=wordbook_by_norm,
                explanation_zh=f"{word} 与 {target} 在雅思阅读语境中可作为近义或同类表达参考；具体替换需看词性和上下文。",
                example_en=f"In context, \"{word}\" can be compared with \"{target}\", but the exact choice depends on grammar and meaning.",
                example_zh=f"在语境中，{word} 可与 {target} 对照学习，但是否能替换要看词性和上下文。",
                source="curated_gap_fill",
                strength=4,
            )
            suggestions[relation["_id"]] = relation

    for spec in SPELLING_CONFUSABLES:
        word = spec["word"]
        target = spec["targetWord"]
        if word not in wordbook_by_norm:
            continue
        relation = make_relation(
            word=word,
            target=target,
            relation_type="spelling_confusable",
            words_by_norm=words_by_norm,
            wordbook_by_norm=wordbook_by_norm,
            explanation_zh=spec["explanationZh"],
            example_en=spec["exampleEn"],
            example_zh=spec["exampleZh"],
            source="manual_spelling_confusable",
            strength=5,
        )
        suggestions[relation["_id"]] = relation
        if target in wordbook_by_norm:
            reverse = make_relation(
                word=target,
                target=word,
                relation_type="spelling_confusable",
                words_by_norm=words_by_norm,
                wordbook_by_norm=wordbook_by_norm,
                explanation_zh=spec["explanationZh"],
                example_en=spec["exampleEn"],
                example_zh=spec["exampleZh"],
                source="manual_spelling_confusable",
                strength=5,
            )
            suggestions[reverse["_id"]] = reverse

    rows = sorted(suggestions.values(), key=lambda item: (item["word"], item["relationType"], item["targetWord"]))
    write_jsonl(OUT_PATH, rows)
    report = {
        "suggestions": len(rows),
        "byRelationType": {},
        "ecdictResembleCandidatesAdded": resemble_added,
        "targetMissingGlobalWords": sum(not row["targetInGlobalWords"] for row in rows),
        "targetOutsideWordbook": sum(not row["targetInWordbook"] for row in rows),
        "output": str(OUT_PATH),
    }
    for row in rows:
        report["byRelationType"][row["relationType"]] = report["byRelationType"].get(row["relationType"], 0) + 1
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
