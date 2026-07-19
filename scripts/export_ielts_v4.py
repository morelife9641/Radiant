r"""
Dry-run export for the IELTS wordbook using the v4 cloud data shape.

Inputs:
  - /Users/chengtingwei/Downloads/IELTS Word List.txt
  - ECDICT-master/ecdict.csv

Outputs:
  - tmp/cloud_import/words.json
  - tmp/cloud_import/wordbooks.json
  - tmp/cloud_import/wordbook_words.json
  - tmp/cloud_import/report.md

This script does not write to cloud databases.
"""

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IELTS_SRC = Path('/Users/chengtingwei/Downloads/IELTS Word List.txt')
DEFAULT_ECDICT_SRC = ROOT / 'ECDICT-master' / 'ecdict.csv'
OUT_DIR = ROOT / 'tmp' / 'cloud_import'

PHONETIC_RE = re.compile(r'(/[^\n/]+/|\[[^\n\]]+\]|\{[^\n}]+\})')
POS_RE = re.compile(r'^([a-zA-Z][a-zA-Z./-]*\.?)\s*')
ZH_RE = re.compile(r'[\u4e00-\u9fff]')


def normalize(value):
    return (value or '').strip().lower()


def word_id_for(normalized):
    slug = re.sub(r'[^a-z0-9]+', '_', normalized).strip('_')
    slug = re.sub(r'_+', '_', slug)
    if slug:
        return f'word_{slug}'
    digest = hashlib.md5(normalized.encode('utf-8')).hexdigest()[:12]
    return f'word_{digest}'


def clean_phonetic(value):
    if not value:
        return ''
    value = value.strip()
    if len(value) >= 2 and value[0] in '[{' and value[-1] in ']}':
        value = value[1:-1].strip()
    return value


def parse_translation(text):
    text = (text or '').strip()
    if not text:
        return '', ''

    match = POS_RE.match(text)
    if not match:
        return '', text

    pos = match.group(1).strip()
    if '.' not in pos and '/' not in pos:
        return '', text

    translation = text[match.end():].strip()
    return pos.rstrip('.'), translation


def parse_ielts_line(line):
    line = line.strip()
    if not line or line.startswith('Word List ') or line == 'README':
        return None
    if ZH_RE.search(line) is None:
        return None

    phonetic_match = PHONETIC_RE.search(line)
    if phonetic_match:
        raw_word = line[:phonetic_match.start()].strip()
        phonetic = clean_phonetic(phonetic_match.group(1))
        translation = line[phonetic_match.end():].strip()
    else:
        first_zh = ZH_RE.search(line)
        if not first_zh:
            return None
        raw_region = line[:first_zh.start()].strip()
        translation = line[first_zh.start():].strip()
        phonetic = ''
        malformed = re.match(r'^(.+?)\s+[\[{]([^\]}]+?)\s{2,}([a-zA-Z][a-zA-Z./-]*\.?)\s*$', raw_region)
        if malformed:
            raw_word = malformed.group(1).strip()
            phonetic = clean_phonetic(malformed.group(2).strip())
            translation = f'{malformed.group(3).strip()} {translation}'.strip()
        else:
            raw_word = raw_region

    important = raw_word.endswith('*')
    word = raw_word.rstrip('*').strip()
    if not word:
        return None

    pos, translation_text = parse_translation(translation)
    return {
        'word': word,
        'normalized': normalize(word),
        'phonetic': phonetic,
        'important': important,
        'senses': [{
            'pos': pos,
            'translation': translation_text or translation,
            'definitionEn': '',
            'definitionZh': '',
            'collinsEn': '',
            'collinsZh': '',
            'synonyms': [],
            'antonyms': [],
            'gamingLink': None
        }]
    }


def parse_ielts(src):
    items = []
    duplicates = []
    unparsed = []
    seen = {}
    started = False
    chapter = ''

    for line_no, line in enumerate(src.read_text(encoding='utf-8').splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('Word List '):
            started = True
            chapter = stripped
            continue
        if not started or not stripped:
            continue
        if ZH_RE.search(stripped) is None:
            continue

        item = parse_ielts_line(stripped)
        if not item:
            unparsed.append({'lineNo': line_no, 'text': stripped})
            continue

        key = item['normalized']
        item['lineNo'] = line_no
        item['chapter'] = chapter
        if key in seen:
            duplicates.append({
                'normalized': key,
                'firstLineNo': seen[key]['lineNo'],
                'duplicateLineNo': line_no,
                'word': item['word']
            })
            continue
        seen[key] = item
        items.append(item)

    return items, duplicates, unparsed


def parse_ecdict_translation(text):
    text = (text or '').strip()
    if not text:
        return []
    text = text.replace('\\n', '\n')
    senses = []
    for part in re.split(r'[\n;]+', text):
        part = part.strip()
        if not part:
            continue
        pos, translation = parse_translation(part)
        senses.append({
            'pos': pos,
            'translation': translation or part,
            'definitionEn': '',
            'definitionZh': '',
            'collinsEn': '',
            'collinsZh': '',
            'synonyms': [],
            'antonyms': [],
            'gamingLink': None
        })
    return senses


def load_ecdict_matches(src, wanted_normalized):
    matches = {}
    if not src.exists():
        return matches

    with src.open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            word = (row.get('word') or '').strip()
            key = normalize(word)
            if key not in wanted_normalized or key in matches:
                continue
            matches[key] = {
                'word': word,
                'phonetic': clean_phonetic(row.get('phonetic') or ''),
                'senses': parse_ecdict_translation(row.get('translation') or ''),
                'exchange': row.get('exchange') or '',
                'bnc': int(row.get('bnc') or 0),
                'frq': int(row.get('frq') or 0),
                'tag': row.get('tag') or ''
            }
    return matches


def build_words(ielts_items, ecdict_matches):
    words = []
    wordbook_words = []
    phrase_count = 0
    important_count = 0

    for order, item in enumerate(ielts_items, 1):
        normalized = item['normalized']
        wid = word_id_for(normalized)
        ecdict = ecdict_matches.get(normalized)
        phonetic = item['phonetic'] or (ecdict or {}).get('phonetic', '')
        senses = item['senses']
        if not senses or not senses[0].get('translation'):
            senses = (ecdict or {}).get('senses') or senses

        is_phrase = bool(re.search(r'\s', normalized))
        phrase_count += 1 if is_phrase else 0
        important_count += 1 if item['important'] else 0

        words.append({
            '_id': wid,
            'word': item['word'],
            'normalized': normalized,
            'type': 'phrase' if is_phrase else 'word',
            'phonetic': {
                'uk': '',
                'us': '',
                'default': phonetic
            },
            'audio': {
                'us': '',
                'uk': ''
            },
            'audioPolicy': None,
            'senses': senses,
            'contextStats': {
                'totalLines': 0,
                'byTopic': {}
            },
            'createdAt': None,
            'updatedAt': None
        })

        wordbook_words.append({
            '_id': f'ielts:{wid}',
            'bookId': 'ielts',
            'wordId': wid,
            'word': item['word'],
            'normalized': normalized,
            'order': order,
            'chapter': item['chapter'],
            'important': item['important'],
            'bookSenseOverride': None,
            'createdAt': None,
            'updatedAt': None
        })

    return words, wordbook_words, {
        'phraseCount': phrase_count,
        'importantCount': important_count
    }


def build_wordbook(total_words):
    return [{
        '_id': 'ielts',
        'name': '雅思核心词',
        'category': 'exam',
        'cefrLevel': 'B2',
        'totalWords': total_words,
        'description': '雅思核心词汇',
        'cover': {
            'letter': 'I',
            'color': '#1A1A1A'
        },
        'status': 'published',
        'schemaVersion': 1,
        'contentVersion': 1,
        'source': {
            'name': 'IELTS Word List.txt',
            'importedAt': None
        },
        'createdAt': None,
        'updatedAt': None
    }]


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def default_audio_url(normalized):
    from urllib.parse import quote
    return 'https://ielts-word-audio-1411800061.cos.ap-guangzhou.myqcloud.com/audio/' + quote(normalized) + '.mp3'


def build_report(stats):
    missing_preview = stats['ecdictMissing'][:50]
    duplicates_preview = stats['duplicates'][:20]
    unparsed_preview = stats['unparsed'][:20]
    chapter_lines = [
        f'- {chapter}: {count}'
        for chapter, count in sorted(stats['chapterCounts'].items())
    ]

    return '\n'.join([
        '# IELTS v4 Dry-run Report',
        '',
        '## Summary',
        '',
        f"- IELTS parsed unique entries: {stats['ieltsUniqueCount']}",
        f"- IELTS duplicate entries skipped: {len(stats['duplicates'])}",
        f"- Unparsed lines: {len(stats['unparsed'])}",
        f"- Output words: {stats['wordsCount']}",
        f"- Output wordbook_words: {stats['wordbookWordsCount']}",
        f"- Important words: {stats['importantCount']}",
        f"- Phrase entries: {stats['phraseCount']}",
        f"- ECDICT matches: {stats['ecdictMatchCount']}",
        f"- ECDICT missing: {len(stats['ecdictMissing'])}",
        f"- ECDICT coverage: {stats['ecdictCoverage']:.2%}",
        '',
        '## Chapter Counts',
        '',
        *chapter_lines,
        '',
        '## Default Audio URL Samples',
        '',
        *[f"- {item['word']}: {default_audio_url(item['normalized'])}" for item in stats['audioSamples']],
        '',
        '## ECDICT Missing Preview',
        '',
        *[f"- {word}" for word in missing_preview],
        '',
        '## Duplicate Preview',
        '',
        *[f"- {d['word']} ({d['normalized']}): first line {d['firstLineNo']}, duplicate line {d['duplicateLineNo']}" for d in duplicates_preview],
        '',
        '## Unparsed Preview',
        '',
        *[f"- line {u['lineNo']}: {u['text']}" for u in unparsed_preview],
        ''
    ])


def main():
    ielts_src = DEFAULT_IELTS_SRC
    ecdict_src = DEFAULT_ECDICT_SRC
    if not ielts_src.exists():
        raise SystemExit(f'IELTS source not found: {ielts_src}')
    if not ecdict_src.exists():
        raise SystemExit(f'ECDICT source not found: {ecdict_src}')

    ielts_items, duplicates, unparsed = parse_ielts(ielts_src)
    wanted = {item['normalized'] for item in ielts_items}
    ecdict_matches = load_ecdict_matches(ecdict_src, wanted)
    words, wordbook_words, derived = build_words(ielts_items, ecdict_matches)
    wordbooks = build_wordbook(len(wordbook_words))

    chapter_counts = Counter(item['chapter'] for item in ielts_items)
    ecdict_missing = sorted(wanted - set(ecdict_matches.keys()))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / 'words.json', words)
    write_json(OUT_DIR / 'wordbooks.json', wordbooks)
    write_json(OUT_DIR / 'wordbook_words.json', wordbook_words)

    stats = {
        'ieltsUniqueCount': len(ielts_items),
        'duplicates': duplicates,
        'unparsed': unparsed,
        'wordsCount': len(words),
        'wordbookWordsCount': len(wordbook_words),
        'importantCount': derived['importantCount'],
        'phraseCount': derived['phraseCount'],
        'ecdictMatchCount': len(ecdict_matches),
        'ecdictMissing': ecdict_missing,
        'ecdictCoverage': len(ecdict_matches) / len(wanted) if wanted else 0,
        'chapterCounts': dict(chapter_counts),
        'audioSamples': [
            item for item in ielts_items[:5]
        ]
    }
    (OUT_DIR / 'report.md').write_text(build_report(stats), encoding='utf-8')
    write_json(OUT_DIR / 'report.json', stats)

    print(f'wrote {OUT_DIR / "words.json"} ({len(words)} records)')
    print(f'wrote {OUT_DIR / "wordbooks.json"} ({len(wordbooks)} records)')
    print(f'wrote {OUT_DIR / "wordbook_words.json"} ({len(wordbook_words)} records)')
    print(f'wrote {OUT_DIR / "report.md"}')


if __name__ == '__main__':
    main()
