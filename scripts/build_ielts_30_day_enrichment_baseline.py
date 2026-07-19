"""Build the offline enrichment baseline for the IELTS 30-day wordbook.

This script does not invent dictionary examples. It structures reliable ECDICT
inflections, extracts existing reviewed relations, and creates an editorial
queue for content that still needs to be written or sourced.
"""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = ROOT / "tmp/cloud_import_ielts_30_day"
IMPORT_READY = ROOT / "tmp/import_ready"
OUT_DIR = ROOT / "tmp/ielts_30_day_enrichment"

FORM_LABELS = {
    "s": "名词复数",
    "p": "过去式",
    "d": "过去分词",
    "i": "现在分词",
    "3": "第三人称单数",
    "r": "比较级",
    "t": "最高级",
    "0": "原形",
}


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def parse_inflections(exchange):
    forms = []
    seen = set()
    for part in str(exchange or "").split("/"):
        if ":" not in part:
            continue
        kind, value = part.split(":", 1)
        value = value.strip()
        if kind == "1" or kind not in FORM_LABELS or not value:
            continue
        key = (kind, value.lower())
        if key in seen:
            continue
        seen.add(key)
        forms.append({"type": kind, "labelZh": FORM_LABELS[kind], "form": value})
    return forms


def relation_bucket(relation_type):
    if relation_type in {"synonym", "near_synonym"}:
        return "nearSynonyms"
    if relation_type == "antonym":
        return "antonyms"
    if relation_type in {"confusing", "contrast"}:
        return "confusingWords"
    return "relatedWords"


def main():
    core_rows = load_jsonl(CORE_DIR / "wordbook_words.json")
    core_ids = {row["wordId"] for row in core_rows}
    core_meta = {row["wordId"]: row for row in core_rows}

    words = load_jsonl(IMPORT_READY / "words.import.json")
    word_map = {row["_id"]: row for row in words}
    relations = load_jsonl(IMPORT_READY / "word_relations.import.json")
    groups = load_jsonl(IMPORT_READY / "word_relation_groups.import.json")

    core_relations = [row for row in relations if row.get("fromWordId") in core_ids]
    relation_map = defaultdict(list)
    for relation in core_relations:
        relation_map[relation["fromWordId"]].append(relation)

    group_ids = {row.get("groupId") for row in core_relations if row.get("groupId")}
    core_groups = [row for row in groups if row.get("_id") in group_ids]

    enriched_words = []
    editorial_rows = []
    editorial_details = []
    for word_id in sorted(core_ids, key=lambda value: core_meta[value]["order"]):
        word = dict(word_map[word_id])
        inflections = parse_inflections((word.get("ecdict") or {}).get("exchange"))
        if inflections:
            word["inflections"] = inflections
        enriched_words.append(word)

        word_relations = relation_map[word_id]
        relation_types = Counter(row.get("relationType") or "related" for row in word_relations)
        relation_examples = sum(bool(row.get("exampleEn")) for row in word_relations)
        relation_words = {
            "nearSynonyms": [],
            "antonyms": [],
            "confusingWords": [],
            "relatedWords": [],
        }
        relation_details = []
        for relation in word_relations:
            target = relation.get("toWord") or relation.get("toWordId") or ""
            bucket = relation_bucket(relation.get("relationType"))
            if target and target not in relation_words[bucket]:
                relation_words[bucket].append(target)
            relation_details.append({
                "wordId": relation.get("toWordId") or "",
                "word": target,
                "type": relation.get("relationType") or "related",
                "strength": relation.get("strength") or 0,
                "explanationEn": relation.get("explanationEn") or "",
                "explanationZh": relation.get("explanationZh") or "",
                "exampleEn": relation.get("exampleEn") or "",
                "exampleZh": relation.get("exampleZh") or "",
                "groupId": relation.get("groupId") or "",
            })
        senses = word.get("senses") or []
        has_primary_example = any(
            sense.get("exampleEn") or sense.get("examples")
            for sense in senses if isinstance(sense, dict)
        )
        editorial_rows.append({
            "order": core_meta[word_id]["order"],
            "day": core_meta[word_id]["chapter"],
            "wordId": word_id,
            "word": word.get("word") or core_meta[word_id]["word"],
            "translation": (senses[0].get("translation") if senses else ""),
            "inflectionCount": len(inflections),
            "relationCount": len(word_relations),
            "relationTypes": " ".join(f"{key}:{value}" for key, value in sorted(relation_types.items())),
            "nearSynonyms": " | ".join(relation_words["nearSynonyms"]),
            "antonyms": " | ".join(relation_words["antonyms"]),
            "confusingWords": " | ".join(relation_words["confusingWords"]),
            "relatedWords": " | ".join(relation_words["relatedWords"]),
            "relationExampleCount": relation_examples,
            "needsWordGroup": "yes" if not word_relations else "no",
            "needsPrimaryExample": "no" if has_primary_example else "yes",
            "exampleEn": "",
            "exampleZh": "",
            "editorStatus": "todo",
            "editorNote": "",
        })
        editorial_details.append({
            "order": core_meta[word_id]["order"],
            "day": core_meta[word_id]["chapter"],
            "wordId": word_id,
            "word": word.get("word") or core_meta[word_id]["word"],
            "translation": (senses[0].get("translation") if senses else ""),
            "inflections": inflections,
            "relations": relation_details,
            "primaryExample": {"en": "", "zh": "", "status": "todo"},
            "needsWordGroup": not bool(word_relations),
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT_DIR / "words.enriched.json", enriched_words)
    write_jsonl(OUT_DIR / "word_relations.json", core_relations)
    write_jsonl(OUT_DIR / "word_relation_groups.json", core_groups)
    with (OUT_DIR / "editorial_queue.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=editorial_rows[0].keys())
        writer.writeheader()
        writer.writerows(editorial_rows)
    (OUT_DIR / "editorial_queue.json").write_text(
        json.dumps(editorial_details, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    words_with_inflections = sum(bool(row.get("inflections")) for row in enriched_words)
    relation_covered = sum(bool(relation_map[word_id]) for word_id in core_ids)
    report = {
        "coreWords": len(core_ids),
        "wordsWithDefinitions": sum(bool(row.get("senses")) for row in enriched_words),
        "wordsWithInflections": words_with_inflections,
        "wordsWithRelations": relation_covered,
        "wordsNeedingRelations": len(core_ids) - relation_covered,
        "relations": len(core_relations),
        "relationGroups": len(core_groups),
        "relationsWithExamples": sum(bool(row.get("exampleEn")) for row in core_relations),
        "wordsNeedingPrimaryExamples": sum(row["needsPrimaryExample"] == "yes" for row in editorial_rows),
    }
    (OUT_DIR / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "README.md").write_text(
        "# 雅思 30 天词书增强基线\n\n"
        "这是一份审核基线，不应四个文件一起盲目导入。\n\n"
        "- `words.enriched.json`: 900 个完整 words 文档，新增结构化 `inflections`。\n"
        "- `word_relations.json`: 已有且以核心词为起点的词群关系。\n"
        "- `word_relation_groups.json`: 上述关系引用的词群。\n"
        "- `editorial_queue.csv`: 每词关联词列表、主例句和词群缺口。\n"
        "- `editorial_queue.json`: 每条关系的说明和双语例句完整展开。\n"
        "- `report.json`: 当前覆盖率。\n\n"
        "主例句缺失时保持空值，不使用模板句冒充真实用例。完成审核后，再生成正式导入包。\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
