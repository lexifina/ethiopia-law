"""Ethiopia first build: 1995 Constitution from Equipo Nizkor / Derechos copy (HTML). Reads the saved page, writes corpus.json."""
import re, html, json, hashlib, sys
from pathlib import Path
here = Path(__file__).resolve().parent
raw = (here / '.cache_der.html').read_bytes()
sha = hashlib.sha256(raw).hexdigest()
t = raw.decode('latin-1')
i = t.find('PROCLAMATION NO. 1/1995'); t = t[i:]
t = re.sub(r'<br\s*/?>', '\n', t); t = re.sub(r'</p>|</div>|</h\d>|</li>|<p>', '\n', t)
t = html.unescape(re.sub(r'<[^>]+>', '', t))
t = t.replace('\xa0', ' ').replace('\x92', "'").replace('\x93', '"').replace('\x94', '"').replace('’', "'").replace('“', '"').replace('”', '"')
t = t.replace('The House of the FederationArticle 61', 'The House of the Federation' + chr(10)*2 + 'Article 61')  # source glitch
t = t.split('[Source: Federal Negarit')[0]
j = t.find('\nPreamble\n'); pre_i = j + 1
body = t[pre_i:]
blocks = [re.sub(r'\s+', ' ', b).strip() for b in re.split(r'\n\s*\n', body)]
blocks = [b for b in blocks if b]
units = {}; order = []
cur = None
def strip_tail(bs):
    bs = list(bs)
    while bs:
        if re.match(r'^(Chapter|Part) (One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven)\b', bs[-1]): bs.pop(); continue
        if len(bs) > 1 and re.match(r'^(Chapter|Part) ', bs[-2]) : bs.pop(); continue
        break
    return bs
groups = []; g = None
for b in blocks:
    m = re.match(r'^Article (\d+)$', b)
    if b == 'Preamble': g = ('preamble', None, []); groups.append(g); continue
    if m: g = ('art', int(m.group(1)), []); groups.append(g); continue
    g[2].append(b)
for kind, n, bs in groups:
    bs = strip_tail(bs)
    if kind == 'preamble':
        key, label, lines = 'preamble', 'Preamble', bs
    else:
        key, label = f'art-{n:03d}', f'Article {n}'
        lines = [f'# {label}: {bs[0]}'] + bs[1:]
        if kind == 'art' and len(bs) < 2: raise SystemExit(f'article {n} empty')
    if kind == 'preamble': lines = ['# Preamble'] + lines
    units[key] = {'label': label, 'kind': 'preamble' if kind == 'preamble' else 'art', 'text': '\n'.join(lines) + '\n'}
assert [k for k in units if k.startswith('art')] == [f'art-{n:03d}' for n in range(1, 107)], 'article gap'
ks=[k for k in units if k.startswith('art')]; print([n for n in range(1,107) if f'art-{n:03d}' not in ks], [k for k in ks if int(k[4:])>106 or ks.count(k)>1], len(ks))
url = 'https://www.derechos.org/intlaw/doc/eth2.html'
corpus = {
 'country': {'code': 'ET', 'name': 'Ethiopia', 'slug': 'ethiopia', 'lang': 'en', 'tz': 'Africa/Addis_Ababa', 'future_branch': 'future',
   'publisher': {'name': 'Equipo Nizkor / Derechos Human Rights (copy of the Federal Negarit Gazeta text)', 'email': 'derechos@derechos-org.invalid'},
   'default_in_force_rule': {'text': 'Proclamation No. 1/1995, article 2: the Constitution came into full force and effect on 21 August 1995.', 'source': url},
   'licence_note': 'Official legislative text: not protected by copyright in Ethiopia (Copyright and Neighbouring Rights Protection Proclamation No. 410/2004, Art. 5(b)). Bytes copied from the Equipo Nizkor / Derechos site, https://www.derechos.org/intlaw/doc/eth2.html.'},
 'sources': [{'name': 'Equipo Nizkor / Derechos Human Rights: Constitution of the Federal Democratic Republic of Ethiopia, Proclamation No. 1/1995 (third-party copy of Federal Negarit Gazeta no. 1, 21 August 1995)', 'url': url, 'retrieved': '2026-10-30', 'licence': 'Law text exempt from copyright by Proclamation 410/2004 Art. 5(b); the host asserts no licence for it.', 'notes': 'English text. The Amharic version has final legal authority (Art. 106); it is not included.'}],
 'laws': {'proclamation-1-1995': {'label': 'Proclamation No. 1/1995', 'title': 'A Proclamation to pronounce the coming into effect of the Constitution of the Federal Democratic Republic of Ethiopia', 'kind': 'law', 'enacted': '1995-08-21', 'published': '1995-08-21', 'url': url, 'temporary_until': None, 'restores': None, 'note': None}},
 'acts': [{'slug': 'constitution', 'short': 'FDRE Const.', 'title': 'Constitution of the Federal Democratic Republic of Ethiopia (1995)', 'url': url, 'first_law': 'proclamation-1-1995', 'earlier_laws': [],
   'versions': [{'from': '1995-08-21', 'source_url': url, 'sha256': sha, 'units': units, 'credits': {k: ['proclamation-1-1995'] for k in units},
     'note': 'The Constitution as proclaimed in force on 21 August 1995 (ratified 8 December 1994). English text; the Amharic version has final legal authority.'}]}],
 'applies': [],
 'decisions': ['The English text is a third-party copy (Equipo Nizkor / Derechos) of the Federal Negarit Gazeta text. Its publication is allowed because Proclamation 410/2004 Art. 5(b) excludes "any official text of a legislative, administrative or of legal nature, as well as official translations thereof" from copyright; the host is credited as the source of the bytes.',
   'The version is dated 21 August 1995, the coming-into-force day in Proclamation No. 1/1995 art. 2; the Constitution is credited to that Proclamation.',
   'Chapter and Part headings are not separate units and are not in the files; articles are numbered 1 to 106 with their titles in each file heading.',
   'Hard line wraps in the HTML were joined; one paragraph or item per line. The Amharic text, which has final legal authority (Art. 106), is not included.'],
 'ai_use': ['none']}
(here / 'corpus.json').write_text(json.dumps(corpus, ensure_ascii=False, indent=1) + '\n', encoding='utf8', newline='\n')
print(len(units), 'units')
