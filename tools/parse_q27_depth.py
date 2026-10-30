"""Parse the six Gazette issues specified in the depth batch; no network."""
import json
import os
import sys
from pathlib import Path

import parts

HERE = Path(__file__).resolve().parent
BATCH = (
    'e1-q27-pr-954-2016', 'e1-q27-pr-690-2010', 'e1-q27-pr-681-2010',
    'e1-q27-pr-668-2010', 'e1-q27-pr-1376-2025', 'e1-q27-pr-1344-2024',
)


def parse(part):
    if part not in BATCH:
        raise ValueError('Part outside this batch')
    if (HERE / 'corpus.d' / (part + '.PUBLISH')).exists():
        raise RuntimeError('Published part is immutable')
    corpus = parts.build(part)
    act = corpus['acts'][0]
    act['first_law'] = None
    act['earlier_laws'] = [parts.SPECS[part]['law']]
    act['versions'][0]['note'] = (
        'Oldest version available: the Gazette text as published; later amendments are not represented.'
    )
    corpus['ai_use'] = [
        'GPT-6 configured source-derived article boundaries and date metadata; all legal wording is '
        'extracted by code from the Gazette PDF text layer.'
    ]
    path = HERE / 'corpus.d' / (part + '.json')
    temp = path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(corpus, ensure_ascii=False, indent=1) + '\n', encoding='utf8', newline='\n')
    os.replace(temp, path)
    print(part, len(act['versions'][0]['units']), 'units')


if __name__ == '__main__':
    for part in sys.argv[1:] or BATCH:
        parse(part)
