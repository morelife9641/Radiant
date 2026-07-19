#!/usr/bin/env python3
"""Build a delivery README and manifest for word data imports."""

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "tmp" / "word_group_delivery"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def count_file(path):
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def relative(path):
    return str(path.relative_to(ROOT))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    words_report = load_json(ROOT / "tmp" / "cloud_import" / "words.ecdict_enriched.report.json")
    clean_report = load_json(ROOT / "tmp" / "word_relations_published_clean_import" / "report.json")
    balanced_report = load_json(ROOT / "tmp" / "word_relations_published_balanced_import" / "report.json")
    priority_report = load_json(ROOT / "tmp" / "word_relations_priority_import" / "report.json")
    curated_report = load_json(ROOT / "tmp" / "word_relations_curated_import" / "report.json")
    recommended_report = load_json(ROOT / "tmp" / "word_relations_recommended_import" / "report.json")
    full_report = load_json(ROOT / "tmp" / "word_relations_resemble_import" / "report.json")
    algorithmic_report = load_json(ROOT / "tmp" / "word_relations_algorithmic_import" / "report.json")

    recommended_relations_path = ROOT / "tmp" / "word_relations_recommended_import" / "word_relations.import.json"
    clean_relations = load_jsonl(recommended_relations_path)
    relation_type_counts = Counter(row.get("relationType") for row in clean_relations)
    per_word = defaultdict(int)
    for row in clean_relations:
        per_word[row.get("fromWordId")] += 1
    covered_words = len(per_word)

    manifest = {
        "formatNote": "All .json import files in this delivery are JSONL: one JSON object per line.",
        "recommendedImports": [
            {
                "collection": "words",
                "file": "tmp/cloud_import/words.ecdict_enriched.import.json",
                "mode": "overwrite/upsert by _id",
                "records": count_file(ROOT / "tmp" / "cloud_import" / "words.ecdict_enriched.import.json"),
                "note": "Includes senseId and ECDICT English/Chinese definition enrichment."
            },
            {
                "collection": "word_relation_groups",
                "file": "tmp/word_relations_recommended_import/word_relation_groups.import.json",
                "mode": "append/upsert by _id",
                "records": recommended_report["groups"],
                "note": "Merged recommended published relation groups: manual sample + balanced resemble + priority recovery + curated batch."
            },
            {
                "collection": "word_relations",
                "file": "tmp/word_relations_recommended_import/word_relations.import.json",
                "mode": "append/upsert by _id",
                "records": recommended_report["relations"],
                "note": "Merged recommended bidirectional relation edges."
            }
        ],
        "optionalReviewImports": [
            {
                "collection": "word_relation_groups",
                "file": "tmp/word_relations_algorithmic_import/word_relation_groups.draft.import.json",
                "mode": "append/upsert by _id",
                "records": algorithmic_report["draftGroups"],
                "note": "Draft only; current frontend does not display draft status."
            },
            {
                "collection": "word_relations",
                "file": "tmp/word_relations_algorithmic_import/word_relations.draft.import.json",
                "mode": "append/upsert by _id",
                "records": algorithmic_report["draftRelations"],
                "note": "Draft only; useful if you want reviewable candidates in the database."
            }
        ],
        "reviewOnlyFiles": [
            "tmp/word_relations_published_clean_import/review_groups.preview.json",
            "tmp/word_relations_published_clean_import/review_relations.preview.json",
            "tmp/word_relations_published_balanced_import/review_groups.preview.json",
            "tmp/word_relations_published_balanced_import/review_relations.preview.json",
            "tmp/word_relations_priority_import/review_groups.preview.json",
            "tmp/word_relations_curated_import/skipped.preview.json",
            "tmp/word_relation_candidates/relation_candidates.preview.csv",
            "tmp/word_relation_candidates/relation_candidates.preview.json"
        ],
        "stats": {
            "words": {
                "total": words_report["words"],
                "ecdictMatched": words_report["matched"],
                "ecdictMissing": words_report["missing"],
                "definitionEnAdded": words_report["definitionEnAdded"],
                "definitionZhAdded": words_report["definitionZhAdded"]
            },
            "recommendedPublishedRelations": {
                "groups": recommended_report["groups"],
                "relations": recommended_report["relations"],
                "coveredWords": covered_words,
                "relationTypeCounts": dict(relation_type_counts)
            },
            "componentBatches": {
                "balanced": {
                    "groups": balanced_report["cleanGroups"],
                    "relations": balanced_report["cleanRelations"]
                },
                "priorityRecovery": {
                    "groups": priority_report["groups"],
                    "relations": priority_report["relations"],
                    "reviewGroups": priority_report["reviewGroups"]
                },
                "manualCurated": {
                    "groups": curated_report["groups"],
                    "relations": curated_report["relations"]
                }
            },
            "strictPublishedRelations": {
                "groups": clean_report["cleanGroups"],
                "relations": clean_report["cleanRelations"]
            },
            "fullResembleBackup": {
                "groups": full_report["groups"],
                "relations": full_report["relations"],
                "skipped": full_report["skipped"]
            },
            "algorithmicDraft": {
                "groups": algorithmic_report["draftGroups"],
                "relations": algorithmic_report["draftRelations"],
                "reviewOnly": algorithmic_report["reviewOnly"]
            }
        }
    }

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    readme = f"""# Word Group Delivery

这些文件是给云数据库导入用的。虽然文件后缀是 `.json`，但格式按之前约定都是 JSONL：每行一个 JSON object。

## 推荐导入顺序

1. `words`
   - 文件：`{manifest["recommendedImports"][0]["file"]}`
   - 记录数：{manifest["recommendedImports"][0]["records"]}
   - 作用：给现有 `words` 补 `senseId`、英文释义、中文释义和 ECDICT 元信息。
   - 导入方式：按 `_id` 覆盖/更新，不要清空用户进度相关集合。

2. `word_relation_groups`
   - 文件：`{manifest["recommendedImports"][1]["file"]}`
   - 记录数：{manifest["recommendedImports"][1]["records"]}
   - 作用：推荐合并版可发布词群说明，包含手工样例、balanced resemble、priority recovery 和 curated batch。
   - 导入方式：追加或按 `_id` upsert。

3. `word_relations`
   - 文件：`{manifest["recommendedImports"][2]["file"]}`
   - 记录数：{manifest["recommendedImports"][2]["records"]}
   - 作用：词到词的双向关系边，详情页就是查这个集合。
   - 导入方式：追加或按 `_id` upsert。

## 这批数据规模

- `words`：{words_report["words"]} 条，ECDICT 命中 {words_report["matched"]} 条。
- recommended published 词群：{recommended_report["groups"]} 组，关系：{recommended_report["relations"]} 条，覆盖单词：{covered_words} 个。
- recommended 关系类型：{json.dumps(dict(relation_type_counts), ensure_ascii=False)}。
- 组成：balanced {balanced_report["cleanGroups"]} 组 / {balanced_report["cleanRelations"]} 条，priority {priority_report["groups"]} 组 / {priority_report["relations"]} 条，curated {curated_report["groups"]} 组 / {curated_report["relations"]} 条，另含 purpose 手工样例。
- strict 备选：{clean_report["cleanGroups"]} 组，{clean_report["cleanRelations"]} 条关系。如果你想极度保守，可以导 `tmp/word_relations_published_clean_import/*`。
- full resemble 备份：{full_report["groups"]} 组，{full_report["relations"]} 条关系，暂不建议直接全量发布。
- algorithmic draft：{algorithmic_report["draftGroups"]} 组，{algorithmic_report["draftRelations"]} 条关系，状态是 `draft`。

## 不建议直接导入展示的文件

- `tmp/word_relations_resemble_import/*`：大而全版本，里面有不少残缺词群，适合后续清洗。
- `tmp/word_relations_published_clean_import/review_*.preview.json`：从 full 里过滤出来的待 review 数据。
- `tmp/word_relation_candidates/*`：算法候选预览，尤其有“相关但不是同义”的情况。

## 覆盖报告

- `tmp/word_group_delivery/coverage.report.json`：当前推荐导入集的覆盖统计。
- `tmp/word_group_delivery/top_uncovered_words.csv`：优先补充的未覆盖高频词。
- `tmp/word_group_delivery/top_covered_words.csv`：关系最多的已覆盖词。

## 导入后检查

- 进 `purpose` 可以继续看之前的手工样例。
- 进 `succeed`、`prosper`、`thrive`、`flourish` 这一组应该能看到“易混淆”。
- 进 `element`、`component`、`constituent`、`ingredient` 这一组也应该能看到“易混淆”。

如果导入后详情页没变化，优先检查：

- `wordbook-fetch` 云函数是否部署到当前云环境。
- `word_relations` 是否有 `fromWordId` 索引。
- 详情页是否切到了“易混淆/近义词/反义词” tab。
"""
    (OUT_DIR / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({"outputDir": relative(OUT_DIR), "manifest": relative(OUT_DIR / "manifest.json"), "readme": relative(OUT_DIR / "README.md")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
