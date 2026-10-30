"""Draft a parts.py spec for a bilingual Federal Negarit Gazette issue (English right column), from the cache only.

Usage: python -X utf8 autospec.py <part> <pdf url> <slug> "<title>" [more ...]  (groups of four)
Writes specs_auto.json (merged into parts.SPECS). A draft is written only when the checks hold: one start line,
article numbers 1..N with the last article on commencement, and the in-force date read from the text agreeing with
the issue's own dates. Anything else is printed as a problem and left out for a manual spec.
"""
import json
import re
import statistics
import sys
from datetime import date
from pathlib import Path

import pymupdf

import gazette as gz

HERE = Path(__file__).resolve().parent
OUT = HERE / 'specs_auto.json'
FIXES = {  # [page, printed number, article]: headings misprinted in the Gazette, recorded in decisions
    '71-government-owned-enterprises': [[46, 32, 33]],
    '77-expropriation': [[23, 25, 24]],
    '9b-general-education': [[37, 35, 34]],
}
MONTHS = {m: i for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                      'september', 'october', 'november', 'december'], 1)}
HEAD = r'^(\d+)(?:\s*\.\s*|\s+)([A-Za-z]\S*.*)$'
HEAD_SLASH = r'^(\d+)(?:\s*[./]\s*|\s+)([A-Za-z]\S*.*)$'  # '1/ Short Title' (bold), in issues that number articles so


DONE = r'^(?:Done|DONE)\s+(?:[Aa][Tt]|[Ii][Nn])\s+(?:Addis|ADDIS)\s+(?:Ab[ae]ba|AB[AE]BA)'  # not the lowercase 'done in Addis Ababa;' of a preamble
MON = r'(january|february|march|april|may|june|july|august|september|semptember|sept|october|november|december|feburary)'


def eng_date(t: str):
    """'5th September, 2019', 'the 23th Day of March, 2020', 'March 23th, 2020', '23 rd, September, 2019'."""
    t = t.lower()
    m = re.search(r'(\d{1,2})\s*(?:st|nd|rd|th)?\s*,?\s*(?:day\s+of\s+)?' + MON + r'\s*,?\s*(\d{4})', t)
    if m:
        d, mon, y = int(m.group(1)), m.group(2), int(m.group(3))
    else:
        m = re.search(MON + r'\s+(\d{1,2})\s*(?:st|nd|rd|th)?\s*(?:day\s+of\s+' + MON + r')?\s*,?\s*(\d{4})', t)
        if not m:
            return None
        mon, d, y = m.group(1), int(m.group(2)), int(m.group(4))
    mon = {'semptember': 'september', 'sept': 'september', 'feburary': 'february'}.get(mon, mon)
    return date(y, MONTHS[mon], d)


def gutter(doc) -> float:
    """Left edge of the English column, a little left of its leftmost text: the 2nd-percentile x of spans that hold
    an English word (three or more Latin letters, not Amharic) right of the page's middle third."""
    xs = sorted(sp['bbox'][0] for p in list(doc)[1:8] for b in p.get_text('dict')['blocks']
                for l in b.get('lines', []) for sp in l['spans']
                if sp['bbox'][0] > p.rect.width * 0.4 and re.search(r'[A-Za-z]{3}', sp['text'])
                and not gz.is_amharic(sp, 0))
    return min(300.0, round(xs[int(len(xs) * 0.02)] - 3)) if xs else 300.0  # never right of x 300


def draft(part: str, url: str, slug: str, title: str):
    doc = pymupdf.open(gz.cached(url))
    h = doc[1].rect.height if doc.page_count > 1 else doc[0].rect.height
    bottom = round(h * 0.915)
    xg = gutter(doc)
    heads = [l['bbox'][3] for pg in list(doc)[1:] for b in pg.get_text('dict')['blocks'] for l in b.get('lines', [])
             if l['bbox'][1] < 160 and gz.FURNITURE.search(gz.norm(''.join(x['text'] for x in l['spans'])))]
    top = max(45, round(max(heads)) + 1) if heads else 45  # below the running heads, wherever the page puts them
    base = {'url': url, 'pages': (0, doc.page_count - 1), 'x': (xg, 700), 'band': (top, bottom)}
    ls = gz.lines(base)
    problems = []
    pat = r'^(A\s+)?PROCLAMATION\s+(?:N[Oo0]\s*\.?|NUMBER|Number)?\s*\d+\s*/\s*\d{4}'
    starts = [i for i, ln in enumerate(ls) if ln['b'] and re.match(pat, ln['t'])]
    if not starts:  # not bold: the last all-capital PROCLAMATION No. line on its page (the first is the contents)
        caps = [i for i, ln in enumerate(ls) if re.match(pat, ln['t'])] or             [i for i, ln in enumerate(ls) if re.match(pat, ln['t'], re.I) and ln['p'] == 0]
        starts = [i for i in caps if ls[i]['p'] == ls[caps[0]]['p']][-1:] if caps else []
    if not starts:
        return None, ['no PROCLAMATION No. line']
    i0 = [i for i in starts if ls[i]['p'] == ls[starts[0]]['p']][-1]  # the contents box comes first
    n_title = 1
    while i0 + n_title < len(ls) and ls[i0 + n_title]['b'] and ls[i0 + n_title]['p'] == ls[i0]['p']:
        n_title += 1
    gaps = [b['y'] - a['y'] for a, b in zip(ls, ls[1:]) if a['p'] == b['p'] and 8 < b['y'] - a['y'] < 30]
    pitch = round(statistics.median(gaps) * 0.95, 1)
    body = ls[i0:]
    dn = [k for k, ln in enumerate(body) if re.match(DONE, ln['t'])]
    if len(dn) != 1:
        problems.append(f'{len(dn)} "Done at" lines')
        return None, problems
    head = HEAD
    fix = {(p, n): a for p, n, a in FIXES.get(part, [])}
    pre, arts = gz.split_articles(body[:dn[0]], re.compile(head), fix=fix)
    hb = True
    if arts and not re.search(r'(?i)effective|entry into force|commencement|come into force', arts[-1][1]):
        for h, b in ((HEAD, False), (HEAD_SLASH, True), (HEAD_SLASH, False)):  # non-bold headings, '75/ Title'
            p2, a2 = gz.split_articles(body[:dn[0]], re.compile(h), fix=fix, bold=b)
            if len(a2) > len(arts):
                pre, arts, head, hb = p2, a2, h, b
    if not arts:
        head = HEAD_SLASH
        pre, arts = gz.split_articles(body[:dn[0]], re.compile(head), fix=fix)
    n = len(arts)
    if not n or not re.search(r'(?i)effective|entry into force|coming into force|commencement|come into force', arts[-1][1]):
        problems.append(f'last article {n}: {arts[-1][1] if arts else None}')
    later = [ln['t'] for ln in body[:dn[0]] if ln['b'] and re.match(rf'^{n + 1}\s*\.', ln['t'])]
    if later:
        problems.append(f'a bold heading for article {n + 1} exists after the run stops: {later[:2]}')
    eff = ' '.join(ln['t'] for ln in arts[-1][2]) if arts else ''
    # the issue's dates: cover, running heads, signature
    cover = [eng_date(ln['t']) for ln in gz.lines(dict(base, pages=(0, 0), band=(0, 10000)))
             if re.search(r'ADDIS ABABA', ln['t'])]
    heads = set()
    for pn in range(1, doc.page_count):
        for w in doc[pn].get_text('blocks'):
            if w[1] < 45 and 'Gazette' in w[4]:
                d = eng_date(w[4].replace('\n', ' '))
                if d:
                    heads.add(d)
    done = eng_date(' '.join(ln['t'] for ln in body[dn[0]:dn[0] + 3]))
    pubs = {d for d in cover if d} | heads
    named = ''
    if (re.search(r'(?i)publication', eff) and not re.search(r'(?i)after|approv|ratif|adopt|\d{4}', eff)) or re.search(r'(?i)(upon|up on|on|from|as of)\s+(the\s+date\s+of\s+)?(its\s+)?publication|date of (its )?publication|(day|date) (it is|of its) published', eff):
        if len(pubs) == 1 and (done is None or done in pubs):
            frm = min(pubs).isoformat()
        else:
            problems.append(f'issue dates disagree: cover {cover} heads {sorted(heads)} done {done}')
            frm = None
    elif re.search(r'(?i)\bone\s+year\s+after\s+(its|the\s+date\s+of\s+its)\s+publication', eff) and len(pubs) == 1:
        p0 = min(pubs)
        frm = date(p0.year + 1, p0.month, p0.day).isoformat()
        named = f' The issue is dated {p0.isoformat()}; one year after it is {frm}.'
    elif eng_date(eff) and len(pubs) == 1:  # the Proclamation names its own in-force day (e.g. the House's ratification)
        frm = eng_date(eff).isoformat()
        named = f' The issue is dated {min(pubs).isoformat()}; the version takes the day the Proclamation names.'
    else:
        problems.append(f'in-force clause is not "on publication": {eff[:160]}')
        frm = None
    no = re.search(r'(\d+)\s*/\s*(\d{4})', ls[i0]['t'])
    num = f'{no.group(1)}/{no.group(2)}'
    gnum = None
    for ln in gz.lines(dict(base, pages=(0, 0), band=(0, 10000))):
        m = re.search(r'(\d+)\s*(?:st|nd|rd|th)\s+Year\s+No\.?\s*(\d+)', ln['t'])
        if m:
            y = int(m.group(1))
            suf = 'th' if 10 <= y % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(y % 10, 'th')
            gnum = f'{y}{suf} Year No. {m.group(2)}'
    if problems:
        return None, problems
    lab = f'Proclamation No. {num}'
    spec = {
        'url': url, 'pages': base['pages'], 'x': [xg, 700], 'band': [top, bottom], 'pitch': pitch,
        'title_lines': n_title, 'start': '^' + re.escape(ls[i0]['t']) + '$', 'done': DONE,
        'head': head, 'slug': slug, 'short': f'{title.split(" Proclamation")[0]} Proc.',
        'title': f'{title} Proclamation No. {num}', 'law': f'proclamation-{num.replace("/", "-")}',
        'law_rec': {'label': lab, 'title': f'{title} Proclamation', 'kind': 'law', 'enacted': frm,
                    'published': min(pubs).isoformat()},
        'from': frm,
        'gazette': f'Federal Negarit Gazette, {gnum + ", " if gnum else ""}Addis Ababa, '
                   f'{min(pubs).day} {min(pubs).strftime("%B %Y")}',
        'in_force': f'Article {n} ({arts[-1][1]}): "{eff.strip()[:300]}"' + (named or f'; the issue is dated {frm}.'),
        'arts': n,
    }
    if not hb:
        spec['head_bold'] = False
    if part in FIXES:
        spec['fix'] = FIXES[part]
        spec['extra'] = [f"{spec['title']}: the heading of Article {a} is printed with the number {n} (page index {p}); "
                         f"it is keyed art-{a:03d}." for p, n, a in FIXES[part]]
    return spec, []


def main(argv):
    specs = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
    for k in range(0, len(argv), 4):
        part, url, slug, title = argv[k:k + 4]
        spec, problems = draft(part, url, slug, title)
        if spec:
            specs[part] = spec
            print(part, 'OK', spec['arts'], 'articles, from', spec['from'], '|', spec['gazette'])
        else:
            specs.pop(part, None)
            print(part, 'PROBLEMS', problems)
    tmp = OUT.with_suffix('.tmp')
    tmp.write_text(json.dumps(specs, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    tmp.replace(OUT)


if __name__ == '__main__':
    main(sys.argv[1:])
