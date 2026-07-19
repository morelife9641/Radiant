"""
将 ECDICT 的 ecdict.csv 按 tag 提取并转换为 Radiant.AI 词书 JSON。

用法：
    python3 scripts/build_wordbook.py cet4
    python3 scripts/build_wordbook.py cet6
    python3 scripts/build_wordbook.py ielts toefl ky  # 多 tag 并集

输出到 miniprogram/assets/data/wordbooks/<tag>.json
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'ECDICT-master' / 'ecdict.csv'
OUT_DIR = ROOT / 'miniprogram' / 'assets' / 'data' / 'wordbooks'

# ECDICT tag → 词书元数据
TAG_META = {
    'cet4':  {'name': '大学英语四级核心词', 'category': 'exam', 'cefrLevel': 'B1'},
    'cet6':  {'name': '大学英语六级核心词', 'category': 'exam', 'cefrLevel': 'B2'},
    'ielts': {'name': '雅思核心词',         'category': 'exam', 'cefrLevel': 'B2'},
    'toefl': {'name': '托福核心词',         'category': 'exam', 'cefrLevel': 'C1'},
    'gre':   {'name': 'GRE 核心词',          'category': 'exam', 'cefrLevel': 'C1'},
    'ky':    {'name': '考研英语核心词',     'category': 'exam', 'cefrLevel': 'B2'},
    'gk':    {'name': '高中英语核心词',     'category': 'exam', 'cefrLevel': 'A2'},
}

POS_RE = re.compile(r'^\s*([a-zA-Z\.&/]+)\s*[\.。]\s*')

# Kingsoft / ECDICT 用的非标准音标符号 → 标准 IPA
PHONETIC_MAP = str.maketrans({
    'ә': 'ə',   # 0x4d9 → 标准 schwa
    "'": 'ˈ',   # 主重音符号
    ',': 'ˌ',   # 次重音符号
})


def normalize_phonetic(s: str) -> str:
    if not s:
        return ''
    return s.strip().translate(PHONETIC_MAP)


def parse_translation(text: str):
    """把 'n. 塑料\\nadj. 可塑的' 拆成 [{pos, text}]
    注意 ECDICT csv 里换行是字面量 \\n，不是真换行。"""
    if not text:
        return []
    # 同时处理字面量 \n 和真实换行
    text = text.replace('\\n', '\n')
    items = []
    for line in re.split(r'[\n;]+', text):
        line = line.strip()
        if not line:
            continue
        m = POS_RE.match(line)
        if m:
            pos = m.group(1).strip().rstrip('.')
            rest = line[m.end():].strip()
            items.append({'pos': pos, 'text': rest})
        else:
            items.append({'pos': '', 'text': line})
    return items


def parse_exchange(text: str):
    """把 'd:accustomed/p:accustomed/3:accustoms/i:accustoming' 拆成 dict"""
    if not text:
        return {}
    KEY = {
        'p': 'past', 'd': 'pastParticiple', 'i': 'presentParticiple',
        '3': 'thirdPerson', 'r': 'comparative', 't': 'superlative',
        's': 'plural', '0': 'lemma', '1': 'lemmaType'
    }
    out = {}
    for part in text.split('/'):
        if ':' in part:
            k, v = part.split(':', 1)
            out[KEY.get(k, k)] = v
    return out


def syllabify_fallback(word: str):
    """没有外部依赖时的简单兜底：返回整词作为单音节"""
    return [word]


def try_syllabify(word: str):
    try:
        import pyphen
        dic = pyphen.Pyphen(lang='en_US')
        s = dic.inserted(word)
        parts = [p for p in s.split('-') if p]
        return parts if parts else [word]
    except ImportError:
        return syllabify_fallback(word)


def build(tags):
    if not SRC.exists():
        print(f'csv not found: {SRC}', file=sys.stderr)
        sys.exit(1)
    tag_set = set(tags)
    out_words = []
    with SRC.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            row_tags = set((row.get('tag') or '').split())
            if not (tag_set & row_tags):
                continue
            word = row['word'].strip()
            if not word:
                continue
            out_words.append({
                'word': word,
                'syllables': try_syllabify(word),
                'phonetic': normalize_phonetic(row.get('phonetic') or ''),
                'translations': parse_translation(row.get('translation') or ''),
                'exchange': parse_exchange(row.get('exchange') or ''),
                'tags': sorted(row_tags),
                'bnc': int(row.get('bnc') or 0),
            })

    # 按 BNC 排序（越常用越靠前），0 视为很冷
    out_words.sort(key=lambda w: (w['bnc'] == 0, w['bnc']))

    # 重新写 order / _id
    for i, w in enumerate(out_words, 1):
        w['_id'] = f'{tags[0]}-{i:04d}'
        w['order'] = i

    book_id = '_'.join(tags)
    meta = TAG_META.get(tags[0], {'name': book_id, 'category': 'exam', 'cefrLevel': 'B1'})
    payload = {
        'wordbook': {
            'id': book_id,
            'name': meta['name'],
            'category': meta['category'],
            'cefrLevel': meta['cefrLevel'],
            'totalWords': len(out_words),
            'source': 'ECDICT tags=' + ','.join(tags),
            'version': 1
        },
        'words': out_words
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # 同时输出 .json（供人阅读 / 后续上云）和 .js（供小程序 require）
    json_path = OUT_DIR / f'{book_id}.json'
    js_path = OUT_DIR / f'{book_id}.js'
    payload_str = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    with json_path.open('w', encoding='utf-8') as f:
        f.write(payload_str)
    with js_path.open('w', encoding='utf-8') as f:
        f.write('module.exports = ')
        f.write(payload_str)
        f.write(';\n')
    size_kb = js_path.stat().st_size / 1024
    print(f'wrote {len(out_words)} words -> {js_path} ({size_kb:.1f} KB)')


if __name__ == '__main__':
    args = sys.argv[1:] or ['cet4']
    build(args)
