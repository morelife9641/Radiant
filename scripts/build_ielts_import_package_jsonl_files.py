#!/usr/bin/env python3
"""Create .jsonl copies of the IELTS import package for CloudBase imports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
PACKAGE_DIR = ROOT / "tmp/cloud_import_ielts_content_words/import_package"
OUT_DIR = PACKAGE_DIR / "jsonl"


FILES = [
    ("words.ielts_content_words.json", "words.jsonl", "words"),
    ("wordbooks.json", "wordbooks.jsonl", "wordbooks"),
    ("wordbook_words.json", "wordbook_words.jsonl", "wordbook_words"),
    ("content_topics.json", "content_topics.jsonl", "content_topics"),
    ("content_lines.json", "content_lines.jsonl", "content_lines"),
    ("content_line_words.json", "content_line_words.jsonl", "content_line_words"),
    ("word_learning_content.json", "word_learning_content.jsonl", "word_learning_content"),
    ("word_relation_groups.json", "word_relation_groups.jsonl", "word_relation_groups"),
    ("word_relations.json", "word_relations.jsonl", "word_relations"),
    ("word_lexical_suggestions.json", "word_lexical_suggestions.jsonl", "word_lexical_suggestions"),
]


def read_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text[0] == "[":
        return json.loads(text)
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for src_name, out_name, collection in FILES:
        rows = read_json_or_jsonl(PACKAGE_DIR / src_name)
        out_path = OUT_DIR / out_name
        write_jsonl(out_path, rows)
        # Verify every line is a JSON object, not an array wrapper.
        verified = 0
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise RuntimeError(f"{out_path} contains non-object JSONL row")
            verified += 1
        if verified != len(rows):
            raise RuntimeError(f"{out_path} verified {verified}, expected {len(rows)}")
        manifest.append(
            {
                "collection": collection,
                "file": str(out_path),
                "sourceFile": src_name,
                "count": len(rows),
                "mode": "upsert",
                "format": "json_lines",
            }
        )

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme = [
        "# JSON Lines Import Files",
        "",
        "这些文件是一行一个 JSON 对象的 JSON Lines 格式，适合 CloudBase/Tencent 云开发数据库导入提示“请检查是否为 JSON Lines 格式”的入口。",
        "",
        "全部使用 upsert。",
        "",
        "| 顺序 | 集合 | 文件 | 条数 |",
        "| --- | --- | --- | ---: |",
    ]
    for index, item in enumerate(manifest, 1):
        readme.append(f"| {index} | `{item['collection']}` | `{Path(item['file']).name}` | {item['count']} |")
    readme.append("")
    readme.append("注意：`words.jsonl` 的目标集合是 `words`，不是 `words.ielts_content_words`。")
    (OUT_DIR / "README.md").write_text("\n".join(readme), encoding="utf-8")
    print(json.dumps({"outDir": str(OUT_DIR), "files": manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
