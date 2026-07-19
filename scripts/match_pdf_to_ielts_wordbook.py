#!/usr/bin/env python3
"""Match every page of an IELTS reading PDF against the local IELTS wordbook."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORDBOOK = ROOT / "miniprogram/assets/data/wordbooks/ielts.json"
DEFAULT_OUTPUT = ROOT / "docs/IELTS阅读真题2016-2017-词库匹配.md"
WORD_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")

# Printed page ranges from the book's contents. The printed and PDF page numbers align.
REGIONS = [
    (1, 3, "前言与目录"),
    (4, 18, "Reading Test 1"),
    (19, 33, "Reading Test 2"),
    (34, 49, "Reading Test 3"),
    (50, 63, "Reading Test 4"),
    (64, 79, "Reading Test 5"),
    (80, 97, "Reading Test 6"),
    (98, 111, "Reading Test 7"),
    (112, 126, "Reading Test 8"),
    (127, 142, "Reading Test 9"),
    (143, 157, "Reading Test 10"),
    (158, 164, "答案"),
]


def region_for_page(page: int) -> str:
    for start, end, name in REGIONS:
        if start <= page <= end:
            return name
    return "其他"


def normalize(value: str) -> str:
    return value.lower().replace("’", "'").strip()


def extract_pages(pdf: Path) -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    pages = result.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def lemma_candidates(token: str) -> list[str]:
    """Return conservative English inflection candidates in priority order."""
    values: list[str] = []

    def add(value: str) -> None:
        if len(value) >= 3 and value not in values:
            values.append(value)

    if token.endswith("'s"):
        add(token[:-2])
    if token.endswith("ies") and len(token) > 4:
        add(token[:-3] + "y")
    if token.endswith("es") and len(token) > 4:
        add(token[:-2])
        add(token[:-1])
    if token.endswith("s") and not token.endswith("ss") and len(token) > 3:
        add(token[:-1])
    if token.endswith("ied") and len(token) > 4:
        add(token[:-3] + "y")
    if token.endswith("ed") and len(token) > 4:
        stem = token[:-2]
        add(stem)
        add(token[:-1])
        if len(stem) > 3 and stem[-1] == stem[-2]:
            add(stem[:-1])
    if token.endswith("ing") and len(token) > 5:
        stem = token[:-3]
        add(stem)
        add(stem + "e")
        if len(stem) > 3 and stem[-1] == stem[-2]:
            add(stem[:-1])
    return values


def translation_for(item: dict) -> str:
    parts = []
    for sense in item.get("senses", []):
        pos = str(sense.get("pos", "")).strip()
        translation = str(sense.get("translation", "")).strip()
        value = f"{pos}. {translation}" if pos else translation
        if value and value not in parts:
            parts.append(value)
    return "；".join(parts).replace("|", "\\|")


def compact_pages(pages: set[int]) -> str:
    ordered = sorted(pages)
    ranges: list[str] = []
    start = previous = ordered[0]
    for page in ordered[1:]:
        if page == previous + 1:
            previous = page
            continue
        ranges.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = page
    ranges.append(str(start) if start == previous else f"{start}-{previous}")
    return ", ".join(ranges)


def match(pages: list[str], words: list[dict]) -> tuple[dict, Counter, Counter]:
    by_key = {normalize(item["word"]): item for item in words}
    single = {key for key in by_key if " " not in key}
    phrases = {key for key in by_key if " " in key}
    stats = defaultdict(lambda: {
        "count": 0,
        "exact": 0,
        "variant": 0,
        "pages": set(),
        "regions": Counter(),
        "forms": Counter(),
    })
    region_tokens = Counter()
    region_matches = Counter()

    for page_number, text in enumerate(pages, 1):
        region = region_for_page(page_number)
        raw_tokens = WORD_RE.findall(text)
        tokens = [normalize(token) for token in raw_tokens]
        region_tokens[region] += len(tokens)

        # Longest phrase first; phrase hits intentionally coexist with their component words.
        normalized_text = " ".join(tokens)
        for phrase in phrases:
            count = len(re.findall(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", normalized_text))
            if count:
                entry = stats[phrase]
                entry["count"] += count
                entry["exact"] += count
                entry["pages"].add(page_number)
                entry["regions"][region] += count
                entry["forms"][phrase] += count
                region_matches[region] += count

        for surface in tokens:
            key = surface if surface in single else None
            mode = "exact"
            if key is None:
                mode = "variant"
                key = next((candidate for candidate in lemma_candidates(surface) if candidate in single), None)
            if key is None:
                continue
            entry = stats[key]
            entry["count"] += 1
            entry[mode] += 1
            entry["pages"].add(page_number)
            entry["regions"][region] += 1
            entry["forms"][surface] += 1
            region_matches[region] += 1

    return stats, region_tokens, region_matches


def render_report(
    pdf: Path,
    wordbook_path: Path,
    meta: dict,
    words: list[dict],
    pages: list[str],
    stats: dict,
    region_tokens: Counter,
    region_matches: Counter,
) -> str:
    matched = len(stats)
    occurrences = sum(item["count"] for item in stats.values())
    exact = sum(item["exact"] for item in stats.values())
    variant = sum(item["variant"] for item in stats.values())
    total_tokens = sum(region_tokens.values())
    important_total = sum(bool(item.get("important")) for item in words)
    important_matched = sum(bool(next(w for w in words if normalize(w["word"]) == key).get("important")) for key in stats)
    item_by_key = {normalize(item["word"]): item for item in words}

    out = [
        "# IELTS Reading Actual Tests 2016-2017 与 IELTS 词库匹配报告",
        "",
        "## 数据与口径",
        "",
        f"- PDF：`{pdf.name}`，共 {len(pages)} 页；全文文本（前言、10 套试题、题目及答案）均参与匹配。",
        f"- 词库：`{wordbook_path.relative_to(ROOT)}`，{meta.get('name', 'IELTS')}，共 {len(words):,} 个词条。",
        "- 精确命中：忽略大小写，按完整单词边界匹配；词组允许空格规范化。",
        "- 词形命中：仅处理常见且保守的所有格、复数、过去式和 `-ing` 形式；不做同义词或语义推断。",
        "- 词组命中与组成它的单词命中会同时计数，因此“命中次数”不是互斥 token 数。页码为 PDF 页码。",
        "",
        "## 总览",
        "",
        "| 指标 | 结果 |",
        "|---|---:|",
        f"| PDF 英文 token 数 | {total_tokens:,} |",
        f"| 命中词条数 | {matched:,} / {len(words):,}（{matched / len(words):.1%}） |",
        f"| 命中总次数 | {occurrences:,} |",
        f"| 精确命中次数 | {exact:,} |",
        f"| 词形还原命中次数 | {variant:,} |",
        f"| important 词条命中 | {important_matched:,} / {important_total:,} |",
        "",
        "## 分区统计",
        "",
        "| 内容区间 | PDF 页码 | 英文 token | 命中次数 | 命中密度 | 独立词条 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for start, end, region in REGIONS:
        unique = sum(1 for item in stats.values() if region in item["regions"])
        token_count = region_tokens[region]
        hit_count = region_matches[region]
        density = hit_count / token_count if token_count else 0
        out.append(f"| {region} | {start}-{end} | {token_count:,} | {hit_count:,} | {density:.1%} | {unique:,} |")

    out.extend([
        "",
        "## 高频命中 Top 100",
        "",
        "| 排名 | 单词 | 释义 | 次数 | 精确/词形 | 页数 | 出现卷次 |",
        "|---:|---|---|---:|---:|---:|---|",
    ])
    ranked = sorted(stats.items(), key=lambda pair: (-pair[1]["count"], pair[0]))
    for rank, (key, data) in enumerate(ranked[:100], 1):
        item = item_by_key[key]
        regions = "、".join(region for _, _, region in REGIONS if region in data["regions"])
        out.append(
            f"| {rank} | **{item['word']}** | {translation_for(item)} | {data['count']} | "
            f"{data['exact']}/{data['variant']} | {len(data['pages'])} | {regions} |"
        )

    out.extend([
        "",
        "## 全部命中词条",
        "",
        "按出现次数降序排列。`实际词形` 最多展示 8 种；带 `★` 的是词库 important 词条。",
        "",
        "| 序号 | 词条 | 音标 | 释义 | 次数 | 精确/词形 | PDF 页码 | 实际词形 |",
        "|---:|---|---|---|---:|---:|---|---|",
    ])
    for rank, (key, data) in enumerate(ranked, 1):
        item = item_by_key[key]
        marker = " ★" if item.get("important") else ""
        phonetic = str(item.get("phonetic", "")).replace("|", "\\|")
        forms = "、".join(form for form, _ in data["forms"].most_common(8))
        out.append(
            f"| {rank} | **{item['word']}**{marker} | {phonetic} | {translation_for(item)} | "
            f"{data['count']} | {data['exact']}/{data['variant']} | {compact_pages(data['pages'])} | {forms} |"
        )

    unmatched = sorted(
        (item for item in words if normalize(item["word"]) not in stats),
        key=lambda item: normalize(item["word"]),
    )
    out.extend([
        "",
        "## 未命中词条",
        "",
        f"共 {len(unmatched):,} 个。此处保留完整清单，便于后续反查或扩充语料。",
        "",
        ", ".join(f"`{item['word']}`" for item in unmatched),
        "",
    ])
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--wordbook", type=Path, default=DEFAULT_WORDBOOK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = json.loads(args.wordbook.read_text(encoding="utf-8"))
    pages = extract_pages(args.pdf)
    stats, region_tokens, region_matches = match(pages, payload["words"])
    report = render_report(
        args.pdf,
        args.wordbook,
        payload["wordbook"],
        payload["words"],
        pages,
        stats,
        region_tokens,
        region_matches,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"wrote {len(stats):,} matched entries to {args.output}")


if __name__ == "__main__":
    main()
