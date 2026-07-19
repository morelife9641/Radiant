#!/usr/bin/env python3
"""Apply user-marked IELTS relation enrichment requests as draft suggestions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
DEFAULT_MARKS_PATH = Path("/Users/chengtingwei/Downloads/ielts_relation_enrichment_marks.json")
SUGGESTIONS_PATH = DATA_DIR / "word_lexical_suggestions.json"
REPORT_PATH = DATA_DIR / "marked_relation_enrichment_report.json"


CURATED_SYNONYMS: dict[str, list[str]] = {
    "install": ["set up", "put in place", "fit", "establish"],
    "adopt": ["take up", "embrace", "approve", "accept"],
    "accredit": ["authorize", "certify", "recognize", "attribute"],
    "culminate": ["end in", "result in", "peak", "climax"],
    "meantime": ["meanwhile", "in the interim", "at the same time"],
    "in addition": ["moreover", "furthermore", "besides", "also"],
    "orbit": ["revolve around", "circle", "trajectory", "path"],
    "attraction": ["appeal", "draw", "allure", "magnetism"],
    "proposal": ["suggestion", "plan", "recommendation", "proposition"],
    "heritage": ["legacy", "inheritance", "tradition", "patrimony"],
    "scour": ["search", "rummage through", "scrub", "cleanse"],
    "allure": ["appeal", "attraction", "charm", "temptation"],
    "mission": ["task", "assignment", "purpose", "objective"],
    "conservation": ["preservation", "protection", "safeguarding"],
    "endanger": ["threaten", "jeopardize", "imperil", "put at risk"],
    "virtually": ["almost", "nearly", "practically", "effectively"],
    "destruction": ["devastation", "demolition", "ruin", "damage"],
    "diversity": ["variety", "range", "variation", "heterogeneity"],
    "recipe": ["formula", "method", "procedure", "instructions"],
    "existence": ["being", "presence", "survival", "life"],
    "mention": ["refer to", "cite", "name", "bring up"],
    "orthodox": ["conventional", "traditional", "established", "mainstream"],
    "deploy": ["use", "employ", "apply", "position"],
    "integrate": ["combine", "merge", "incorporate", "unify"],
    "impulse": ["urge", "drive", "instinct", "stimulus"],
    "generate": ["produce", "create", "cause", "give rise to"],
    "trigger": ["cause", "prompt", "spark", "set off"],
    "generic": ["general", "common", "standard", "non-specific"],
    "conclusion": ["finding", "inference", "judgement", "ending"],
    "formal": ["official", "ceremonial", "structured", "proper"],
    "favourite": ["preferred", "favoured", "best-liked"],
    "invade": ["enter", "intrude into", "attack", "occupy"],
    "crash": ["collide", "smash", "plunge", "collapse"],
    "dominate": ["control", "govern", "prevail over", "overshadow"],
    "indigenous": ["native", "local", "aboriginal", "home-grown"],
    "susceptible": ["vulnerable", "prone", "sensitive", "liable"],
    "cope": ["manage", "handle", "deal with", "adapt"],
    "hybrid": ["mixed", "crossbred", "composite", "combined"],
    "promising": ["hopeful", "encouraging", "prospective", "favourable"],
    "extremely": ["very", "highly", "exceptionally", "exceedingly"],
    "spectrum": ["range", "scale", "continuum", "band"],
    "encase": ["enclose", "cover", "wrap", "surround"],
    "grim": ["bleak", "severe", "harsh", "gloomy"],
    "regarding": ["concerning", "about", "with respect to", "in relation to"],
    "in addition to": ["besides", "as well as", "apart from", "along with"],
    "resort": ["turn to", "fall back on", "destination", "retreat"],
    "occupy": ["take up", "inhabit", "hold", "engage"],
    "subsequent": ["later", "following", "ensuing", "successive"],
    "excess": ["surplus", "extra", "overabundance", "overflow"],
    "stance": ["position", "attitude", "viewpoint", "posture"],
    "pursuit": ["quest", "search", "aim", "activity"],
    "at random": ["randomly", "arbitrarily", "haphazardly", "by chance"],
    "relax": ["loosen", "ease", "unwind", "calm down"],
    "contrast": ["comparison", "difference", "distinction", "juxtaposition"],
    "prolonged": ["extended", "lengthy", "long-lasting", "sustained"],
    "visual": ["visible", "optical", "pictorial", "graphic"],
    "stimulus": ["trigger", "prompt", "incentive", "impetus"],
    "activate": ["trigger", "stimulate", "switch on", "set in motion"],
    "significance": ["importance", "meaning", "value", "implication"],
    "content": ["material", "substance", "information", "satisfied"],
    "inclination": ["tendency", "preference", "leaning", "disposition"],
    "solve": ["resolve", "work out", "settle", "answer"],
    "disrupt": ["disturb", "interrupt", "distort", "upset"],
    "prevalence": ["frequency", "commonness", "widespread occurrence"],
    "intrigue": ["fascinate", "interest", "scheme", "plot"],
    "identity": ["selfhood", "character", "individuality", "recognition"],
    "sculpture": ["statue", "carving", "model", "three-dimensional artwork"],
    "utterance": ["statement", "remark", "expression", "speech"],
    "equation": ["formula", "equality", "calculation", "balance"],
    "emulate": ["imitate", "copy", "rival", "match"],
    "imitate": ["copy", "mimic", "emulate", "simulate"],
    "perceive": ["notice", "detect", "recognize", "interpret"],
    "recognition": ["identification", "acknowledgement", "approval", "awareness"],
    "respond": ["reply", "react", "answer", "act in response"],
    "extend": ["expand", "prolong", "stretch", "broaden"],
    "declare": ["announce", "state", "proclaim", "assert"],
    "frequent": ["common", "regular", "repeated", "recurring"],
    "intensity": ["strength", "force", "severity", "degree"],
    "incredible": ["unbelievable", "extraordinary", "remarkable", "astonishing"],
    "insufficient": ["inadequate", "deficient", "not enough", "scarce"],
    "commitment": ["dedication", "pledge", "obligation", "responsibility"],
    "eject": ["expel", "throw out", "emit", "discharge"],
    "prepare": ["get ready", "arrange", "organize", "make ready"],
    "variability": ["variation", "fluctuation", "changeability", "diversity"],
    "formula": ["equation", "method", "recipe", "rule"],
    "reliable": ["dependable", "trustworthy", "credible", "consistent"],
    "departure": ["leaving", "exit", "deviation", "change"],
    "dramatic": ["striking", "sudden", "marked", "theatrical"],
    "intense": ["strong", "severe", "extreme", "concentrated"],
    "collate": ["collect", "compile", "arrange", "compare"],
    "exploitation": ["use", "utilization", "abuse", "taking advantage"],
    "cooperative": ["collaborative", "joint", "helpful", "collective"],
    "briefly": ["shortly", "in short", "for a moment", "concisely"],
    "clue": ["hint", "sign", "indication", "evidence"],
    "primitive": ["early", "basic", "simple", "rudimentary"],
    "overall": ["general", "total", "entire", "broad"],
    "constantly": ["continually", "repeatedly", "persistently", "all the time"],
    "simultaneously": ["at the same time", "concurrently", "together"],
    "dearth": ["shortage", "lack", "scarcity", "paucity"],
    "multiple": ["many", "several", "numerous", "various"],
    "coordinate": ["organize", "align", "synchronize", "manage"],
    "discretion": ["judgement", "choice", "caution", "prudence"],
    "background": ["context", "setting", "history", "basis"],
    "relevant": ["pertinent", "related", "applicable", "connected"],
    "ingenuity": ["inventiveness", "creativity", "resourcefulness", "cleverness"],
    "erode": ["wear away", "diminish", "undermine", "corrode"],
    "stark": ["sharp", "plain", "severe", "bleak"],
    "synthesis": ["combination", "integration", "fusion", "amalgamation"],
    "offset": ["counterbalance", "compensate for", "balance", "neutralize"],
    "exclusive": ["restricted", "sole", "private", "selective"],
    "imitation": ["copy", "mimicry", "replica", "emulation"],
    "transplant": ["relocate", "transfer", "graft", "move"],
    "substantial": ["considerable", "significant", "large", "solid"],
    "visible": ["observable", "noticeable", "apparent", "clear"],
    "homogeneous": ["uniform", "consistent", "similar", "alike"],
    "strand": ["thread", "fiber", "element", "shore"],
    "spill": ["overflow", "pour out", "leak", "scatter"],
    "spectacular": ["striking", "impressive", "dramatic", "remarkable"],
    "insert": ["put in", "place", "embed", "introduce"],
    "champion": ["support", "advocate", "defend", "winner"],
    "launch": ["start", "initiate", "introduce", "set in motion"],
    "erosion": ["wearing away", "degradation", "deterioration", "attrition"],
    "reconstruction": ["rebuilding", "restoration", "re-creation", "renewal"],
    "unparalleled": ["unmatched", "unequalled", "unique", "unrivalled"],
    "suffice": ["be enough", "meet the need", "serve", "satisfy"],
    "redevelopment": ["renewal", "regeneration", "rebuilding", "renovation"],
    "extensive": ["wide-ranging", "large-scale", "broad", "widespread"],
    "albeit": ["although", "though", "even though"],
    "provision": ["supply", "providing", "arrangement", "measure"],
    "passionate": ["enthusiastic", "ardent", "fervent", "devoted"],
    "posture": ["position", "stance", "pose", "attitude"],
    "bouncing": ["springing", "rebounding", "lively", "buoyant"],
    "mime": ["gesture", "pantomime", "imitate silently", "act out"],
    "absolute": ["complete", "total", "unconditional", "definite"],
    "large-scale": ["extensive", "widespread", "broad", "massive"],
    "regularity": ["consistency", "uniformity", "pattern", "frequency"],
    "substitution": ["replacement", "exchange", "swap", "stand-in"],
    "variant": ["version", "form", "variation", "alternative"],
    "invoke": ["cite", "refer to", "call upon", "appeal to"],
    "assimilation": ["absorption", "integration", "incorporation", "adaptation"],
    "simplify": ["make simpler", "streamline", "clarify", "reduce complexity"],
    "initial": ["first", "early", "opening", "preliminary"],
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def relation_id(word: str, target: str) -> str:
    safe_word = word.replace(" ", "_").replace("-", "_").replace("/", "_").lower()
    safe_target = target.replace(" ", "_").replace("-", "_").replace("/", "_").lower()
    return f"lex_marked_{safe_word}_near_synonym_{safe_target}"


def phrase_note(word: str, target: str) -> str:
    return (
        f"用户在审核页标记 {word} 需要补充近义/同类表达；{target} 是高频候选。"
        "具体是否完全等价需按词性和文章语境复核。"
    )


def build_example(word: str, target: str) -> tuple[str, str]:
    return (
        f"In this context, {word} can be compared with {target}, but the exact choice depends on meaning and register.",
        f"在这个语境中，{word} 可以和 {target} 对照学习，但具体选择要看含义和语体。",
    )


def main() -> None:
    marks = json.loads(DEFAULT_MARKS_PATH.read_text(encoding="utf-8"))
    marked_words = {
        item["word"]
        for item in marks.get("items", [])
        if item.get("requestType") == "synonyms"
    }
    suggestions = read_jsonl(SUGGESTIONS_PATH)
    by_id = {row["_id"]: row for row in suggestions}
    wordbook = read_jsonl(DATA_DIR / "wordbook_words.json")
    word_ids = {row["word"]: row["wordId"] for row in wordbook}
    existing_targets = {
        (row.get("word"), row.get("relationType"), str(row.get("targetWord", "")).lower())
        for row in suggestions
    }

    added = 0
    skipped_existing = 0
    missing_curated: list[str] = []
    for word in sorted(marked_words):
        targets = CURATED_SYNONYMS.get(word)
        if not targets:
            missing_curated.append(word)
            continue
        if word not in word_ids:
            missing_curated.append(word)
            continue
        for target in targets:
            key = (word, "near_synonym", target.lower())
            if key in existing_targets:
                skipped_existing += 1
                continue
            rid = relation_id(word, target)
            if rid in by_id:
                skipped_existing += 1
                continue
            example_en, example_zh = build_example(word, target)
            row = {
                "_id": rid,
                "wordId": word_ids[word],
                "word": word,
                "targetWordId": word_ids.get(target),
                "targetWord": target,
                "targetInWordbook": target in word_ids,
                "targetInGlobalWords": False,
                "relationType": "near_synonym",
                "strength": 4,
                "explanationZh": phrase_note(word, target),
                "exampleEn": example_en,
                "exampleZh": example_zh,
                "source": "user_marked_ai_curated",
                "status": "draft",
                "reviewStatus": "ai_suggested_pending_human_review",
                "createdAt": None,
                "updatedAt": None,
            }
            by_id[rid] = row
            existing_targets.add(key)
            added += 1

    rows = sorted(by_id.values(), key=lambda item: (item["word"], item["relationType"], item["targetWord"]))
    write_jsonl(SUGGESTIONS_PATH, rows)
    report = {
        "marksPath": str(DEFAULT_MARKS_PATH),
        "markedSynonymWords": len(marked_words),
        "addedSuggestions": added,
        "skippedExisting": skipped_existing,
        "missingCurated": missing_curated,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
