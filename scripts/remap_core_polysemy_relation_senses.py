#!/usr/bin/env python3
"""Remap word relation sense scopes after semantic polysemy splits."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
RELATIONS_PATH = DATA_DIR / "word_relations.json"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
REPORT_PATH = DATA_DIR / "core_polysemy_relation_sense_remap_report.json"


DEFAULT_REMAP = {
    "advance_adj_01": "advance_v_move_01",
    "charge_n_01": "charge_n_cost_01",
    "demand_n_01": "demand_n_request_01",
    "effect_n_01": "effect_n_result_01",
    "feature_n_01": "feature_n_characteristic_01",
    "grant_n_01": "grant_n_money_01",
    "interest_n_01": "interest_n_benefit_01",
    "point_n_01": "point_n_idea_01",
    "process_n_01": "process_n_steps_01",
    "stock_n_01": "stock_n_goods_01",
    "supply_n_01": "supply_n_amount_01",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def remap_by_context(word: str, old_sense_id: str, rel: dict[str, Any]) -> str | None:
    other = rel.get("toWord") if rel.get("fromWord") == word else rel.get("fromWord")
    text = f"{rel.get('explanationZh') or ''} {rel.get('explanationEn') or ''}".lower()

    if old_sense_id == "range_n_01":
        if other in {"mount", "volcano"} or any(term in text for term in ["山", "mountain", "volcano"]):
            return "range_n_land_01"
        if any(term in text for term in ["系列", "set", "series"]):
            return "range_n_series_01"
        return "range_n_scope_01"

    if old_sense_id == "design_n_01":
        if other in {"pattern", "figure"} or any(term in text for term in ["图案", "样式", "pattern"]):
            return "design_n_pattern_01"
        if other == "create" or any(term in text for term in ["设计", "create", "plan"]):
            return "design_v_create_01" if other == "create" else "design_n_plan_01"
        return "design_n_plan_01"

    if old_sense_id == "figure_n_01":
        if other in {"pattern", "design", "form", "outline"}:
            return "figure_n_shape_01"
        if any(term in text for term in ["数字", "number", "amount"]):
            return "figure_n_number_01"
        return "figure_n_shape_01"

    if old_sense_id == "form_n_01":
        if other == "register" or any(term in text for term in ["表格", "document"]):
            return "form_n_document_01"
        return "form_n_type_01"

    if old_sense_id == "position_n_01":
        if other == "attitude" or any(term in text for term in ["立场", "观点", "opinion", "attitude"]):
            return "position_n_opinion_01"
        if other in {"setting", "location", "spot"}:
            return "position_n_place_01"
        return "position_n_place_01"

    if old_sense_id == "match_n_01":
        if other == "competition":
            return "match_n_competition_01"
        if other == "equal" or any(term in text for term in ["相配", "equal"]):
            return "match_n_equal_01"
        return "match_n_equal_01"

    return DEFAULT_REMAP.get(old_sense_id)


def main() -> None:
    relations = read_jsonl(RELATIONS_PATH)
    words = read_jsonl(WORDS_PATH)
    valid = {row["_id"]: {sense["senseId"] for sense in row.get("senses") or []} for row in words}
    updates: list[dict[str, str]] = []

    for rel in relations:
        scope = rel.get("senseScope")
        if not isinstance(scope, dict):
            continue
        for side in ("from", "to"):
            word = rel.get(f"{side}Word")
            word_id = rel.get(f"{side}WordId")
            key = f"{side}SenseId"
            old = scope.get(key)
            if not word or not old or not word_id:
                continue
            if old in valid.get(word_id, set()):
                continue
            new = remap_by_context(str(word), str(old), rel)
            if not new:
                continue
            scope[key] = new
            updates.append(
                {
                    "relationId": rel.get("_id", ""),
                    "word": str(word),
                    "field": key,
                    "old": str(old),
                    "new": new,
                }
            )

    remaining_invalid = []
    for rel in relations:
        scope = rel.get("senseScope") or {}
        for side in ("from", "to"):
            word_id = rel.get(f"{side}WordId")
            sid = scope.get(f"{side}SenseId")
            if word_id in valid and sid and sid not in valid[word_id]:
                remaining_invalid.append({"relationId": rel.get("_id", ""), "wordId": word_id, "senseId": sid})

    write_jsonl(RELATIONS_PATH, relations)
    REPORT_PATH.write_text(
        json.dumps({"updatedCount": len(updates), "remainingInvalid": remaining_invalid, "updates": updates}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"updated relation scopes: {len(updates)}")
    print(f"remaining invalid: {len(remaining_invalid)}")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
