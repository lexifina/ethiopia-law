"""Write corpus.d/<part>.PUBLISH for verified parts: runs verify_parts.check and refuses unless it is clean.
Usage: python -X utf8 publish_line.py <part> [...]   (only after a clean scratch build, check.py and --compare)"""
import os
import sys
from pathlib import Path

import parts
import verify_parts as vp

for part in sys.argv[1:]:
    r = vp.check(part)
    if r['problems']:
        sys.exit(f'{part}: not clean: {r["problems"]}')
    s = parts.SPECS[part]
    line = (f"{s['title']}: every word of the English column of the {s['gazette']} is in the units "
            f"({r['pdf_words']:,} words; independent PyMuPDF span check, Amharic spans, invisible <3pt glyphs and "
            f"running heads ignored); Articles 1-{r['articles']} contiguous; in force {s['from']} ({s['in_force']}). "
            "Scratch build 0/0, --compare identical, audit clean.")
    p = Path(__file__).resolve().parent / 'corpus.d' / f'{part}.PUBLISH'
    tmp = p.with_suffix('.tmp')
    tmp.write_text(line + '\n', encoding='utf-8', newline='\n')
    os.replace(tmp, p)
    print(part, 'PUBLISH')
