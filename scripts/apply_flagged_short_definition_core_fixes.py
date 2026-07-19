#!/usr/bin/env python3
"""Rewrite flagged short definitions with simple core meanings."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDBOOK_WORDS_PATH = DATA_DIR / "wordbook_words.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "flagged_short_definition_core_fix_report.json"


CORE_DEFINITIONS: dict[str, str] = {
    "aware": "Knowing about a fact, situation, or problem.",
    "remove": "To take something away from a place or position.",
    "economic": "Related to money, trade, industry, or the economy.",
    "snap": "To break suddenly, or to make a short sharp sound.",
    "pest": "An insect, animal, or person that causes trouble or damage.",
    "otherwise": "In a different way, or if not.",
    "chill": "A cold feeling, or to make something colder.",
    "inactive": "Not active, working, or being used.",
    "variety": "A range of different types or examples of something.",
    "apply": "To request something formally, or to use a rule, idea, or method.",
    "avoid": "To stay away from someone or something, or prevent something from happening.",
    "assess": "To judge the value, quality, size, or importance of something.",
    "observation": "The act of watching, noticing, or studying something carefully.",
    "commit": "To promise to do something, or to do something wrong or illegal.",
    "endorse": "To publicly support, approve of, or recommend something.",
    "request": "To ask for something politely or officially.",
    "explore": "To examine or discuss something in order to learn more about it.",
    "implication": "A possible effect, meaning, or result of an action or idea.",
    "technique": "A particular method or skill used to do something.",
    "emotional": "Related to feelings rather than facts or practical reasons.",
    "encounter": "To meet or experience someone or something, often unexpectedly.",
    "discipline": "A field of study, or training that controls behavior.",
    "physical": "Related to the body, real objects, or the material world.",
    "relation": "A connection between people, things, ideas, or events.",
    "effective": "Successful in producing the wanted result.",
    "advanced": "Highly developed, modern, or at a high level.",
    "negotiate": "To discuss something in order to reach an agreement.",
    "refusal": "The act of saying no or not accepting something.",
    "opposite": "Completely different, or on the other side.",
    "scholar": "A person who studies or knows a lot about a subject.",
    "drill": "A tool for making holes, or repeated practice of a skill.",
    "occur": "To happen or exist in a particular place or situation.",
    "strategy": "A plan for achieving a goal.",
    "basis": "The main reason, idea, or support on which something depends.",
    "address": "To deal with a problem or speak to a person or group.",
    "organize": "To arrange people, things, or activities in a planned way.",
    "arrange": "To plan or put things in a particular order.",
    "eliminate": "To remove or get rid of something completely.",
    "reinforcement": "Extra support, strength, or evidence that makes something stronger.",
    "attract": "To make someone or something come closer or become interested.",
    "notion": "An idea, belief, or understanding of something.",
    "proof": "Information or evidence showing that something is true.",
    "exist": "To be real or present.",
    "pollinate": "To move pollen to a flower so that a plant can produce seeds.",
    "biological": "Related to living things or the science of life.",
    "organic": "Related to living things, natural processes, or food grown without artificial chemicals.",
    "smell": "To notice an odour with the nose, or the odour itself.",
    "release": "To let someone or something go, or make information or a product available.",
    "consist": "To be made up of particular parts or things.",
    "contain": "To have something inside or as part of itself.",
    "oxygen": "A gas in the air that living things need to breathe.",
    "mechanism": "A system, process, or set of parts that makes something work.",
    "ancient": "Very old, especially from a time long ago in history.",
    "trap": "A device or situation that catches or prevents escape.",
    "signal": "A sign, sound, or action that gives information or instructions.",
    "female": "Belonging to the sex that can produce eggs or give birth.",
    "profile": "A short description of a person, thing, or set of features.",
    "mite": "A very small creature similar to a spider, often living on plants or animals.",
    "signature": "A person's written name, or a special feature that identifies something.",
    "offend": "To make someone upset, angry, or hurt by what you say or do.",
    "hatch": "To come out of an egg, or to make young animals come out of eggs.",
    "scheme": "A plan or system for doing or organizing something.",
    "attack": "To use violence against someone or something, or strongly criticize it.",
    "perform": "To do a task, action, or piece of work.",
    "valuable": "Useful, important, or worth a lot of money.",
    "fragrance": "A pleasant smell.",
    "emission": "The release of gas, heat, light, or other substances.",
    "exacerbate": "To make a problem, illness, or bad situation worse.",
    "major": "Very important, large, or serious.",
    "breed": "To produce young animals or plants, or a type of animal or plant.",
    "solution": "An answer to a problem, or a liquid mixture.",
    "adequate": "Good enough or enough for a particular purpose.",
    "drawback": "A disadvantage or problem with something.",
    "genetic": "Related to genes or inherited characteristics.",
    "consequent": "Happening as a result of something else.",
    "attempt": "An effort to do or achieve something.",
    "spray": "Liquid sent out in many small drops, or to send liquid out this way.",
    "toxic": "Poisonous or harmful.",
    "appropriate": "Suitable or right for a particular situation.",
    "manipulate": "To control or handle something skillfully, sometimes unfairly.",
    "sacrifice": "To give up something important in order to gain or help something else.",
    "express": "To show or communicate thoughts, feelings, or ideas.",
    "gene": "A unit of DNA that controls inherited characteristics.",
    "preliminary": "Coming before the main or final stage.",
    "amount": "A quantity of something.",
    "sophisticated": "Advanced, complex, or showing good judgment and taste.",
    "organ": "A part of the body, such as the heart or liver, with a special function.",
    "commodity": "A product or raw material that can be bought and sold.",
    "application": "A formal request, practical use, or computer program.",
    "competition": "A situation in which people or groups try to be more successful than others.",
    "dissolve": "To mix into a liquid and disappear, or to end an organization or agreement.",
    "manufacture": "To make goods in large quantities, usually in a factory.",
    "handle": "To deal with, control, or hold something.",
    "frame": "A strong border or structure that supports or surrounds something.",
    "resistant": "Not easily affected, damaged, or changed by something.",
    "switch": "To change from one thing to another, or a device used to turn something on or off.",
    "waterproof": "Not allowing water to pass through.",
    "relate": "To show or understand a connection between things.",
    "ideal": "Best or most suitable for a particular purpose.",
    "roller": "A tube or wheel that turns, often used to press, move, or spread something.",
    "element": "An important part of something, or a simple chemical substance.",
    "fibre": "A thin thread-like part of a material, plant, or food.",
    "stretch": "To make something longer or wider, or a continuous area or period.",
    "litter": "Waste left in a public place, or young animals born at the same time.",
    "recycle": "To use waste materials again to make new products.",
    "trend": "A general direction in which something is changing or developing.",
    "stem": "The main stalk of a plant, or to stop something from spreading.",
    "conditioner": "A substance used to improve the condition of hair, skin, or a material.",
}


def read_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )


def is_flagged(record: dict[str, Any]) -> bool:
    review = record.get("shortDefinitionReview") or {}
    return record.get("shortDefinitionStatus") == "human_flagged_for_revision" or review.get("status") == "rejected"


def main() -> None:
    wordbook_words = read_records(WORDBOOK_WORDS_PATH)
    wordbook_by_id = {record.get("wordId"): record for record in wordbook_words}
    learning_records = read_records(LEARNING_PATH)
    now = datetime.now(timezone.utc).isoformat()
    report: list[dict[str, Any]] = []

    for record in learning_records:
        word = str(record.get("word") or "").strip()
        if not word or not is_flagged(record):
            continue
        new_definition = CORE_DEFINITIONS.get(word)
        wordbook_record = wordbook_by_id.get(record.get("wordId"), {})
        if not new_definition:
            report.append(
                {
                    "order": wordbook_record.get("order"),
                    "word": word,
                    "wordId": record.get("wordId"),
                    "status": "missing_core_definition",
                    "oldShortDefinitionEn": record.get("shortDefinitionEn"),
                }
            )
            continue

        old_definition = record.get("shortDefinitionEn")
        record["shortDefinitionEn"] = new_definition
        record["shortDefinitionStatus"] = "curated_manual_short_definition"
        record["shortDefinitionReview"] = {
            "status": "revised_after_human_feedback",
            "labelZh": "已按人工反馈改为核心释义",
            "reviewedAt": now,
            "reviewSource": "codex_core_meaning_revision",
            "originalShortDefinitionEn": old_definition,
        }
        provenance = record.setdefault("provenance", {})
        if isinstance(provenance, dict):
            provenance["shortDefinitionSource"] = "human_feedback_core_revision"
            provenance["reviewStatus"] = "short_definition_revised_after_human_feedback"
            provenance["reviewedAt"] = now

        report.append(
            {
                "order": wordbook_record.get("order"),
                "word": word,
                "wordId": record.get("wordId"),
                "oldShortDefinitionEn": old_definition,
                "newShortDefinitionEn": new_definition,
                "status": "updated",
            }
        )

    write_jsonl(LEARNING_PATH, learning_records)
    report.sort(key=lambda row: (row.get("order") is None, row.get("order") or 0, row.get("word") or ""))
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "updated": sum(1 for row in report if row.get("status") == "updated"),
                "missing": sum(1 for row in report if row.get("status") != "updated"),
                "report": str(REPORT_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
