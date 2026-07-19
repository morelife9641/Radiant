#!/usr/bin/env python3
"""Extract the 2025 Sep-Dec IELTS speaking question bank into Markdown."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
SOURCE_DIR = Path("/Users/chengtingwei/Downloads/2025年9-12月口语题库/2025年9-12月新题/25年9-12月口语题库")
OUT = ROOT / "tmp/ielts_speaking_question_bank_2025_09_12.md"
P1 = SOURCE_DIR / "25年9-12月题库P1必考题+老题（题目版）.pdf"
P2 = SOURCE_DIR / "25年9-12月题库P2新题+老题（题目版）.pdf"
P3 = SOURCE_DIR / "25年9-12月题库P3新题+老题（题目版）.pdf"

BULLET_RE = re.compile(r"^\s*[•·]\s*(.+)$")
NUMBERED_RE = re.compile(r"^\s*(\d+)\.\s*(.+)$")
QUESTION_START = re.compile(
    r"^(what|why|how|do|did|does|are|is|have|has|would|when|who|which|can|will|please|at|on|where)\b",
    re.I,
)


def extract(path: Path) -> str:
    return subprocess.check_output(["pdftotext", "-raw", str(path), "-"], text=True).replace("\f", "\n")


def clean(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value


def is_section(value: str) -> bool:
    value = clean(value)
    return not value or value.startswith("Part ")


def is_p1_heading(value: str) -> bool:
    value = clean(value)
    if not value or value.startswith("Part "):
        return False
    if NUMBERED_RE.match(value):
        return True
    # Wrapped question lines in the extracted PDF are usually lowercase
    # fragments ("careers", "now and in the past"). Topic titles start with
    # an uppercase letter and do not end in a question mark.
    return (
        value[:1].isupper()
        and not value.endswith("?")
        and not QUESTION_START.match(value)
        and not value.startswith(("•", "·"))
        and len(value) < 80
    )


def extract_bullets(path: Path, numbered_topics: bool) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    topic = ""
    current = ""
    for raw in extract(path).splitlines():
        line = clean(raw)
        if not line:
            continue
        heading = NUMBERED_RE.match(line) if numbered_topics else None
        if heading:
            if current:
                rows.append((topic, clean(current)))
                current = ""
            topic = clean(heading.group(2))
            continue
        bullet = BULLET_RE.match(line)
        if bullet:
            if current:
                rows.append((topic, clean(current)))
            current = clean(bullet.group(1))
            continue
        if current:
            # Wrapped question line (for example, after a PDF page break).
            if not line.startswith("Part ") and not (not numbered_topics and is_p1_heading(line)):
                current = f"{current} {line}"
            else:
                rows.append((topic, clean(current)))
                current = ""
        if not current and (line.startswith("Part ") or is_p1_heading(line)):
            topic = clean(line)
    if current:
        rows.append((topic, clean(current)))
    return rows


def extract_part2(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    current_number = ""
    current_zh = ""
    current_en = ""
    for raw in extract(path).splitlines():
        line = clean(raw)
        if not line:
            continue
        match = NUMBERED_RE.match(line)
        if match:
            if current_number and current_en:
                rows.append((current_zh, current_en))
            current_number = match.group(1)
            current_zh = clean(match.group(2))
            current_en = ""
            continue
        if current_number and not current_en:
            current_en = line
        elif current_number and current_en:
            current_en = f"{current_en} {line}"
    if current_number and current_en:
        rows.append((current_zh, current_en))
    return rows


def build() -> str:
    p1_rows = extract_bullets(P1, numbered_topics=False)
    p2_rows = extract_part2(P2)
    p3_rows = extract_bullets(P3, numbered_topics=True)
    out: list[str] = [
        "# IELTS Speaking 2025 年 9-12 月题库",
        "",
        "整理范围：Part 1、Part 2、Part 3 题目版。",
        "",
        f"- Part 1：{len(p1_rows)} 题",
        f"- Part 2：{len(p2_rows)} 题卡",
        f"- Part 3：{len(p3_rows)} 题",
        f"- 合计：{len(p1_rows) + len(p2_rows) + len(p3_rows)} 条",
        "",
        "## Part 1：日常问答",
        "",
    ]
    last_topic = None
    for topic, question in p1_rows:
        if topic != last_topic:
            out.extend([f"### {topic}", ""])
            last_topic = topic
        out.append(f"- {question}")
    out.extend(["", "## Part 2：个人陈述题卡", ""])
    for index, (zh, en) in enumerate(p2_rows, 1):
        out.extend([f"### {index}. {zh}", "", en, ""])
    out.extend(["## Part 3：深入讨论", ""])
    last_topic = None
    for topic, question in p3_rows:
        if topic != last_topic:
            out.extend([f"### {topic}", ""])
            last_topic = topic
        out.append(f"- {question}")
    out.append("")
    return "\n".join(out)


def main() -> None:
    text = build()
    OUT.write_text(text, encoding="utf-8")
    print({"path": str(OUT), "bytes": len(text.encode("utf-8")), "questionMarkers": text.count("\n- ")})


if __name__ == "__main__":
    main()
