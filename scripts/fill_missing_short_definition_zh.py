#!/usr/bin/env python3
"""Fill missing Chinese short definitions for IELTS learning content."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
WORDBOOK_WORDS_PATH = DATA_DIR / "wordbook_words.json"
REPORT_PATH = DATA_DIR / "missing_short_definition_zh_fill_report.json"


MANUAL_ZH: dict[str, str] = {
    "transform": "彻底改变；转变",
    "subject": "主题；研究对象；科目",
    "route": "路线；路径",
    "presumably": "大概；推测起来",
    "memorise": "记住；熟记",
    "landmark": "地标；重要事件",
    "tap": "轻拍；利用资源",
    "proceed": "继续进行；前进",
    "thereby": "因此；由此",
    "exhibit": "展品；展示；表现",
    "involve": "涉及；包含；使参与",
    "feedback": "反馈；反应",
    "remark": "评论；话语",
    "ecology": "生态学；生态关系",
    "journal": "期刊；日志",
    "course": "课程；过程；路线",
    "definition": "定义；释义",
    "merely": "仅仅；只是",
    "acquire": "获得；习得",
    "guidance": "指导；建议",
    "hamper": "阻碍；妨碍",
    "valid": "有效的；有根据的",
    "advocate": "提倡；支持",
    "carry": "携带；承载",
    "oppose": "反对；抵制",
    "however": "然而；不过",
    "mere": "仅仅的；只不过",
    "alarm": "警报；惊慌",
    "benefit": "好处；使受益",
    "enable": "使能够；使可能",
    "incur": "招致；遭受",
    "transfer": "转移；调动",
    "except": "除……之外",
    "general": "一般的；总体的",
    "scent": "气味；香味",
    "sample": "样本；取样",
    "damage": "损害；破坏",
    "mixture": "混合物",
    "create": "创造；产生",
    "ornamental": "装饰性的",
    "aesthetic": "审美的；美学的",
    "gland": "腺体",
    "synthetic": "合成的；人造的",
    "principle": "原则；原理",
    "replace": "替代；更换",
    "acid": "酸；酸性物质",
    "item": "项目；物品",
    "foam": "泡沫",
    "pump": "泵；抽送",
    "glossy": "有光泽的",
    "apart": "分开；相隔",
    "prohibit": "禁止；阻止",
    "despite": "尽管；虽然",
    "undoubtedly": "无疑地",
    "for instance": "例如",
    "grasp": "抓住；理解",
    "occasion": "场合；时机；原因",
    "response": "回应；反应",
    "understanding": "理解；谅解",
    "behave": "表现；行为",
    "at random": "随机地；任意地",
    "requirement": "要求；必要条件",
    "correspond": "符合；通信",
    "albeit": "虽然；尽管",
    "outlaw": "宣布非法；不法之徒",
    "recreate": "再创造；重现",
    "triumphant": "胜利的；得意的",
    "dusk": "黄昏；傍晚",
    "aptitude": "天资；能力倾向",
    "front-line": "一线的；前线的",
    "superb": "极好的；出色的",
    "conceive": "构想；想象",
    "dubious": "可疑的；不确定的",
    "virtuous": "有德行的；高尚的",
    "acclaim": "赞誉；称赞",
    "unrealistic": "不现实的",
}


EN_FIXES: dict[str, str] = {
    "differ": "To be different from something or someone.",
}


def read_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )


def clean_zh(text: str) -> str:
    text = re.sub(r"\[[^\]]+\]", "", text or "")
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"（[^）]*）", "", text)
    text = re.sub(r"\b(?:n|v|vt|vi|adj|adv|prep|conj|pron|a|ad)\.\s*", "", text, flags=re.I)
    text = text.replace("\\n", "；")
    text = text.replace("...", "……")
    parts = [p.strip(" .;；,，、") for p in re.split(r"[；;\n]+", text) if p.strip(" .;；,，、")]
    if not parts:
        return ""
    first = parts[0]
    subparts = [p.strip(" .;；,，、") for p in re.split(r"[，,/、]", first) if p.strip(" .;；,，、")]
    if len(subparts) >= 2:
        candidate = "；".join(subparts[:2])
        if len(candidate) <= 20:
            return candidate
    return first[:40]


def main() -> None:
    word_docs = {record.get("_id"): record for record in read_records(WORDS_PATH)}
    wordbook_by_id = {record.get("wordId"): record for record in read_records(WORDBOOK_WORDS_PATH)}
    records = read_records(LEARNING_PATH)
    now = datetime.now().astimezone(timezone.utc).isoformat()
    report: list[dict[str, Any]] = []

    for record in records:
        if record.get("shortDefinitionZh"):
            continue
        word = str(record.get("word") or "").strip()
        word_id = record.get("wordId")
        word_doc = word_docs.get(word_id, {})
        senses = word_doc.get("senses") or []
        first_sense = senses[0] if senses else {}
        zh = MANUAL_ZH.get(word) or clean_zh(str(first_sense.get("translation") or first_sense.get("definitionZh") or ""))
        if not zh:
            zh = "待人工补中文短释"

        old_en = record.get("shortDefinitionEn")
        if word in EN_FIXES:
            record["shortDefinitionEn"] = EN_FIXES[word]
            provenance = record.setdefault("provenance", {})
            if isinstance(provenance, dict):
                provenance["shortDefinitionEnglishFix"] = "fixed_while_filling_zh"

        record["shortDefinitionZh"] = zh
        review = record.setdefault("shortDefinitionReview", {})
        if isinstance(review, dict):
            review["zhFilledAt"] = now
            review["zhFillSource"] = "manual_map" if word in MANUAL_ZH else "word_sense_translation"
        provenance = record.setdefault("provenance", {})
        if isinstance(provenance, dict):
            provenance["shortDefinitionZhSource"] = "manual_map" if word in MANUAL_ZH else "word_sense_translation"
            provenance["shortDefinitionZhFilledAt"] = now

        wb = wordbook_by_id.get(word_id, {})
        report.append(
            {
                "order": wb.get("order"),
                "word": word,
                "wordId": word_id,
                "shortDefinitionEn": record.get("shortDefinitionEn"),
                "oldShortDefinitionEn": old_en,
                "shortDefinitionZh": zh,
                "status": record.get("shortDefinitionStatus"),
                "source": provenance.get("shortDefinitionZhSource") if isinstance(provenance, dict) else "",
            }
        )

    write_jsonl(LEARNING_PATH, records)
    report.sort(key=lambda row: row.get("order") or 0)
    REPORT_PATH.write_text(json.dumps({"updated": len(report), "items": report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updated": len(report), "report": str(REPORT_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
