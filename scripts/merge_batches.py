"""合并 cet4_batch_*_ultimate.json 成单一 cet4.js（小程序可 require）。"""
import json
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / 'miniprogram' / 'assets' / 'data' / 'wordbooks'
OUT_DIR = SRC_DIR


def main():
    files = sorted(SRC_DIR.glob('cet4_batch_*_ultimate.json'),
                   key=lambda p: int(p.stem.split('_')[2]))
    if not files:
        print('no batch files found')
        return

    all_words = []
    seen = set()
    for f in files:
        items = json.loads(f.read_text(encoding='utf-8'))
        for w in items:
            key = w.get('word', '').strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            # 给每个词加 _id 和 order
            w['_id'] = f'cet4-{len(all_words)+1:04d}'
            w['order'] = len(all_words) + 1
            all_words.append(w)

    payload = {
        'wordbook': {
            'id': 'cet4',
            'name': '大学英语四级核心词',
            'category': 'exam',
            'cefrLevel': 'B1',
            'totalWords': len(all_words),
            'source': 'cet4_batch_*_ultimate.json',
            'version': 2,
            'schema': 'senses-v1'
        },
        'words': all_words
    }

    json_path = OUT_DIR / 'cet4.json'
    js_path = OUT_DIR / 'cet4.js'
    payload_str = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    json_path.write_text(payload_str, encoding='utf-8')
    js_path.write_text('module.exports = ' + payload_str + ';\n', encoding='utf-8')
    size_kb = js_path.stat().st_size / 1024
    print(f'merged {len(all_words)} words from {len(files)} files -> {js_path} ({size_kb:.1f} KB)')


if __name__ == '__main__':
    main()
