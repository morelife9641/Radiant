"""Convert a JSON array file to JSONL, one object per line."""

import json
import sys
from pathlib import Path


def convert(src, dst):
    data = json.loads(src.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError(f'{src} must contain a JSON array')
    with dst.open('w', encoding='utf-8') as handle:
        for item in data:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(',', ':')))
            handle.write('\n')
    print(f'wrote {len(data)} lines -> {dst}')


def main():
    if len(sys.argv) != 3:
        raise SystemExit('Usage: python3 scripts/json_to_jsonl.py input.json output.jsonl')
    convert(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == '__main__':
    main()
