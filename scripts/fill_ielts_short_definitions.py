#!/usr/bin/env python3
"""Fill concise English definitions for IELTS word learning content."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
REPORT_PATH = DATA_DIR / "short_definitions_fill_report.json"


CURATED: dict[str, str] = {
    "transform": "To change something greatly in form, nature, or appearance.",
    "subject": "A topic, area of study, or person being discussed or tested.",
    "route": "A way or path from one place to another.",
    "presumably": "Used to say that something is probably true based on what is known.",
    "memorise": "To learn something so that you can remember it exactly.",
    "landmark": "An important building, place, event, or discovery that is easy to recognize.",
    "tap": "To touch lightly, or to make use of a source or resource.",
    "proceed": "To continue doing something or move forward.",
    "thereby": "By that action or as a result of it.",
    "involve": "To include, require, or make someone take part in something.",
    "feedback": "Information or reaction given about how well something works or is done.",
    "remark": "Something said or written as a comment.",
    "ecology": "The study of how living things relate to each other and their environment.",
    "journal": "A written record, diary, or academic publication.",
    "course": "A class, direction, or series of events over time.",
    "definition": "A statement that explains the meaning of a word or idea.",
    "merely": "Only, simply, or no more than.",
    "acquire": "To get, learn, or develop something over time.",
    "guidance": "Help, advice, or direction about what to do.",
    "hamper": "To make progress or action difficult.",
    "carry": "To hold, move, or support something from one place to another.",
    "mere": "Used to emphasize that something is only or simply what is stated.",
    "alarm": "A warning signal or a feeling of fear caused by possible danger.",
    "incur": "To experience something unpleasant as a result of your actions.",
    "benefit": "An advantage, help, or useful effect.",
    "transfer": "To move someone or something from one place, job, or situation to another.",
    "except": "Not including someone or something.",
    "facilitate": "To make an action or process easier.",
    "stage": "A period or step in a process or development.",
    "stick": "To attach to something, or to push a pointed object into something.",
    "profit": "Money gained from business, or an advantage gained from something.",
    "willing": "Ready or happy to do something if needed.",
    "flexible": "Able to change or adapt easily.",
    "firm": "Strong, steady, and unlikely to change.",
    "bargain": "Something bought cheaply, or an agreement after negotiation.",
    "union": "An organization of workers, or the act of joining things together.",
    "proportion": "A part, share, or amount compared with the whole.",
    "retire": "To stop working, usually because of age.",
    "management": "The act of controlling or organizing people, work, or resources.",
    "virtue": "A good moral quality or an advantage of something.",
    "exaggerate": "To describe something as larger, better, or worse than it really is.",
    "judgment": "An opinion, decision, or ability to make sensible decisions.",
    "besides": "In addition to something, or apart from it.",
    "graduate": "To complete a course of study, especially at a university.",
    "tend": "To be likely to do something or happen in a particular way.",
    "attractive": "Pleasant, interesting, or likely to draw attention.",
    "service": "Work done to help others, or maintenance done on equipment.",
    "employ": "To hire someone or use something for a purpose.",
    "innovation": "A new idea, method, or product.",
    "describe": "To say what someone or something is like.",
    "barrier": "Something that blocks movement, progress, or communication.",
    "devise": "To invent or plan a method or system.",
    "staff": "The people who work for an organization.",
    "concentrate": "To give all your attention to something.",
    "separate": "Not joined or connected; different or independent.",
    "contract": "A legal agreement between people or organizations.",
    "hang": "To attach or place something so that it is supported from above.",
    "ambiguous": "Having more than one possible meaning and therefore unclear.",
    "productive": "Able to produce useful results or a large amount of something.",
    "assumption": "Something accepted as true without definite proof.",
    "spite": "A desire to hurt or annoy someone.",
    "extra": "More than usual, expected, or necessary.",
    "persuade": "To make someone believe something or agree to do something.",
    "insurance": "An arrangement that pays money if loss, damage, or illness occurs.",
    "announce": "To tell people something publicly or officially.",
    "anthropologist": "A person who studies human societies, cultures, and development.",
    "advertise": "To tell people about a product, service, or event to attract interest.",
    "agency": "An organization that provides a particular service or represents others.",
    "link": "A connection between people, things, ideas, or events.",
    "percentage": "An amount expressed as a part of one hundred.",
    "wage": "A regular amount of money paid for work.",
    "corporate": "Related to a company or business organization.",
    "intellectual": "Related to thinking, learning, and ideas.",
    "temporary": "Existing or lasting for only a limited time.",
    "transition": "A change from one state, stage, or situation to another.",
    "prohibit": "To officially forbid something or prevent it from happening.",
    "despite": "Used to show that something happens although another thing might have prevented it.",
    "undoubtedly": "Used to say that something is certainly true.",
    "for instance": "Used to introduce an example.",
    "grasp": "To hold something firmly, or to understand something clearly.",
    "occasion": "A particular time, event, opportunity, or reason for something.",
    "response": "Something said, done, or felt as a reaction to something.",
    "understanding": "Knowledge about something, or sympathy for how someone feels.",
    "behave": "To act in a particular way.",
    "mosquito": "A small flying insect that bites people or animals and drinks blood.",
    "latitude": "The distance north or south of the equator, measured in degrees.",
    "equal": "The same in amount, size, value, or status.",
    "superior": "Better, higher in quality, or higher in rank.",
    "stress": "Pressure, worry, or special emphasis placed on something.",
    "include": "To have something as one part of a larger whole.",
    "equator": "An imaginary line around the middle of the Earth.",
    "affect": "To influence someone or something.",
    "general": "Usual, common, or relating to the whole rather than details.",
    "scent": "A smell, especially a pleasant or distinctive one.",
    "sample": "A small part or amount used to show what the whole is like.",
    "damage": "Harm that makes something less useful, healthy, or valuable.",
    "mixture": "A combination of two or more different things.",
    "create": "To make something new exist.",
    "ornamental": "Used or grown for decoration rather than practical use.",
    "aesthetic": "Related to beauty or the appreciation of beauty.",
    "gland": "An organ that produces substances the body needs.",
    "synthetic": "Made by chemical or artificial processes rather than naturally.",
    "principle": "A basic rule, belief, or truth that guides action or reasoning.",
    "replace": "To take the place of someone or something.",
    "acid": "A chemical substance that can react with metals and has a sour taste.",
    "item": "A single thing in a list, group, or collection.",
    "foam": "A mass of small bubbles on or in a liquid.",
    "pump": "A machine that moves liquid or gas from one place to another.",
    "glossy": "Smooth and shiny.",
    "apart": "Separated by distance, time, or difference.",
    "valid": "Based on truth, logic, or accepted rules.",
    "advocate": "To publicly support an idea, policy, or person.",
    "oppose": "To disagree with or act against something.",
    "however": "Used to introduce a contrast or opposite point.",
    "attention": "Careful thought, notice, or mental focus.",
    "enable": "To make it possible for someone to do something.",
    "various": "Different from one another; of several kinds.",
    "locate": "To find the position or place of something.",
    "observe": "To watch or notice something carefully.",
    "theory": "An idea or explanation based on evidence and reasoning.",
    "in addition": "Used to add another point or piece of information.",
    "at least": "Used to show the smallest amount, number, or degree.",
    "saline": "Containing salt or related to salt water.",
    "fragile": "Easily broken, damaged, or weakened.",
    "solar-powered": "Using energy from the sun to work.",
    "stance": "A position, attitude, or opinion about an issue.",
    "capacity": "The ability to do something, or the amount something can hold.",
    "bind": "To tie, hold, or connect things together.",
    "constrain": "To limit or restrict someone or something.",
    "astonish": "To surprise someone very greatly.",
    "at random": "Without a fixed plan, pattern, or order.",
    "requirement": "Something that is needed or officially demanded.",
    "correspond": "To match, be similar, or communicate by writing.",
    "albeit": "Although; used to introduce a contrasting detail.",
    "outlaw": "To make something illegal, or a person who has broken the law.",
    "recreate": "To make something exist or happen again.",
    "triumphant": "Very successful or showing joy after success.",
    "dusk": "The time in the evening when daylight is fading.",
    "aptitude": "A natural ability to learn or do something well.",
    "front-line": "Directly involved in the most important or difficult work.",
    "superb": "Extremely good or impressive.",
    "conceive": "To imagine, think of, or form an idea.",
    "dubious": "Doubtful, uncertain, or not completely trustworthy.",
    "virtuous": "Having good moral qualities.",
    "acclaim": "Public praise and approval.",
    "unrealistic": "Not sensible or practical because it ignores real conditions.",
    "calorie": "A unit used to measure energy in food.",
    "fossil": "The preserved remains or mark of an ancient plant or animal.",
    "commission": "A group officially given a task, or money paid for making a sale.",
    "bureaucracy": "A system of government or management with many rules and officials.",
    "administrator": "A person who manages or organizes an institution, system, or office.",
    "maintenance": "The work of keeping something in good condition.",
    "realm": "A field, area, or sphere of activity or knowledge.",
    "in accordance with": "In agreement with a rule, request, or standard.",
    "refresh": "To make someone or something feel new, active, or energetic again.",
    "consumption": "The act or amount of using, eating, drinking, or buying something.",
    "association": "A connection between people, ideas, events, or things.",
}


ZH_KEYWORDS: list[tuple[str, str]] = [
    ("改变", "To change something or make it different."),
    ("转换", "To change from one form, state, or use to another."),
    ("影响", "To influence someone or something."),
    ("包括", "To have something as one part of a larger whole."),
    ("涉及", "To include or be connected with something."),
    ("导致", "To cause something to happen."),
    ("减少", "To make something smaller in amount, number, or degree."),
    ("增加", "To become or make something greater in amount, number, or degree."),
    ("发展", "To grow, improve, or become more advanced."),
    ("研究", "To study something carefully in order to learn more about it."),
    ("分析", "To examine something carefully to understand it."),
    ("解释", "To make something clear or easy to understand."),
    ("证明", "To show that something is true or exists."),
    ("认为", "To have or express a particular opinion."),
    ("提供", "To give or make something available."),
    ("产生", "To produce or cause something."),
    ("保护", "To keep someone or something safe from harm."),
    ("适应", "To change in order to suit a new situation."),
    ("支持", "To help, approve of, or provide what is needed."),
    ("反对", "To disagree with or resist something."),
    ("限制", "To control or keep something within limits."),
    ("比较", "To examine similarities and differences."),
    ("测量", "To find the size, amount, or degree of something."),
    ("观察", "To watch or notice something carefully."),
    ("发现", "To find or learn something for the first time."),
    ("出现", "To happen, begin to exist, or become visible."),
    ("消失", "To stop existing or being seen."),
    ("保持", "To continue to have or do something."),
    ("避免", "To prevent something from happening or stay away from it."),
    ("选择", "To decide which thing or person you want."),
    ("评估", "To judge the value, quality, or importance of something."),
    ("预测", "To say what is likely to happen in the future."),
    ("过程", "A series of actions or changes that happen over time."),
    ("方法", "A way of doing something."),
    ("原因", "The reason why something happens."),
    ("结果", "Something that happens because of another thing."),
    ("证据", "Information that helps show whether something is true."),
    ("协议", "An agreement between people, groups, or organizations."),
    ("合同", "A legal agreement between people or organizations."),
    ("利润", "Money gained from business after costs are paid."),
    ("益处", "A useful or helpful effect."),
    ("美德", "A good moral quality."),
    ("意见", "An opinion or judgment about something."),
    ("障碍", "Something that blocks progress, movement, or communication."),
    ("栅栏", "A structure that blocks or separates an area."),
    ("服务", "Work or help provided for other people."),
    ("维修", "The act of keeping equipment in good condition or fixing it."),
    ("雇用", "To hire someone to do paid work."),
    ("使用", "To use something for a purpose."),
    ("革新", "A new idea, method, or product."),
    ("描述", "To say what someone or something is like."),
    ("设计", "To plan or create something for a particular purpose."),
    ("配备", "To provide people or things needed for a task."),
    ("全神贯注", "To give all your attention to something."),
    ("分离", "To move apart or keep things apart."),
    ("毕业", "To complete a course of study."),
    ("愿意", "Ready or happy to do something if needed."),
    ("易弯曲", "Able to bend or change easily."),
    ("灵活", "Able to change or adapt easily."),
    ("坚实", "Strong, steady, and not easily moved."),
    ("讨价还价", "To discuss prices or terms in order to reach an agreement."),
    ("协会", "An organization of people with a shared purpose."),
    ("比例", "A part or amount compared with the whole."),
    ("退休", "To stop working, usually because of age."),
    ("夸大", "To make something seem larger, better, or worse than it really is."),
    ("除", "Not including someone or something."),
    ("倾向于", "To be likely to do something or develop in a particular way."),
    ("吸引", "To make people interested in or drawn to something."),
    ("仅仅", "Only, simply, or no more than."),
    ("纯粹", "Only or completely of the stated kind."),
    ("阶段", "A period or step in a process or development."),
    ("舞台", "A raised area where performers can be seen by an audience."),
    ("刺", "To push a pointed object into something."),
    ("黏", "To attach to something or stay fixed to it."),
    ("特征", "A typical quality or feature of someone or something."),
    ("能力", "The power or skill to do something."),
    ("数量", "The amount or number of something."),
    ("程度", "The level or amount of something."),
    ("关系", "A connection between people, things, or ideas."),
    ("环境", "The conditions or surroundings in which something exists."),
    ("资源", "Something useful that can be used when needed."),
    ("材料", "A substance or information used to make or do something."),
    ("系统", "A set of connected parts that work together."),
    ("理论", "An idea or explanation based on evidence and reasoning."),
    ("主题", "The main subject or idea of something."),
    ("趋势", "A general direction in which something is changing."),
    ("问题", "A subject or difficulty that needs attention or a solution."),
    ("行为", "The way a person, animal, or system acts."),
    ("社会", "People living together in an organized community."),
    ("文化", "The ideas, customs, and way of life of a group of people."),
    ("经济", "Related to money, trade, industry, or the economy."),
    ("自然", "Related to the physical world, not made by people."),
    ("主要", "Most important or central."),
    ("明显", "Easy to see, notice, or understand."),
    ("可能", "Likely to happen or be true."),
    ("有效", "Working well and producing the intended result."),
    ("重要", "Having great value, effect, or influence."),
]


POS_LABELS = {
    "n": "A person, thing, idea, or process related to",
    "v": "To do or cause something related to",
    "vt": "To do or cause something related to",
    "vi": "To act or happen in a way related to",
    "a": "Describing something that is related to",
    "adj": "Describing something that is related to",
    "adv": "In a way that is related to",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\\n", " ")).strip()


def normalize_pos(pos: str) -> str:
    value = str(pos or "").lower().strip().rstrip(".")
    if "/" in value:
        parts = [normalize_pos(part) for part in re.split(r"[/,]", value) if part.strip()]
        if "v" in parts:
            return "v"
        if parts:
            return parts[0]
    if value in {"adj", "s"}:
        return "a"
    if value in {"vt", "vi"}:
        return "v"
    return value


def split_translation(text: str) -> str:
    text = clean_text(text)
    text = re.sub(r"\[[^\]]+\]", "", text)
    text = re.sub(r"\b(?:n|v|vt|vi|a|adj|adv|prep|conj|pron)\.\s*", "", text, flags=re.I)
    text = re.sub(r"/[^/]+/", "", text)
    text = text.strip(" ;；,，")
    first = re.split(r"[;；,，]", text)[0].strip()
    return first or text


def definition_from_zh(translation: str, pos: str) -> str:
    for keyword, definition in ZH_KEYWORDS:
        if keyword in translation:
            return definition
    return ""


def definition_from_en(raw: str, pos: str) -> str:
    raw = str(raw or "").replace("\\n", "\n")
    candidates: list[tuple[str, str]] = []
    for part in re.split(r"[\n;]", raw):
        text = clean_text(part)
        match = re.match(r"^(n|v|vt|vi|a|adj|adv|prep|conj|pron|s|r)\.?\s+", text, flags=re.I)
        marker = normalize_pos(match.group(1)) if match else ""
        text = re.sub(r"^(?:n|v|vt|vi|a|adj|adv|prep|conj|pron|s|r)\.?\s+", "", text, flags=re.I)
        text = text.strip(" .;:")
        if not text:
            continue
        if text.lower().startswith(("see ", "same as ", "a radioactive")):
            continue
        if len(text.split()) >= 3:
            candidates.append((marker, text))
    if not candidates:
        return ""
    pos_norm = normalize_pos(pos)
    pos_matches = [text for marker, text in candidates if marker == pos_norm]
    pool = pos_matches or [text for _, text in candidates]
    best = pool[0]
    if pos_norm == "v":
        for item in pool:
            if item.lower().startswith(("to ", "make ", "cause ", "change ", "move ", "give ", "show ", "use ")):
                best = item
                break
    if pos_norm == "n":
        for item in pool:
            if item.lower().startswith(("a ", "an ", "the ", "someone ", "something ")):
                best = item
                break
    if len(best) > 145:
        best = best[:142].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    if best and best[-1] not in ".!?":
        best += "."
    return best[:1].upper() + best[1:] if best else ""


def is_bad_short_definition(word: str, definition: str, status: str) -> bool:
    text = clean_text(definition)
    lower = text.lower()
    word_lower = word.lower()
    if not text:
        return True
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        return True
    if status.startswith("curated_"):
        return False
    # Avoid circular explanations such as "give occasion to".
    if re.search(r"\b" + re.escape(word_lower) + r"(?:s|ed|ing)?\b", lower):
        return True
    # Avoid obscure dictionary senses that are poor as learner-facing short
    # explanations for IELTS core vocabulary.
    if any(term in lower for term in ("priest", "minister", "congregation", "versicle", "radioactive isotope")):
        return True
    # Short definitions should be short. If an auto definition needs a whole
    # clause chain, it is not doing its job.
    if len(text.split()) > 18 and status.startswith("auto_"):
        return True
    return False


def build_definition(row: dict[str, Any], word_doc: dict[str, Any] | None) -> tuple[str, str]:
    word = str(row.get("normalized") or row.get("word") or "").lower()
    if word in CURATED:
        return CURATED[word], "curated_manual_short_definition"

    senses = (word_doc or {}).get("senses") or []
    sense = senses[0] if senses else {}
    pos = str(sense.get("pos") or "")
    translation = clean_text(sense.get("translation") or sense.get("definitionZh"))
    definition = definition_from_en(str(sense.get("definitionEn") or ""), pos)
    if definition:
        return definition, "auto_from_english_definition_pending_review"
    if translation:
        definition = definition_from_zh(translation, pos)
        if definition:
            return definition, "auto_from_translation_keyword_pending_review"
    return "", ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--force-auto", action="store_true", help="Clear and refill existing auto-generated short definitions.")
    args = parser.parse_args()

    learning = read_jsonl(LEARNING_PATH)
    words = read_jsonl(WORDS_PATH)
    words_by_id = {row["_id"]: row for row in words}

    for row in learning:
        current = str(row.get("shortDefinitionEn") or "")
        current_status = str(row.get("shortDefinitionStatus") or "")
        word = str(row.get("normalized") or row.get("word") or "").lower()
        if current and is_bad_short_definition(word, current, current_status):
            row.pop("shortDefinitionEn", None)
            row.pop("shortDefinitionStatus", None)
        elif args.force_auto and current_status.startswith("auto_from_"):
            row.pop("shortDefinitionEn", None)
            row.pop("shortDefinitionStatus", None)
        elif args.force_auto and word in CURATED:
            row.pop("shortDefinitionEn", None)
            row.pop("shortDefinitionStatus", None)

    updated: list[dict[str, str]] = []
    manual_updated: list[dict[str, str]] = []
    skipped: list[str] = []

    for row in learning:
        word = str(row.get("normalized") or row.get("word") or "").lower()
        if word not in CURATED:
            continue
        if clean_text(row.get("shortDefinitionEn")) and row.get("shortDefinitionStatus") == "curated_manual_short_definition":
            continue
        row["shortDefinitionEn"] = CURATED[word]
        row["shortDefinitionStatus"] = "curated_manual_short_definition"
        manual_updated.append({"word": str(row.get("word") or ""), "shortDefinitionEn": CURATED[word], "status": "curated_manual_short_definition"})

    for row in learning:
        if len(updated) >= args.limit:
            break
        if clean_text(row.get("shortDefinitionEn")):
            continue
        definition, status = build_definition(row, words_by_id.get(str(row.get("wordId") or "")))
        if not definition:
            skipped.append(str(row.get("word") or row.get("normalized") or ""))
            continue
        row["shortDefinitionEn"] = definition
        row["shortDefinitionStatus"] = status
        updated.append({"word": str(row.get("word") or ""), "shortDefinitionEn": definition, "status": status})

    write_jsonl(LEARNING_PATH, learning)
    report = {
        "requestedLimit": args.limit,
        "manualUpdatedCount": len(manual_updated),
        "updatedCount": len(updated),
        "skippedCountBeforeLimit": len(skipped),
        "manualUpdated": manual_updated,
        "updated": updated,
        "skippedBeforeLimit": skipped[:100],
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "updated"}, ensure_ascii=False, indent=2))
    print("firstUpdated:")
    print(json.dumps(updated[:20], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
