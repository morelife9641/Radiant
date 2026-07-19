#!/usr/bin/env python3
"""Fix bad Argos translations for shortDefinitionZh."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
REPORT_PATH = DATA_DIR / "short_definition_zh_argos_bad_case_fix_report.json"


WORD_FIXES: dict[str, str] = {
    "comparatively": "与其他事物相比，达到相当高的程度。",
    "amount": "某事物的数量。",
    "solution": "问题的答案，或液体混合物。",
    "ensure": "确保某事一定发生或为真。",
    "improve": "使某事物变得更好。",
    "cite": "提到或引用某事物作为证据或例子。",
    "feed": "给人或动物提供食物。",
    "reveal": "使某事为人所知，或显示隐藏的事物。",
    "judgment": "意见、决定，或作出明智决定的能力。",
    "concentrate": "把全部注意力集中在某事上。",
    "collect": "把来自不同地方的事物聚集到一起。",
    "argue": "进行有不同意见的争论或讨论。",
    "collection": "把来自不同地方的事物聚集到一起。",
    "abolish": "废除或取消某事物。",
    "fair": "平等地对待人。",
    "deliver": "说出话语，或把某物送到某处。",
    "conversation": "通过说话非正式地交换观点、想法或信息。",
    "occupy": "居住在某处，或占据空间、时间或注意力。",
    "obtain": "获得或取得某事物。",
    "stance": "对某个问题的立场、态度或观点。",
    "poll": "通过采访随机样本来调查公众意见。",
    "addict": "使人对某事物产生依赖。",
    "harmony": "观点和行动上的一致或协调。",
    "contribute": "有助于某事发生或改善。",
    "debate": "有不同意见的争论或讨论。",
    "briefly": "持续很短时间；或简短地说。",
    "wildlife": "未经驯养、生活在自然环境中的所有动物和植物。",
    "fancy": "一种较随意、较表层的想象。",
    "lever": "绕支点转动的坚硬杆状工具。",
    "sympathy": "支持、忠于或同意某种观点的倾向。",
    "enlist": "参军，或争取某人帮助。",
    "evaluate": "形成判断或评估某事物的价值。",
    "embryo": "发育早期的动植物，或事物的萌芽阶段。",
}


def read_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )


def main() -> None:
    rows = read_records(LEARNING_PATH)
    now = datetime.now(timezone.utc).isoformat()
    report: list[dict[str, Any]] = []
    for row in rows:
        word = str(row.get("word") or "")
        if word not in WORD_FIXES:
            continue
        old_zh = row.get("shortDefinitionZh")
        row["shortDefinitionZh"] = WORD_FIXES[word]
        review = row.setdefault("shortDefinitionReview", {})
        if isinstance(review, dict):
            review["shortDefinitionZhSource"] = "manual_argos_bad_case_fix"
            review["shortDefinitionZhFixedAt"] = now
            review["oldShortDefinitionZhBeforeBadCaseFix"] = old_zh
        provenance = row.setdefault("provenance", {})
        if isinstance(provenance, dict):
            provenance["shortDefinitionZhSource"] = "manual_argos_bad_case_fix"
            provenance["shortDefinitionZhFixedAt"] = now
        report.append(
            {
                "word": word,
                "wordId": row.get("wordId"),
                "shortDefinitionEn": row.get("shortDefinitionEn"),
                "oldShortDefinitionZh": old_zh,
                "newShortDefinitionZh": row["shortDefinitionZh"],
            }
        )
    write_jsonl(LEARNING_PATH, rows)
    REPORT_PATH.write_text(json.dumps({"updated": len(report), "items": report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updated": len(report), "report": str(REPORT_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
