#!/usr/bin/env python3
"""Fix remaining words.senses structural issues after broad POS splitting."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
REPORT_PATH = ROOT / "tmp/cloud_import_ielts_content_words/fix_remaining_word_sense_structure_issues_report.json"


MANUAL_WORD_FIXES: dict[str, list[dict[str, str]]] = {
    "word_equal": [
        {"senseId": "equal_v_01", "pos": "v", "translation": "等于；比得上"},
        {"senseId": "equal_a_01", "pos": "a", "translation": "相等的；平等的；胜任的"},
        {"senseId": "equal_n_01", "pos": "n", "translation": "同等的人或物；匹敌者"},
    ],
    "word_snap": [
        {"senseId": "snap_v_01", "pos": "v", "translation": "咔嚓折断；啪地打开或关上；厉声说；咬"},
        {"senseId": "snap_n_01", "pos": "n", "translation": "咔嚓声；快照；突然的一段时间"},
        {"senseId": "snap_a_01", "pos": "a", "translation": "突然的；仓促的"},
        {"senseId": "snap_adv_01", "pos": "adv", "translation": "啪地；猛地"},
    ],
    "word_divide": [
        {"senseId": "divide_v_01", "pos": "v", "translation": "分开；分隔；分配；除以"},
        {"senseId": "divide_n_01", "pos": "n", "translation": "分歧；分界线；分水岭"},
    ],
    "word_industrialise": [
        {"senseId": "industrialise_v_01", "pos": "v", "translation": "（使）工业化"},
    ],
    "word_remain": [
        {"senseId": "remain_v_01", "pos": "v", "translation": "保持；仍然是；剩下；逗留"},
        {"senseId": "remain_n_01", "pos": "n", "translation": "残余；遗迹；遗体"},
    ],
    "word_campfire": [
        {"senseId": "campfire_n_01", "pos": "n", "translation": "营火；篝火"},
    ],
    "word_transmute": [
        {"senseId": "transmute_v_01", "pos": "v", "translation": "改变；使变形；使变质"},
    ],
    "word_sentient": [
        {"senseId": "sentient_a_01", "pos": "a", "translation": "有感觉能力的；有知觉的"},
    ],
}


PHRASE_POS_OVERRIDES = {
    "roll film": "n",
    "notice board": "n",
    "inductive reasoning": "n",
    "sulphuric acid": "n",
    "orientation meeting": "n",
    "id card": "n",
    "journal": "n",
    "track and field": "n",
    "bring out": "v",
    "bump into": "v",
    "bring around/round": "v",
    "get off track": "v",
    "pull up stakes": "v",
    "snap up": "v",
    "hang on": "v",
    "pore over": "v",
    "tick off": "v",
    "lead to": "v",
    "vice versa": "adv",
    "at random": "adv",
    "and so forth": "adv",
    "spot on": "a",
    "in vain": "adv",
    "for instance": "adv",
    "as if/though": "conj",
    "at least": "adv",
    "in addition": "adv",
    "in accordance with": "prep",
    "in favour of": "prep",
    "as for/to": "prep",
    "on the horizon": "prep",
    "for the sake of": "prep",
    "in comparison with": "prep",
    "in addition to": "prep",
}


POS_RE = re.compile(r"\b(adj|adv|prep|conj|pron|excl|vt|vi|n|v|a)(?:\./|/)?\.?\s*", re.I)
SLASH_PRON_RE = re.compile(r"/[^/\n]+/")
BRACKET_PRON_RE = re.compile(r"[\[{][^\]}]+[\]}]")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def clean_translation(text: Any) -> str:
    value = str(text or "")
    value = SLASH_PRON_RE.sub(" ", value)
    value = BRACKET_PRON_RE.sub(" ", value)
    value = POS_RE.sub(" ", value)
    value = value.replace("]", " ").replace("[", " ").replace("{", " ").replace("}", " ")
    return re.sub(r"\s+", " ", value).strip(" ;；,，")


def base_sense(template: dict[str, Any], spec: dict[str, str]) -> dict[str, Any]:
    sense = dict(template)
    sense["senseId"] = spec["senseId"]
    sense["pos"] = spec["pos"]
    sense["translation"] = spec["translation"]
    sense["definitionEn"] = ""
    sense["definitionZh"] = f"该词作{pos_label(spec['pos'])}时表示：{spec['translation']}。"
    sense["synonyms"] = sense.get("synonyms") or []
    sense["antonyms"] = sense.get("antonyms") or []
    return sense


def pos_label(pos: str) -> str:
    return {
        "n": "名词",
        "v": "动词",
        "a": "形容词",
        "adv": "副词",
        "prep": "介词",
        "conj": "连词",
        "pron": "代词",
        "excl": "感叹词",
    }.get(pos, "对应词性")


def main() -> None:
    rows = read_jsonl(WORDS_PATH)
    changed: list[dict[str, Any]] = []

    for row in rows:
        word_id = str(row.get("_id") or "")
        word = str(row.get("word") or "").strip().lower()
        senses = row.get("senses") or []
        if not senses:
            continue

        before = json.loads(json.dumps(senses, ensure_ascii=False))

        if word_id in MANUAL_WORD_FIXES:
            template = senses[0]
            row["senses"] = [base_sense(template, spec) for spec in MANUAL_WORD_FIXES[word_id]]
        else:
            override_pos = PHRASE_POS_OVERRIDES.get(word)
            if override_pos:
                for sense in senses:
                    if not str(sense.get("pos") or "").strip():
                        sense["pos"] = override_pos
                    cleaned = clean_translation(sense.get("translation"))
                    if cleaned:
                        sense["translation"] = cleaned
                    if str(sense.get("senseId") or "").endswith("_sense_01"):
                        normalized = re.sub(r"[^a-z0-9]+", "_", str(row.get("normalized") or word)).strip("_")
                        sense["senseId"] = f"{normalized}_{override_pos}_01"

        after = row.get("senses") or []
        if before != after:
            changed.append(
                {
                    "wordId": word_id,
                    "word": row.get("word"),
                    "before": [
                        {"senseId": s.get("senseId"), "pos": s.get("pos"), "translation": s.get("translation")}
                        for s in before
                    ],
                    "after": [
                        {"senseId": s.get("senseId"), "pos": s.get("pos"), "translation": s.get("translation")}
                        for s in after
                    ],
                }
            )

    write_jsonl(WORDS_PATH, rows)
    REPORT_PATH.write_text(
        json.dumps({"changedCount": len(changed), "changed": changed}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"changed: {len(changed)}")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
