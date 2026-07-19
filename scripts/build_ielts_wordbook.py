r"""
Build the IELTS wordbook from the plain text word list.

Usage:
    python3 scripts/build_ielts_wordbook.py /path/to/IELTS\ Word\ List.txt
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'miniprogram' / 'assets' / 'data' / 'wordbooks'

PHONETIC_RE = re.compile(r'(/[^\n/]+/|\[[^\n\]]+\]|\{[^\n}]+\})')
POS_RE = re.compile(r'^([a-zA-Z][a-zA-Z./-]*\.?)\s*')


def clean_phonetic(value):
    if not value:
        return ''
    value = value.strip()
    if value[0] in '[{' and value[-1] in ']}':
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


def parse_line(line):
    line = line.strip()
    if not line or line.startswith('Word List ') or line == 'README':
        return None
    if re.search(r'[\u4e00-\u9fff]', line) is None:
        return None

    phonetic_match = PHONETIC_RE.search(line)
    if phonetic_match:
        raw_word = line[:phonetic_match.start()].strip()
        phonetic = clean_phonetic(phonetic_match.group(1))
        translation = line[phonetic_match.end():].strip()
    else:
        first_zh = re.search(r'[\u4e00-\u9fff]', line)
        if not first_zh:
            return None
        raw_word = line[:first_zh.start()].strip()
        translation = line[first_zh.start():].strip()
        phonetic = ''

    important = raw_word.endswith('*')
    word = raw_word.rstrip('*').strip()
    if not word:
        return None

    pos, translation_text = parse_translation(translation)
    return {
        'word': word,
        'phonetic': phonetic,
        'senses': [{
            'pos': pos,
            'translation': translation_text or translation
        }],
        'tags': ['ielts'] + (['important'] if important else []),
        'important': important
    }


def build(src):
    words = []
    seen = set()
    started = False
    for line in src.read_text(encoding='utf-8').splitlines():
        if line.startswith('Word List '):
            started = True
            continue
        if not started:
            continue
        item = parse_line(line)
        if not item:
            continue
        key = item['word'].lower()
        if key in seen:
            continue
        seen.add(key)
        words.append(item)

    for index, item in enumerate(words, 1):
        item['_id'] = f'ielts-{index:04d}'
        item['order'] = index

    payload = {
        'wordbook': {
            'id': 'ielts',
            'name': '雅思核心词',
            'category': 'exam',
            'cefrLevel': 'B2',
            'totalWords': len(words),
            'source': src.name,
            'version': 1,
            'schema': 'senses-v1'
        },
        'words': words
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / 'ielts.json'
    js_path = OUT_DIR / 'ielts.js'
    payload_str = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    json_path.write_text(payload_str, encoding='utf-8')
    js_path.write_text(f'module.exports = {payload_str};\n', encoding='utf-8')
    print(f'wrote {len(words)} words -> {js_path}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)
    build(Path(sys.argv[1]))
