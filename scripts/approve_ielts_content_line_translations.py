#!/usr/bin/env python3
"""Mark IELTS content line translations as reviewed after human approval."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
LINES_PATH = DATA_DIR / "content_lines.json"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    rows = read_jsonl(LINES_PATH)
    for row in rows:
        row["status"] = "published"
        row["translationStatus"] = "reviewed"
        meta = row.setdefault("translationMeta", {})
        meta["reviewStatus"] = "reviewed"
        meta["reviewMethod"] = "human_batch_approval"
        meta["reviewedAt"] = None
        if row.get("sourceReview", {}).get("status") == "needs_source_verification":
            row.setdefault("releaseWarnings", [])
            warning = "source_text_needs_verification"
            if warning not in row["releaseWarnings"]:
                row["releaseWarnings"].append(warning)
    write_jsonl(LINES_PATH, rows)
    print(f"approvedContentLines={len(rows)}")


if __name__ == "__main__":
    main()
