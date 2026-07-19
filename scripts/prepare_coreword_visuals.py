#!/usr/bin/env python3
"""Prepare manually selected core-word images for the word_visuals collection."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
ASSETS_ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3-assets")
SOURCE_DIR = Path("/Users/chengtingwei/Desktop/corewords")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
WORDBOOK_PATH = ROOT / "tmp/cloud_import_ielts_content_words/wordbook_words.json"
OUT_DIR = ASSETS_ROOT / "tmp/word_visuals"
IMAGE_DIR = OUT_DIR / "images"
IMPORT_DIR = OUT_DIR / "import"
VISUALS_PATH = IMPORT_DIR / "word_visuals.json"
MANIFEST_PATH = IMPORT_DIR / "upload_manifest.csv"
REPORT_PATH = IMPORT_DIR / "corewords_prepare_report.json"
COS_BASE = "https://word-content-assets-1411800061.cos.ap-guangzhou.myqcloud.com"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def first_translation(word: dict[str, Any]) -> str:
    senses = word.get("senses") or []
    return str((senses[0] if senses else {}).get("translation") or "").strip()


def default_phonetic(word: dict[str, Any]) -> str:
    phonetic = word.get("phonetic") or {}
    return str(phonetic.get("default") or phonetic.get("uk") or phonetic.get("us") or "").strip()


def cover_resize(src: Path, dest: Path, size: tuple[int, int] = (750, 1200)) -> tuple[int, int, int]:
    with Image.open(src) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        dest.parent.mkdir(parents=True, exist_ok=True)
        image.save(dest, "JPEG", quality=88, optimize=True, progressive=True)
    return size[0], size[1], dest.stat().st_size


def main() -> None:
    words = read_jsonl(WORDS_PATH)
    words_by_norm = {str(row.get("normalized") or row.get("word") or "").lower(): row for row in words}
    in_wordbook = {
        str(row.get("normalized") or row.get("word") or "").lower()
        for row in read_jsonl(WORDBOOK_PATH)
    }
    existing = read_jsonl(VISUALS_PATH)
    existing_by_word = {str(row.get("normalized") or row.get("word") or "").lower(): row for row in existing}

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    IMPORT_DIR.mkdir(parents=True, exist_ok=True)

    report = {"processed": [], "missingWord": [], "notInWordbook": [], "updated": [], "created": []}
    rows_by_word = dict(existing_by_word)

    for src in sorted(SOURCE_DIR.glob("*.jpg")):
        normalized = src.stem.strip().lower()
        word_doc = words_by_norm.get(normalized)
        if not word_doc:
            report["missingWord"].append(src.name)
            continue
        if normalized not in in_wordbook:
            report["notInWordbook"].append(normalized)

        dest = IMAGE_DIR / f"{normalized}.jpg"
        width, height, size_bytes = cover_resize(src, dest)
        local_path = f"word_visuals/{normalized}.jpg"
        now = None
        row = {
            "_id": f"visual_{word_doc['_id']}_001",
            "wordId": word_doc["_id"],
            "word": word_doc.get("word") or normalized,
            "normalized": normalized,
            "type": "daily_wallpaper",
            "title": word_doc.get("word") or normalized,
            "phonetic": default_phonetic(word_doc),
            "translationZh": first_translation(word_doc),
            "image": {
                "url": f"{COS_BASE}/{local_path}",
                "localPath": local_path,
                "width": width,
                "height": height,
                "format": "jpg",
                "sizeBytes": size_bytes,
            },
            "source": {
                "provider": "manual",
                "photographer": "",
                "sourceUrl": "",
                "licenseNote": "Image selected manually for vocabulary learning. Verify rights before public release.",
            },
            "status": "published",
            "weight": 1,
            "createdAt": (existing_by_word.get(normalized) or {}).get("createdAt", now),
            "updatedAt": now,
        }
        rows_by_word[normalized] = row
        report["processed"].append({"word": normalized, "wordId": word_doc["_id"], "image": str(dest), "sizeBytes": size_bytes})
        report["updated" if normalized in existing_by_word else "created"].append(normalized)

    next_rows = sorted(rows_by_word.values(), key=lambda row: str(row.get("normalized") or row.get("word") or ""))
    write_jsonl(VISUALS_PATH, next_rows)

    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["word", "sourcePath", "localImagePath", "cosKey", "cosUrl", "sizeBytes"])
        for row in next_rows:
            word = row["normalized"]
            image_path = IMAGE_DIR / f"{word}.jpg"
            writer.writerow([
                word,
                str(SOURCE_DIR / f"{word}.jpg") if (SOURCE_DIR / f"{word}.jpg").exists() else "",
                str(image_path),
                row["image"]["localPath"],
                row["image"]["url"],
                row["image"]["sizeBytes"],
            ])

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "sourceImages": len(list(SOURCE_DIR.glob("*.jpg"))),
        "processed": len(report["processed"]),
        "created": len(report["created"]),
        "updated": len(report["updated"]),
        "totalVisuals": len(next_rows),
        "missingWord": report["missingWord"],
        "notInWordbook": report["notInWordbook"],
        "visuals": str(VISUALS_PATH),
        "manifest": str(MANIFEST_PATH),
        "report": str(REPORT_PATH),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
