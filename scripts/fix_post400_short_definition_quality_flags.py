#!/usr/bin/env python3
"""Fix quality flags after the post-400 short-definition pass."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDBOOK_WORDS_PATH = DATA_DIR / "wordbook_words.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "post400_short_definition_quality_fix_report.json"


FIXES: dict[str, tuple[str, str]] = {
    "inadequate": ("Not enough or not good enough for a particular purpose.", "不充分的；不够好的"),
    "retail": ("The sale of goods directly to customers, or to sell goods this way.", "零售；零售销售"),
    "prior": ("Existing, happening, or coming before something else.", "先前的；优先的"),
    "disorder": ("A state of confusion, lack of order, or illness.", "混乱；失调；疾病"),
    "orthodox": ("Following accepted, traditional, or established beliefs and methods.", "正统的；传统的"),
    "generic": ("General rather than specific, or shared by a whole group.", "一般的；通用的"),
    "sponge": ("A soft material or sea creature that can take in water easily.", "海绵；海绵状物"),
    "resort": ("A place people visit for holidays, or the act of turning to something for help.", "度假地；求助"),
    "height": ("The distance from the bottom to the top, or the level above the ground or sea.", "高度；海拔"),
    "statistics": ("Numbers collected and studied to understand facts or trends.", "统计数据；统计学"),
    "respond": ("To answer or react to something.", "回答；回应；反应"),
    "mammal": ("An animal that feeds its young with milk from the mother's body.", "哺乳动物"),
    "hospitable": ("Friendly to guests, or suitable for living and growth.", "好客的；适宜的"),
    "compile": ("To collect information from different places and put it together.", "汇编；编制；收集"),
    "calcium": ("A chemical element important for bones, teeth, and many living processes.", "钙"),
    "opportunity": ("A chance to do something or make progress.", "机会；时机"),
    "compete": ("To try to win or be more successful than others.", "竞争；比赛"),
    "detail": ("A small part or fact, or to describe something fully.", "细节；详述"),
    "cardiovascular": ("Related to the heart and blood vessels.", "心血管的"),
    "steady": ("Firm, controlled, and not changing suddenly.", "稳定的；平稳的"),
    "burst": ("To break open suddenly, or a sudden strong expression of something.", "爆裂；突然爆发"),
    "Mediterranean": ("Related to the sea and region between southern Europe, North Africa, and western Asia.", "地中海的；地中海地区"),
    "disadvantage": ("A problem or condition that makes success more difficult.", "缺点；不利条件"),
    "reptile": ("A cold-blooded animal such as a snake, lizard, turtle, or crocodile.", "爬行动物"),
    "skull": ("The bone structure of the head that protects the brain.", "颅骨；头骨"),
    "chase": ("To run after someone or something in order to catch it.", "追赶；追捕"),
    "humanistic": ("Related to human values, culture, and individual dignity.", "人文主义的；重视人的"),
    "exact": ("Completely correct, accurate, or precise.", "准确的；精确的"),
    "laser": ("A device that produces a very narrow and powerful beam of light.", "激光"),
    "flint": ("A hard grey stone that can produce sparks when struck.", "火石；燧石"),
    "renaissance": ("A period of renewed interest, growth, or cultural achievement.", "复兴；文艺复兴"),
    "probability": ("How likely something is to happen.", "可能性；概率"),
    "notoriety": ("The state of being famous for something bad.", "恶名；声名狼藉"),
    "hypothetical": ("Based on an imagined situation rather than a real one.", "假设的；假定的"),
    "nerve": ("A fibre in the body that carries signals between the brain and other parts.", "神经"),
    "symphony": ("A long piece of music written for an orchestra.", "交响乐；交响曲"),
    "gender": ("The social or biological category of being male, female, or another identity.", "性别"),
    "chart": ("A visual display of information, often using lines, bars, or symbols.", "图表；图"),
}


def read_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )


def main() -> None:
    wordbook_by_id = {record.get("wordId"): record for record in read_records(WORDBOOK_WORDS_PATH)}
    records = read_records(LEARNING_PATH)
    now = datetime.now(timezone.utc).isoformat()
    report: list[dict[str, Any]] = []

    for record in records:
        word = str(record.get("word") or "").strip()
        if word not in FIXES:
            continue
        wb = wordbook_by_id.get(record.get("wordId"), {})
        old_en = record.get("shortDefinitionEn")
        old_zh = record.get("shortDefinitionZh")
        new_en, new_zh = FIXES[word]
        record["shortDefinitionEn"] = new_en
        record["shortDefinitionZh"] = new_zh
        record["shortDefinitionStatus"] = "curated_manual_short_definition"
        record["shortDefinitionReview"] = {
            "status": "quality_fixed_after_post400_pass",
            "labelZh": "已修复短释质量问题",
            "reviewedAt": now,
            "reviewSource": "codex_quality_scan_revision",
            "originalShortDefinitionEn": old_en,
            "originalShortDefinitionZh": old_zh,
        }
        provenance = record.setdefault("provenance", {})
        if isinstance(provenance, dict):
            provenance["shortDefinitionSource"] = "codex_quality_scan_revision"
            provenance["reviewStatus"] = "short_definition_quality_fixed"
            provenance["reviewedAt"] = now
        report.append(
            {
                "order": wb.get("order"),
                "word": word,
                "oldShortDefinitionEn": old_en,
                "newShortDefinitionEn": new_en,
                "oldShortDefinitionZh": old_zh,
                "newShortDefinitionZh": new_zh,
            }
        )

    write_jsonl(LEARNING_PATH, records)
    report.sort(key=lambda row: row.get("order") or 0)
    REPORT_PATH.write_text(json.dumps({"updated": len(report), "items": report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updated": len(report), "report": str(REPORT_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
