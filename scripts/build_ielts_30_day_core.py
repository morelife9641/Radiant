"""Build a 900-word IELTS core book for a 30-day study plan.

The script only creates a wordbook document and wordbook_words relations. It
reuses the existing records in the words collection.
"""

import csv
import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IELTS_SOURCE = ROOT / "miniprogram/assets/data/wordbooks/ielts.json"
ECDICT_SOURCE = ROOT / "ECDICT-master/ecdict.csv"
OUT_DIR = ROOT / "tmp/cloud_import_ielts_30_day"
BOOK_ID = "ielts-30-day"
WORD_COUNT = 900
DAYS = 30


def normalize(value):
    return (value or "").strip().lower()


def word_id_for(normalized):
    slug = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    slug = re.sub(r"_+", "_", slug)
    if slug:
        return f"word_{slug}"
    digest = hashlib.md5(normalized.encode("utf-8")).hexdigest()[:12]
    return f"word_{digest}"


def load_ecdict(wanted):
    rows = {}
    with ECDICT_SOURCE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            word = normalize(row.get("word"))
            if word in wanted:
                rows[word] = row
    return rows


def rank_value(row):
    values = []
    for field in ("bnc", "frq"):
        try:
            value = int(row.get(field) or 0)
        except ValueError:
            value = 0
        if value > 0:
            values.append(value)
    return min(values) if values else 100_000


def frequency_score(rank):
    if rank >= 100_000:
        return 0.0
    # Smoothly rewards useful corpus frequency without letting basic words
    # overwhelm IELTS relevance signals.
    return max(0.0, 36.0 * (1.0 - math.log10(max(rank, 1)) / 5.0))


def score_word(item, row):
    tags = set((row.get("tag") or "").split())
    rank = rank_value(row)
    score = frequency_score(rank)
    score += 45 if item.get("important") else 0
    score += 50 if "ielts" in tags else 0
    score += 14 if "toefl" in tags else 0
    score += 12 if "cet6" in tags else 0
    score += 8 if "ky" in tags else 0

    if "gre" in tags and not tags.intersection({"ielts", "toefl", "cet6"}):
        score -= 12
    if re.search(r"\s", item["word"]):
        score -= 5

    return round(score, 4), rank, tags


def write_json_lines(path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def distribute_across_days(ranked):
    """Give every day a mix of high, medium and lower ranked core words."""
    day_groups = [[] for _ in range(DAYS)]
    for rank_index, item in enumerate(ranked):
        day_groups[rank_index % DAYS].append(item)
    return [item for group in day_groups for item in group]


def main():
    payload = json.loads(IELTS_SOURCE.read_text(encoding="utf-8"))
    words = payload["words"]
    wanted = {normalize(item["word"]) for item in words}
    ecdict = load_ecdict(wanted)

    candidates = []
    for item in words:
        normalized = normalize(item["word"])
        score, corpus_rank, tags = score_word(item, ecdict.get(normalized, {}))
        candidates.append({
            "item": item,
            "normalized": normalized,
            "score": score,
            "corpusRank": corpus_rank,
            "tags": tags,
        })

    ranked = sorted(
        candidates,
        key=lambda row: (-row["score"], row["corpusRank"], row["item"]["order"]),
    )[:WORD_COUNT]
    ordered = distribute_across_days(ranked)

    book = {
        "_id": BOOK_ID,
        "name": "雅思 30 天核心词",
        "category": "exam",
        "cefrLevel": "B2-C1",
        "totalWords": WORD_COUNT,
        "description": "考前 30 天冲刺词书，每天 30 词",
        "cover": {"letter": "30", "color": "#D93645"},
        "status": "published",
        "schemaVersion": 1,
        "contentVersion": 1,
        "source": {
            "name": "IELTS Word List + ECDICT frequency ranking",
            "importedAt": None,
        },
        "createdAt": None,
        "updatedAt": None,
    }

    relations = []
    review_rows = []
    for order, candidate in enumerate(ordered, 1):
        item = candidate["item"]
        word_id = word_id_for(candidate["normalized"])
        day = (order - 1) // (WORD_COUNT // DAYS) + 1
        relations.append({
            "_id": f"{BOOK_ID}:{word_id}",
            "bookId": BOOK_ID,
            "wordId": word_id,
            "word": item["word"],
            "normalized": candidate["normalized"],
            "order": order,
            "chapter": f"Day {day:02d}",
            "important": True,
            "bookSenseOverride": None,
            "createdAt": None,
            "updatedAt": None,
        })
        review_rows.append({
            "order": order,
            "day": day,
            "word": item["word"],
            "translation": item.get("senses", [{}])[0].get("translation", ""),
            "score": candidate["score"],
            "corpus_rank": candidate["corpusRank"],
            "source_important": bool(item.get("important")),
            "ecdict_tags": " ".join(sorted(candidate["tags"])),
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json_lines(OUT_DIR / "wordbooks.json", [book])
    write_json_lines(OUT_DIR / "wordbook_words.json", relations)
    with (OUT_DIR / "selection_review.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=review_rows[0].keys())
        writer.writeheader()
        writer.writerows(review_rows)

    source_important = sum(row["source_important"] for row in review_rows)
    tagged_ielts = sum("ielts" in row["ecdict_tags"].split() for row in review_rows)
    report = f"""# 雅思 30 天核心词书

- 词书 ID: `{BOOK_ID}`
- 总词数: {WORD_COUNT}
- 计划: {DAYS} 天，每天 {WORD_COUNT // DAYS} 词
- 原雅思词书重点词: {source_important}
- ECDICT 含 IELTS 标签: {tagged_ielts}
- `words` 新增记录: 0（全部复用现有单词）

## 导入

1. 向 `wordbooks` 导入 `wordbooks.json`。
2. 向 `wordbook_words` 导入 `wordbook_words.json`。
3. 两个文件扩展名为 `.json`，文件内容为每行一个 JSON 对象。
4. 不要再次导入 `words`，否则会产生唯一索引冲突。

`selection_review.csv` 用于人工抽查，不导入数据库。
"""
    (OUT_DIR / "README.md").write_text(report, encoding="utf-8")

    print(f"Built {WORD_COUNT} words in {DAYS} chapters")
    print(f"Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
