#!/usr/bin/env python3
"""
Build compressed word wallpaper assets and JSONL import files.

Input images are named by word, e.g. miniprogram/assets/covers/universe.jpg.
Output images are cropped to a home-wallpaper-friendly portrait ratio.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "miniprogram" / "assets" / "covers"
DEFAULT_OUTPUT = ROOT / "tmp" / "word_visuals"
DEFAULT_BASE_URL = "https://word-content-assets-1411800061.cos.ap-guangzhou.myqcloud.com"
DEFAULT_COS_PREFIX = "word_visuals"
WORD_RE = re.compile(r"^[a-z]+(?:[-_][a-z]+)*$")


def normalize_word(value: str) -> str:
    return value.strip().lower().replace("_", "-")


def word_id_for(word: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", word.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return f"word_{slug}" if slug else ""


def load_wordbooks() -> dict:
    items = {}
    for path in [
        ROOT / "miniprogram" / "assets" / "data" / "wordbooks" / "ielts.json",
        ROOT / "miniprogram" / "assets" / "data" / "wordbooks" / "cet4.json",
    ]:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data.get("words", data if isinstance(data, list) else [])
        for row in rows:
            if not isinstance(row, dict):
                continue
            word = normalize_word(str(row.get("word", "")))
            if word and word not in items:
                items[word] = row
    return items


def load_ecdict() -> dict:
    path = ROOT / "ECDICT-master" / "ecdict.csv"
    items = {}
    if not path.exists():
        return items
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = normalize_word(row.get("word", ""))
            if word:
                items[word] = row
    return items


def first_translation(row: dict) -> str:
    senses = row.get("senses")
    if isinstance(senses, list) and senses:
        return str(senses[0].get("translation") or "").strip()

    translation = str(row.get("translation") or "").strip()
    if translation:
        return shorten_translation(translation)
    return ""


def shorten_translation(value: str) -> str:
    value = value.replace("\\n", "\n")
    first_line = value.splitlines()[0].strip()
    first_line = re.sub(r"^\[[^\]]+\]\s*", "", first_line)
    first_line = re.sub(r"^[a-zA-Z./]+\s*", "", first_line)
    first_line = first_line.replace(",", "，").replace(";", "；")
    parts = [part.strip() for part in re.split(r"[，；]", first_line) if part.strip()]
    if parts:
        return "；".join(parts[:2])
    return first_line[:18]


def first_pos(row: dict) -> str:
    senses = row.get("senses")
    if isinstance(senses, list) and senses:
        return str(senses[0].get("pos") or "").strip()
    return str(row.get("pos") or "").strip().rstrip(".")


def clean_phonetic(value: str) -> str:
    value = (value or "").strip()
    return value if not value or value.startswith("/") else f"/{value}/"


def build_word_doc(word: str, row: dict, now_ms: int) -> dict:
    translation = first_translation(row)
    pos = first_pos(row)
    phonetic = clean_phonetic(str(row.get("phonetic") or ""))
    return {
        "_id": word_id_for(word),
        "word": word,
        "normalized": word,
        "type": "word",
        "phonetic": {
            "uk": "",
            "us": "",
            "default": phonetic,
        },
        "audio": {
            "us": "",
            "uk": "",
        },
        "audioPolicy": None,
        "senses": [
            {
                "pos": pos,
                "translation": translation,
                "definitionEn": "",
                "definitionZh": "",
                "collinsEn": "",
                "collinsZh": "",
                "synonyms": [],
                "antonyms": [],
                "gamingLink": None,
            }
        ],
        "contextStats": {
            "totalLines": 0,
            "byTopic": {},
        },
        "createdAt": now_ms,
        "updatedAt": now_ms,
    }


def run_magick(src: Path, dst: Path, width: int, height: int, quality: int) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "magick",
        str(src),
        "-auto-orient",
        "-resize",
        f"{width}x{height}^",
        "-gravity",
        "center",
        "-extent",
        f"{width}x{height}",
        "-strip",
        "-interlace",
        "Plane",
        "-quality",
        str(quality),
        str(dst),
    ], check=True)


def image_size(path: Path) -> tuple[int, int]:
    result = subprocess.run(
        ["identify", "-format", "%w %h", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    w, h = result.stdout.strip().split()
    return int(w), int(h)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            f.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process word visual images for home/daily cards.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--cos-prefix", default=DEFAULT_COS_PREFIX)
    parser.add_argument("--width", type=int, default=750)
    parser.add_argument("--height", type=int, default=1200)
    parser.add_argument("--quality", type=int, default=72)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ecdict_rows = load_ecdict()
    now_ms = int(time.time() * 1000)

    image_dir = args.out / "images"
    import_dir = args.out / "import"
    visual_rows = []
    missing_word_rows = []
    manifest_rows = []

    files = sorted([p for p in args.input.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}])
    for src in files:
        word = normalize_word(src.stem)
        if not WORD_RE.match(word):
            print(f"skip invalid word filename: {src.name}")
            continue

        row = ecdict_rows.get(word) or {}
        if row:
            missing_word_rows.append(build_word_doc(word, row, now_ms))
        else:
            missing_word_rows.append(build_word_doc(word, {"translation": "", "phonetic": "", "pos": ""}, now_ms))

        dst_name = f"{word}.jpg"
        dst = image_dir / dst_name
        run_magick(src, dst, args.width, args.height, args.quality)
        width, height = image_size(dst)
        local_path = f"{args.cos_prefix.strip('/')}/{dst_name}"
        url = f"{args.base_url.rstrip('/')}/{local_path}"

        visual_rows.append({
            "_id": f"visual_{word_id_for(word)}_001",
            "wordId": word_id_for(word),
            "word": word,
            "normalized": word,
            "type": "daily_wallpaper",
            "title": word,
            "phonetic": clean_phonetic(str(row.get("phonetic") or "")),
            "translationZh": first_translation(row),
            "image": {
                "url": url,
                "localPath": local_path,
                "width": width,
                "height": height,
                "format": "jpg",
                "sizeBytes": dst.stat().st_size,
            },
            "source": {
                "provider": "manual",
                "photographer": "",
                "sourceUrl": "",
                "licenseNote": "Image selected manually for vocabulary learning. Verify rights before public release.",
            },
            "status": "published",
            "weight": 1,
            "createdAt": now_ms,
            "updatedAt": now_ms,
        })

        manifest_rows.append({
            "word": word,
            "source": str(src),
            "output": str(dst),
            "cosPath": local_path,
            "url": url,
            "sizeBytes": dst.stat().st_size,
        })

    write_jsonl(import_dir / "word_visuals.jsonl", visual_rows)
    write_jsonl(import_dir / "missing_words.jsonl", missing_word_rows)
    with (import_dir / "upload_manifest.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["word", "source", "output", "cosPath", "url", "sizeBytes"])
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"Processed {len(visual_rows)} images -> {image_dir}")
    print(f"Wrote {import_dir / 'word_visuals.jsonl'}")
    print(f"Wrote {import_dir / 'missing_words.jsonl'} ({len(missing_word_rows)} rows)")
    print(f"Wrote {import_dir / 'upload_manifest.csv'}")


if __name__ == "__main__":
    main()
