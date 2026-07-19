#!/usr/bin/env python3
"""Serve the IELTS review page with small write APIs for local curation."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
OUT_DIR = ROOT / "tmp/ielts_review_tool"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
SUGGESTIONS_PATH = DATA_DIR / "word_lexical_suggestions.json"
RELATIONS_PATH = DATA_DIR / "word_relations.json"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"
AUDIT_PATH = DATA_DIR / "review_deletions_audit.jsonl"
SHORT_DEFINITION_REVIEW_AUDIT_PATH = DATA_DIR / "short_definition_review_audit.jsonl"
BUILD_SCRIPT = ROOT / "scripts/build_ielts_word_inventory_review_page.py"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).lower()


def synonym_text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("word") or value.get("text") or value.get("value") or value.get("normalized") or "")
    return str(value or "")


def remove_from_synonym_value(value: Any, target: str) -> tuple[Any, int]:
    target_norm = norm(target)
    if not value:
        return value, 0
    if isinstance(value, list):
        next_items = []
        removed = 0
        for item in value:
            if norm(synonym_text(item)) == target_norm:
                removed += 1
            else:
                next_items.append(item)
        return next_items, removed
    if isinstance(value, str):
        parts = [part.strip() for part in re.split(r"[,;/，；、\n]+", value) if part.strip()]
        if len(parts) <= 1:
            return ("", 1) if norm(value) == target_norm else (value, 0)
        kept = [part for part in parts if norm(part) != target_norm]
        return ", ".join(kept), len(parts) - len(kept)
    return value, 0


def delete_dictionary_synonyms(word_id: str, target: str) -> int:
    rows = read_jsonl(WORDS_PATH)
    removed = 0
    changed = False
    for row in rows:
        if row.get("_id") != word_id:
            continue
        for sense in row.get("senses") or []:
            next_value, count = remove_from_synonym_value(sense.get("synonyms"), target)
            if count:
                sense["synonyms"] = next_value
                removed += count
                changed = True
    if changed:
        write_jsonl(WORDS_PATH, rows)
    return removed


def delete_lexical_suggestions(word_id: str, target: str) -> int:
    rows = read_jsonl(SUGGESTIONS_PATH)
    target_norm = norm(target)
    kept = []
    removed = 0
    for row in rows:
        is_match = (
            row.get("wordId") == word_id
            and row.get("relationType") == "near_synonym"
            and norm(row.get("targetWord")) == target_norm
        )
        if is_match:
            removed += 1
        else:
            kept.append(row)
    if removed:
        write_jsonl(SUGGESTIONS_PATH, kept)
    return removed


def delete_word_relations(word_id: str, word: str, target: str) -> int:
    rows = read_jsonl(RELATIONS_PATH)
    word_norm = norm(word)
    target_norm = norm(target)
    kept = []
    removed = 0
    for row in rows:
        relation_type = row.get("relationType")
        is_near = relation_type in {"near_synonym", "confusing"}
        outward = row.get("fromWordId") == word_id and norm(row.get("toWord")) == target_norm
        inward = row.get("toWordId") == word_id and norm(row.get("fromWord")) == target_norm
        fallback = norm(row.get("fromWord")) == word_norm and norm(row.get("toWord")) == target_norm
        if is_near and (outward or inward or fallback):
            removed += 1
        else:
            kept.append(row)
    if removed:
        write_jsonl(RELATIONS_PATH, kept)
    return removed


def rebuild_page() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ROOT), check=True)


def append_audit(payload: dict[str, Any], removed: dict[str, int]) -> None:
    row = {"action": "delete_synonym", "payload": payload, "removed": removed}
    with AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def review_short_definitions(payload: dict[str, Any]) -> dict[str, int]:
    rows = read_jsonl(LEARNING_PATH)
    by_word_id = {row.get("wordId"): row for row in rows}
    updated = 0
    approved = 0
    rejected = 0
    for item in payload.get("items") or []:
        if not isinstance(item, dict):
            continue
        word_id = str(item.get("wordId") or "").strip()
        decision = str(item.get("decision") or "").strip()
        short_definition = str(item.get("shortDefinitionEn") or "").strip()
        if not word_id or decision not in {"approved", "rejected"} or not short_definition:
            continue
        row = by_word_id.get(word_id)
        if not row:
            continue
        row["shortDefinitionEn"] = short_definition
        row["shortDefinitionStatus"] = "human_reviewed" if decision == "approved" else "human_flagged_for_revision"
        row["shortDefinitionReview"] = {
            "status": decision,
            "labelZh": "已通过" if decision == "approved" else "有问题",
            "reviewedAt": item.get("reviewedAt") or payload.get("submittedAt"),
            "reviewSource": "ielts_word_inventory_review_page",
            "originalShortDefinitionEn": item.get("originalShortDefinitionEn") or "",
        }
        provenance = row.setdefault("provenance", {})
        if isinstance(provenance, dict):
            provenance["reviewStatus"] = "short_definition_reviewed" if decision == "approved" else "short_definition_needs_revision"
        updated += 1
        if decision == "approved":
            approved += 1
        else:
            rejected += 1
    if updated:
        write_jsonl(LEARNING_PATH, rows)
        audit_row = {
            "action": "review_short_definitions",
            "submittedAt": payload.get("submittedAt"),
            "updated": updated,
            "approved": approved,
            "rejected": rejected,
            "items": payload.get("items") or [],
        }
        with SHORT_DEFINITION_REVIEW_AUDIT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(audit_row, ensure_ascii=False, separators=(",", ":")) + "\n")
    return {"updated": updated, "approved": approved, "rejected": rejected}


class ReviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(OUT_DIR), **kwargs)

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path not in {"/api/delete-synonym", "/api/review-short-definitions"}:
            self.send_json(404, {"ok": False, "error": "Unknown endpoint"})
            return
        try:
            length = int(self.headers.get("Content-Length") or "0")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if self.path == "/api/review-short-definitions":
                result = review_short_definitions(payload)
                rebuild_page()
                self.send_json(200, {"ok": True, **result})
                return
            word_id = str(payload.get("wordId") or "").strip()
            word = str(payload.get("word") or "").strip()
            target = str(payload.get("targetWord") or "").strip()
            if not word_id or not target:
                raise ValueError("wordId and targetWord are required")
            removed = {
                "lexicalSuggestions": delete_lexical_suggestions(word_id, target),
                "wordRelations": delete_word_relations(word_id, word, target),
                "dictionarySynonyms": delete_dictionary_synonyms(word_id, target),
            }
            rebuild_page()
            append_audit(payload, removed)
            self.send_json(200, {"ok": True, "removed": removed})
        except Exception as exc:  # noqa: BLE001 - local review API should return the exact failure.
            self.send_json(500, {"ok": False, "error": str(exc)})


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 8765), ReviewHandler)
    print("Serving IELTS review tool at http://127.0.0.1:8765/ielts_word_inventory.html")
    server.serve_forever()


if __name__ == "__main__":
    main()
