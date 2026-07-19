#!/usr/bin/env python3
"""Append obvious IELTS antonym/near-synonym suggestions across the wordbook."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
ECDICT_PATH = ROOT / "ECDICT-master/ecdict.csv"
SUGGESTIONS_PATH = DATA_DIR / "word_lexical_suggestions.json"
REPORT_PATH = DATA_DIR / "obvious_antonym_enrichment_report.json"


ANTONYM_PAIRS = [
    ("negative", "positive"),
    ("active", "inactive"),
    ("actual", "potential"),
    ("adequate", "inadequate"),
    ("admit", "deny"),
    ("advanced", "basic"),
    ("advantage", "drawback"),
    ("affluent", "impoverished"),
    ("ancient", "modern"),
    ("appear", "disappear"),
    ("appear", "vanish"),
    ("appropriate", "inappropriate"),
    ("available", "unavailable"),
    ("aware", "ignorant"),
    ("benefit", "drawback"),
    ("combine", "separate"),
    ("compatible", "incompatible"),
    ("complete", "incomplete"),
    ("complex", "simple"),
    ("conscious", "unconscious"),
    ("conserve", "waste"),
    ("construct", "destroy"),
    ("conventional", "unorthodox"),
    ("cooperative", "uncooperative"),
    ("current", "previous"),
    ("decrease", "increase"),
    ("deficiency", "abundance"),
    ("deficit", "surplus"),
    ("destruction", "preservation"),
    ("destructive", "constructive"),
    ("domestic", "overseas"),
    ("dominant", "subordinate"),
    ("durable", "fragile"),
    ("effective", "ineffective"),
    ("efficient", "inefficient"),
    ("emerge", "disappear"),
    ("enable", "hamper"),
    ("endorse", "oppose"),
    ("endanger", "protect"),
    ("enhance", "weaken"),
    ("essential", "nonessential"),
    ("exclude", "include"),
    ("exclusive", "inclusive"),
    ("expand", "contract"),
    ("export", "import"),
    ("extensive", "limited"),
    ("external", "internal"),
    ("fake", "genuine"),
    ("flexible", "rigid"),
    ("formal", "informal"),
    ("former", "latter"),
    ("frequent", "rare"),
    ("general", "particular"),
    ("generous", "stingy"),
    ("global", "local"),
    ("grim", "cheerful"),
    ("heterogeneous", "homogeneous"),
    ("hospitable", "inhospitable"),
    ("impossible", "possible"),
    ("improve", "worsen"),
    ("improvement", "deterioration"),
    ("include", "exclude"),
    ("indigenous", "foreign"),
    ("inferior", "superior"),
    ("influential", "insignificant"),
    ("initial", "final"),
    ("inside", "outside"),
    ("insufficient", "sufficient"),
    ("internal", "external"),
    ("legal", "illegal"),
    ("likely", "unlikely"),
    ("limited", "unlimited"),
    ("major", "minor"),
    ("majority", "minority"),
    ("maximum", "minimum"),
    ("mental", "physical"),
    ("minimal", "maximal"),
    ("minimum", "maximum"),
    ("moral", "immoral"),
    ("natural", "artificial"),
    ("normal", "abnormal"),
    ("optimism", "pessimism"),
    ("optimistic", "pessimistic"),
    ("original", "imitation"),
    ("orthodox", "unorthodox"),
    ("particular", "general"),
    ("passive", "active"),
    ("permanent", "temporary"),
    ("permit", "prohibit"),
    ("positive", "negative"),
    ("presence", "absence"),
    ("preserve", "destroy"),
    ("previous", "subsequent"),
    ("primary", "secondary"),
    ("private", "public"),
    ("productive", "unproductive"),
    ("prohibit", "permit"),
    ("protect", "endanger"),
    ("random", "systematic"),
    ("regular", "irregular"),
    ("relevant", "irrelevant"),
    ("reliable", "unreliable"),
    ("reluctant", "willing"),
    ("resistant", "vulnerable"),
    ("responsible", "irresponsible"),
    ("rigid", "flexible"),
    ("rural", "urban"),
    ("secure", "insecure"),
    ("senior", "junior"),
    ("separate", "combine"),
    ("shallow", "deep"),
    ("significant", "insignificant"),
    ("similar", "different"),
    ("simple", "complex"),
    ("specific", "generic"),
    ("stable", "unstable"),
    ("steady", "unsteady"),
    ("strengthen", "weaken"),
    ("substantial", "insubstantial"),
    ("subsequent", "previous"),
    ("sufficient", "insufficient"),
    ("suitable", "unsuitable"),
    ("superficial", "deep"),
    ("superior", "inferior"),
    ("sustainable", "unsustainable"),
    ("synthetic", "natural"),
    ("temporary", "permanent"),
    ("traditional", "modern"),
    ("unique", "common"),
    ("urban", "rural"),
    ("valid", "invalid"),
    ("variable", "constant"),
    ("visible", "invisible"),
    ("vague", "precise"),
    ("vanish", "appear"),
    ("valuable", "worthless"),
    ("vast", "tiny"),
    ("vulnerable", "resistant"),
    ("weaken", "strengthen"),
    ("wealthy", "poor"),
    ("willing", "reluctant"),
]


NEAR_SYNONYMS = {
    "negative": ["passive", "adverse", "unfavourable", "pessimistic"],
    "positive": ["favourable", "constructive", "optimistic", "affirmative"],
    "passive": ["inactive", "submissive", "unassertive", "receptive"],
    "insufficient": ["inadequate", "deficient", "scarce", "not enough"],
    "visible": ["observable", "apparent", "noticeable", "clear"],
    "formal": ["official", "structured", "proper", "ceremonial"],
    "valid": ["legitimate", "sound", "well-founded", "reasonable"],
}


ADJECTIVE_PREFIX_ALLOWLIST = {
    ("accessible", "inaccessible"),
    ("adequate", "inadequate"),
    ("appropriate", "inappropriate"),
    ("available", "unavailable"),
    ("capable", "incapable"),
    ("compatible", "incompatible"),
    ("complete", "incomplete"),
    ("consistent", "inconsistent"),
    ("conscious", "unconscious"),
    ("creative", "uncreative"),
    ("distinct", "indistinct"),
    ("efficient", "inefficient"),
    ("essential", "nonessential"),
    ("formal", "informal"),
    ("frequent", "infrequent"),
    ("legal", "illegal"),
    ("mature", "immature"),
    ("moral", "immoral"),
    ("possible", "impossible"),
    ("precise", "imprecise"),
    ("proper", "improper"),
    ("regular", "irregular"),
    ("relevant", "irrelevant"),
    ("reliable", "unreliable"),
    ("responsible", "irresponsible"),
    ("secure", "insecure"),
    ("sufficient", "insufficient"),
    ("suitable", "unsuitable"),
    ("visible", "invisible"),
    ("willing", "unwilling"),
}


BLOCKED_AUTO_ANTONYMS = {
    ("acceptable", "inacceptable"),
    ("accessible", "unaccessible"),
    ("advanced", "unadvanced"),
    ("apparent", "inapparent"),
    ("apparent", "unapparent"),
    ("available", "nonavailable"),
    ("capable", "uncapable"),
    ("distinct", "tinct"),
    ("equal", "inequal"),
    ("essential", "inessential"),
    ("essential", "unessential"),
    ("frequent", "unfrequent"),
    ("negative", "nonnegative"),
    ("positive", "dispositive"),
    ("positive", "nonpositive"),
}


PREFIX_TARGETS = {
    "un": [
        "acceptable", "available", "aware", "certain", "clear", "comfortable",
        "common", "conscious", "controlled", "desirable", "equal", "expected",
        "fair", "favourable", "healthy", "important", "likely", "limited",
        "necessary", "pleasant", "productive", "reliable", "successful",
        "suitable", "stable", "steady", "usual", "willing",
    ],
    "in": [
        "active", "adequate", "appropriate", "capable", "complete", "consistent",
        "correct", "dependent", "direct", "effective", "efficient", "formal",
        "frequent", "secure", "sufficient", "visible",
    ],
    "im": ["mature", "mobile", "moral", "partial", "patient", "perfect", "possible", "precise", "proper", "pure"],
    "ir": ["regular", "relevant", "responsible", "resistible"],
    "il": ["legal", "legible", "literate", "logical"],
    "dis": ["advantage", "agree", "appear", "approve", "connect", "continue", "honest", "integrate", "like", "order", "similar"],
    "non": ["essential", "existent", "verbal"],
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def load_ecdict_entries() -> dict[str, dict[str, str]]:
    with ECDICT_PATH.open(encoding="utf-8", errors="ignore") as f:
        return {row["word"].lower(): row for row in csv.DictReader(f) if row.get("word")}


def is_adjective_entry(entry: dict[str, str] | None) -> bool:
    if not entry:
        return False
    text = f"{entry.get('translation') or ''}\n{entry.get('definition') or ''}".lower()
    return any(marker in text for marker in ["a.", "adj.", "\na ", "\ns "])


def make_id(word: str, relation_type: str, target: str) -> str:
    safe = f"{word}_{relation_type}_{target}".lower()
    for ch in " /.-'’":
        safe = safe.replace(ch, "_")
    while "__" in safe:
        safe = safe.replace("__", "_")
    return f"lex_obvious_{safe.strip('_')}"


def make_relation(
    *,
    word: str,
    target: str,
    relation_type: str,
    word_ids: dict[str, str],
    global_word_ids: dict[str, str],
    source: str,
    strength: int,
) -> dict[str, Any]:
    if relation_type == "antonym":
        explanation = f"{word} 与 {target} 是常见反义或方向相反的表达；具体语义需按词性和上下文复核。"
        example_en = f"The contrast between {word} and {target} is important in academic reading."
        example_zh = f"{word} 和 {target} 的对比在学术阅读中很常见。"
    else:
        explanation = f"{word} 与 {target} 可作为近义/同类表达学习；是否能直接替换取决于词性、搭配和语境。"
        example_en = f"In context, {word} can be compared with {target}, but they are not always interchangeable."
        example_zh = f"在语境中，{word} 可以和 {target} 对照学习，但不一定总能互换。"
    return {
        "_id": make_id(word, relation_type, target),
        "wordId": word_ids[word],
        "word": word,
        "targetWordId": word_ids.get(target) or global_word_ids.get(target),
        "targetWord": target,
        "targetInWordbook": target in word_ids,
        "targetInGlobalWords": target in global_word_ids,
        "relationType": relation_type,
        "strength": strength,
        "explanationZh": explanation,
        "exampleEn": example_en,
        "exampleZh": example_zh,
        "source": source,
        "status": "draft",
        "reviewStatus": "ai_suggested_pending_human_review",
        "createdAt": None,
        "updatedAt": None,
    }


def add_relation(
    suggestions: dict[str, dict[str, Any]],
    existing: set[tuple[str, str, str]],
    *,
    word: str,
    target: str,
    relation_type: str,
    word_ids: dict[str, str],
    global_word_ids: dict[str, str],
    source: str,
    strength: int,
) -> bool:
    if word not in word_ids or not target or word == target:
        return False
    key = (word, relation_type, target.lower())
    if key in existing:
        return False
    relation = make_relation(
        word=word,
        target=target,
        relation_type=relation_type,
        word_ids=word_ids,
        global_word_ids=global_word_ids,
        source=source,
        strength=strength,
    )
    if relation["_id"] in suggestions:
        return False
    suggestions[relation["_id"]] = relation
    existing.add(key)
    return True


def main() -> None:
    wordbook = read_jsonl(DATA_DIR / "wordbook_words.json")
    suggestions_rows = read_jsonl(SUGGESTIONS_PATH)
    global_words = read_jsonl(WORDS_PATH)
    ecdict_entries = load_ecdict_entries()
    ecdict_words = set(ecdict_entries)

    word_ids = {row["word"].lower(): row["wordId"] for row in wordbook}
    global_word_ids = {
        str(row.get("normalized") or row.get("word") or "").lower(): row["_id"]
        for row in global_words
        if row.get("_id")
    }
    suggestions = {row["_id"]: row for row in suggestions_rows}
    removed_blocked = 0
    allowed_auto_pairs = ADJECTIVE_PREFIX_ALLOWLIST | {(b, a) for a, b in ADJECTIVE_PREFIX_ALLOWLIST}
    for sid, row in list(suggestions.items()):
        pair = (str(row.get("word") or "").lower(), str(row.get("targetWord") or "").lower())
        if row.get("source") == "adjective_prefix_antonym_scan" and (
            pair in BLOCKED_AUTO_ANTONYMS or pair not in allowed_auto_pairs
        ):
            suggestions.pop(sid)
            removed_blocked += 1
    suggestions_rows = list(suggestions.values())
    existing = {
        (str(row.get("word") or "").lower(), str(row.get("relationType") or ""), str(row.get("targetWord") or "").lower())
        for row in suggestions_rows
    }

    added_antonyms = 0
    added_synonyms = 0

    for left, right in ANTONYM_PAIRS:
        left = left.lower()
        right = right.lower()
        if add_relation(
            suggestions,
            existing,
            word=left,
            target=right,
            relation_type="antonym",
            word_ids=word_ids,
            global_word_ids=global_word_ids,
            source="manual_obvious_antonym_axis",
            strength=5,
        ):
            added_antonyms += 1
        if right in word_ids and add_relation(
            suggestions,
            existing,
            word=right,
            target=left,
            relation_type="antonym",
            word_ids=word_ids,
            global_word_ids=global_word_ids,
            source="manual_obvious_antonym_axis",
            strength=5,
        ):
            added_antonyms += 1

    for word, targets in NEAR_SYNONYMS.items():
        for target in targets:
            if add_relation(
                suggestions,
                existing,
                word=word.lower(),
                target=target.lower(),
                relation_type="near_synonym",
                word_ids=word_ids,
                global_word_ids=global_word_ids,
                source="manual_obvious_synonym_gap",
                strength=4,
            ):
                added_synonyms += 1

    prefix_added = 0
    for prefix, bases in PREFIX_TARGETS.items():
        for base in bases:
            base = base.lower()
            negative = f"{prefix}{base}"
            if negative not in ecdict_words and negative not in global_word_ids and negative not in word_ids:
                continue
            if base in word_ids and add_relation(
                suggestions,
                existing,
                word=base,
                target=negative,
                relation_type="antonym",
                word_ids=word_ids,
                global_word_ids=global_word_ids,
                source="prefix_antonym_scan",
                strength=4,
            ):
                prefix_added += 1
            if negative in word_ids and add_relation(
                suggestions,
                existing,
                word=negative,
                target=base,
                relation_type="antonym",
                word_ids=word_ids,
                global_word_ids=global_word_ids,
                source="prefix_antonym_scan",
                strength=4,
            ):
                prefix_added += 1

    adjective_prefix_added = 0
    adjective_prefixes = ["un", "in", "im", "ir", "il", "dis", "non"]
    for word in sorted(word_ids):
        entry = ecdict_entries.get(word)
        if not is_adjective_entry(entry):
            continue
        for prefix in adjective_prefixes:
            target = f"{prefix}{word}"
            if (
                (word, target) in ADJECTIVE_PREFIX_ALLOWLIST
                and target in ecdict_words
                and is_adjective_entry(ecdict_entries.get(target))
            ):
                if add_relation(
                    suggestions,
                    existing,
                    word=word,
                    target=target,
                    relation_type="antonym",
                    word_ids=word_ids,
                    global_word_ids=global_word_ids,
                    source="adjective_prefix_antonym_scan",
                    strength=4,
                ):
                    adjective_prefix_added += 1
        for prefix in adjective_prefixes:
            if not word.startswith(prefix) or len(word) <= len(prefix) + 2:
                continue
            base = word[len(prefix):]
            if (
                (base, word) in ADJECTIVE_PREFIX_ALLOWLIST
                and base in ecdict_words
                and is_adjective_entry(ecdict_entries.get(base))
            ):
                if add_relation(
                    suggestions,
                    existing,
                    word=word,
                    target=base,
                    relation_type="antonym",
                    word_ids=word_ids,
                    global_word_ids=global_word_ids,
                    source="adjective_prefix_antonym_scan",
                    strength=4,
                ):
                    adjective_prefix_added += 1

    rows = sorted(suggestions.values(), key=lambda item: (item["word"], item["relationType"], item["targetWord"]))
    write_jsonl(SUGGESTIONS_PATH, rows)
    report = {
        "before": len(suggestions_rows),
        "after": len(rows),
        "addedAntonyms": added_antonyms,
        "addedPrefixAntonyms": prefix_added,
        "addedAdjectivePrefixAntonyms": adjective_prefix_added,
        "addedNearSynonyms": added_synonyms,
        "removedBlockedAutoAntonyms": removed_blocked,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
