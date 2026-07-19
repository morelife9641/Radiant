#!/usr/bin/env python3
"""Create JSON-array copies of the IELTS import package for cloud consoles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
PACKAGE_DIR = ROOT / "tmp/cloud_import_ielts_content_words/import_package"
OUT_DIR = PACKAGE_DIR / "json_array"


FILES = [
    ("words.ielts_content_words.json", "words.json", "words"),
    ("wordbooks.json", "wordbooks.json", "wordbooks"),
    ("wordbook_words.json", "wordbook_words.json", "wordbook_words"),
    ("content_topics.json", "content_topics.json", "content_topics"),
    ("content_lines.json", "content_lines.json", "content_lines"),
    ("content_line_words.json", "content_line_words.json", "content_line_words"),
    ("word_learning_content.json", "word_learning_content.json", "word_learning_content"),
    ("word_relation_groups.json", "word_relation_groups.json", "word_relation_groups"),
    ("word_relations.json", "word_relations.json", "word_relations"),
    ("word_lexical_suggestions.json", "word_lexical_suggestions.json", "word_lexical_suggestions"),
]


def read_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text[0] == "[":
        return json.loads(text)
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for src_name, out_name, collection in FILES:
        rows = read_json_or_jsonl(PACKAGE_DIR / src_name)
        out_path = OUT_DIR / out_name
        out_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest.append(
            {
                "collection": collection,
                "file": str(out_path),
                "sourceFile": src_name,
                "count": len(rows),
                "mode": "upsert",
            }
        )

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme = [
        "# JSON Array Import Files",
        "",
        "这些文件是给云控制台 JSON 导入用的数组版。原 import_package 根目录下是一行一个对象的 JSONL；如果控制台不支持 JSONL，可能出现导入成功 0。",
        "",
        "全部使用 upsert。",
        "",
        "| 顺序 | 集合 | 文件 | 条数 |",
        "| --- | --- | --- | ---: |",
    ]
    for index, item in enumerate(manifest, 1):
        readme.append(f"| {index} | `{item['collection']}` | `{Path(item['file']).name}` | {item['count']} |")
    readme.append("")
    readme.append("注意：`words.ielts_content_words.json` 在数组版里改名为 `words.json`，目标集合仍然是 `words`。")
    (OUT_DIR / "README.md").write_text("\n".join(readme), encoding="utf-8")
    print(json.dumps({"outDir": str(OUT_DIR), "files": manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
