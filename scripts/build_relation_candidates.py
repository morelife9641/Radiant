#!/usr/bin/env python3
"""Generate review-only relation candidates from definitions/translations.

This script does not create import-ready production relations. It creates
preview JSON/CSV files for human review, so weak algorithmic matches do not
pollute word_relations.
"""

import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORDS = ROOT / "tmp" / "cloud_import" / "words.ecdict_enriched.import.json"
DEFAULT_EXISTING_RELATIONS = ROOT / "tmp" / "word_relations_resemble_import" / "word_relations.import.json"
DEFAULT_OUT_DIR = ROOT / "tmp" / "word_relation_candidates"

STOPWORDS = {
    "a", "an", "the", "of", "or", "to", "and", "in", "on", "for", "with",
    "by", "from", "as", "is", "are", "be", "being", "that", "which",
    "someone", "something", "person", "thing", "one", "used", "using",
    "having", "relating", "related", "especially", "usually", "often",
    "act", "state", "quality", "make", "cause", "become", "have", "has"
}


def load_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def tokenize(text):
    words = re.findall(r"[a-z][a-z'-]{2,}", str(text or "").lower())
    result = []
    for word in words:
        word = word.strip("'")
        if word in STOPWORDS:
            continue
        if word.endswith("ing") and len(word) > 5:
            word = word[:-3]
        elif word.endswith("ed") and len(word) > 4:
            word = word[:-2]
        elif word.endswith("s") and len(word) > 4:
            word = word[:-1]
        if word and word not in STOPWORDS:
            result.append(word)
    return result


def zh_tokens(text):
    # Coarse Chinese keyword extraction. Good enough for candidate scoring, not
    # used as a final source of truth.
    cleaned = re.sub(r"[a-zA-Z0-9\\[\\]().,;:，。；：、（）/]+", " ", str(text or ""))
    parts = re.split(r"\\s+|[，。；、；,;]", cleaned)
    return [item.strip() for item in parts if len(item.strip()) >= 2]


def word_text(word):
    sense = word.get("senses", [{}])[0] if word.get("senses") else {}
    return "\\n".join([
        sense.get("definitionEn") or "",
        sense.get("definitionZh") or "",
        sense.get("translation") or "",
    ])


def vectorize(words):
    docs = []
    df = Counter()
    for word in words:
        sense = word.get("senses", [{}])[0] if word.get("senses") else {}
        terms = tokenize(sense.get("definitionEn") or "")
        terms += [f"zh:{x}" for x in zh_tokens((sense.get("definitionZh") or "") + "\\n" + (sense.get("translation") or ""))]
        counts = Counter(terms)
        docs.append(counts)
        for term in counts:
            df[term] += 1

    total = len(words)
    vectors = []
    norms = []
    for counts in docs:
        vec = {}
        for term, count in counts.items():
            idf = math.log((total + 1) / (df[term] + 1)) + 1
            vec[term] = count * idf
        norm = math.sqrt(sum(value * value for value in vec.values())) or 1
        vectors.append(vec)
        norms.append(norm)
    return vectors, norms


def cosine(vec_a, norm_a, vec_b, norm_b):
    if len(vec_a) > len(vec_b):
        vec_a, vec_b = vec_b, vec_a
        norm_a, norm_b = norm_b, norm_a
    dot = sum(value * vec_b.get(term, 0) for term, value in vec_a.items())
    return dot / (norm_a * norm_b)


def main(argv):
    words_path = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_WORDS
    relations_path = Path(argv[2]).resolve() if len(argv) > 2 else DEFAULT_EXISTING_RELATIONS
    out_dir = Path(argv[3]).resolve() if len(argv) > 3 else DEFAULT_OUT_DIR

    words = load_jsonl(words_path)
    existing_relations = load_jsonl(relations_path)
    existing_pairs = {
        tuple(sorted([rel.get("fromWordId"), rel.get("toWordId")]))
        for rel in existing_relations
        if rel.get("fromWordId") and rel.get("toWordId")
    }

    candidates_source = []
    for word in words:
        if not word.get("ecdict"):
            continue
        sense = word.get("senses", [{}])[0] if word.get("senses") else {}
        if not sense.get("definitionEn") and not sense.get("definitionZh"):
            continue
        candidates_source.append(word)

    vectors, norms = vectorize(candidates_source)
    rows = []
    for i, left in enumerate(candidates_source):
        left_id = left["_id"]
        scored = []
        for j, right in enumerate(candidates_source):
            if i >= j:
                continue
            right_id = right["_id"]
            pair = tuple(sorted([left_id, right_id]))
            if pair in existing_pairs:
                continue
            # Avoid pairing words with wildly different broad POS when available.
            left_pos = first_pos(left)
            right_pos = first_pos(right)
            if left_pos and right_pos and broad_pos(left_pos) != broad_pos(right_pos):
                continue
            score = cosine(vectors[i], norms[i], vectors[j], norms[j])
            if score >= 0.34:
                scored.append((score, right))
        for score, right in sorted(scored, reverse=True, key=lambda item: item[0])[:4]:
            rows.append({
                "fromWordId": left_id,
                "fromWord": left["word"],
                "toWordId": right["_id"],
                "toWord": right["word"],
                "score": round(score, 4),
                "fromTranslation": first_translation(left),
                "toTranslation": first_translation(right),
                "fromDefinitionEn": first_definition(left),
                "toDefinitionEn": first_definition(right),
                "reviewDecision": ""
            })

    rows.sort(key=lambda item: item["score"], reverse=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "relation_candidates.preview.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    with (out_dir / "relation_candidates.preview.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()) if rows else ["fromWord"])
        writer.writeheader()
        writer.writerows(rows)
    report = {
        "words": len(words),
        "candidateSourceWords": len(candidates_source),
        "existingRelations": len(existing_relations),
        "candidates": len(rows),
        "threshold": 0.34,
        "outputDir": str(out_dir)
    }
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def first_pos(word):
    senses = word.get("senses") or []
    return str((senses[0] if senses else {}).get("pos") or "")


def broad_pos(pos):
    value = pos.lower()
    if "n" in value:
        return "n"
    if "v" in value:
        return "v"
    if "a" in value or "adj" in value:
        return "adj"
    if "adv" in value:
        return "adv"
    return value


def first_translation(word):
    senses = word.get("senses") or []
    return str((senses[0] if senses else {}).get("translation") or "")[:160]


def first_definition(word):
    senses = word.get("senses") or []
    return str((senses[0] if senses else {}).get("definitionEn") or "").split("\\n")[0][:220]


if __name__ == "__main__":
    main(sys.argv)
