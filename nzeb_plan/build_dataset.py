# -*- coding: utf-8 -*-
# Build curated stand dataset from extracted words + rects
import json, re, pathlib

base = pathlib.Path(r'C:\ClaudeCode\NZEB_2026\nzeb_plan')
words = json.loads((base/'words.json').read_text(encoding='utf-8'))
rects = json.loads((base/'rects.json').read_text(encoding='utf-8'))

def is_orange(f): return f and abs(f[0]-0.98)<0.03 and abs(f[1]-0.69)<0.03 and abs(f[2]-0.255)<0.03
BLUE = (0.1, 0.4, 0.82)
def is_blue(f): return f and abs(f[0]-0.1)<0.03 and abs(f[1]-0.4)<0.03 and abs(f[2]-0.82)<0.03

# collect candidate stand rects (dedupe identical)
seen = set()
cands = []
for r in rects:
    f = tuple(r['fill']) if r['fill'] else None
    if not (is_orange(f) or is_blue(f)):
        continue
    key = (r['x0'], r['y0'], r['w'], r['h'])
    if key in seen: continue
    seen.add(key)
    r = dict(r)
    r['color'] = 'orange' if is_orange(f) else 'blue'
    cands.append(r)

# big blue container rects to exclude (zone backgrounds, not stands)
def area(r): return r['w']*r['h']
cands = [r for r in cands if not (r['color']=='blue' and area(r) > 16000)]

id_re = re.compile(r'^([A-HMNO]\d{1,2}[ab]?)$')
noise_re = re.compile(r'^(\d+([.,]\d+)?\s*(sqm|mp|m)?|[xX=+]|\d+([.,]\d+)?\s?[xX]\s?\d+.*|sqm|mp|m|\d{9})$')

# assign each word to the SMALLEST candidate rect containing its center
assign = {}
for wi, w in enumerate(words):
    cx, cy = (w['x0']+w['x1'])/2, (w['y0']+w['y1'])/2
    best, best_a = None, 1e18
    for ri, r in enumerate(cands):
        if r['x0']-0.5 <= cx <= r['x0']+r['w']+0.5 and r['y0']-0.5 <= cy <= r['y0']+r['h']+0.5:
            if area(r) < best_a:
                best, best_a = ri, area(r)
    if best is not None:
        assign.setdefault(best, []).append(w)

stands = []
for ri, r in enumerate(cands):
    ws = sorted(assign.get(ri, []), key=lambda w: (round(w['y0']), w['x0']))
    sid, names = None, []
    for w in ws:
        t = w['t'].strip().replace('ﬁ','fi')
        if not t: continue
        if id_re.match(t):
            if sid is None: sid = t
        elif noise_re.match(t.replace(' ','')):
            continue
        else:
            names.append(t)
    name = ' '.join(names).strip()
    stands.append({'id': sid, 'name': name, 'x0': r['x0'], 'y0': r['y0'], 'w': r['w'], 'h': r['h'], 'color': r['color']})

# drop empty
stands = [s for s in stands if s['name'] or s['id']]

# ---- manual overrides keyed by (x0, y0) ----
OVR = {
    (367.4, 307.4): {'name': 'SYMMETRICA'},
    (410.4, 558.4): {'name': 'TESLA'},
    (410.4, 467.1): {'name': 'LEPAS'},
    (410.3, 228.6): {'name': 'SOLIS - Masina de curse'},
    (313.7, 467.4): {'name': 'LYNK&CO / ZEEKR'},
    (313.7, 558.4): {'name': 'DREAME'},
    (705.7, 477.6): {'name': 'NOVING AIR'},
    (1642.0, 337.2): {'name': 'ALL WORLD LOGISTICS'},
    (1589.1, 418.9): {'name': 'CRIANO EXIM'},
    (1386.6, 348.2): {'name': 'DAFCO FENDOOR'},
    (1386.6, 573.8): {'name': 'BUILDMAN STORE'},
    (1386.5, 406.5): {'name': 'HAPPY HOME CORPORATION'},
    (1386.7, 296.6): {'name': 'MHV TECHNOLOGY'},
    (177.5, 65.3):   {'name': 'BOSCH GROUP - PRO TOUR TRUCK'},
    (1589.3, 294.4): {'name': 'ART SHADOWS'},
    (616.4, 641.9):  {'name': 'HAUSENERGY'},
    (1319.4, 644.3, 82.3): {'name': 'Universitatea de Arhitectura si Urbanism Ion Mincu'},
    (1319.4, 644.3, 30.5): {'name': 'ARDBI'},
    (705.5, 499.7):  {'id': 'F5', 'name': 'IZO ONE'},
    (727.9, 499.7):  {'id': 'F5a', 'name': 'GUTMAN'},
    (750.4, 499.7):  {'id': 'F6', 'name': 'UNIKAT'},
    (837.0, 216.3):  {'id': 'E11', 'name': 'XELLA'},
    (836.9, 232.2):  {'id': 'E9', 'name': 'BARRIER'},
    (851.4, 232.2):  {'id': 'E9', 'name': 'BARRIER', 'drop': True},
    (577.4, 132.4):  {'id': 'G23', 'name': 'KRAFT CAMPUS + ZECAPH'},
    (626.0, 132.4):  {'id': 'G24', 'name': 'KRAFT CAMPUS'},
    (473.7, 162.0):  {'name': 'KRAFT CAMPUS'},
    (1095.2, 641.4): {'name': 'SMART CLIMA'},
    (524.7, 642.1):  {'name': 'BIKERS FOR HUMANITY'},
    (1127.8, 131.7): {'id': 'B20', 'name': 'CASA AVANTAJ'},
}
out = []
for s in stands:
    o = OVR.get((s['x0'], s['y0'], s['w'])) or OVR.get((s['x0'], s['y0']))
    if o:
        if o.get('drop'): continue
        s.update({k: v for k, v in o.items() if k != 'drop'})
    out.append(s)

# second pass: assign orphan stand-ID labels to nearest stand lacking an ID
used_ids = {s['id'] for s in out if s['id']}
id_words = []
for w in words:
    t = w['t'].strip()
    if id_re.match(t) and t not in used_ids:
        id_words.append((t, (w['x0']+w['x1'])/2, (w['y0']+w['y1'])/2))
for t, cx, cy in id_words:
    best, best_d = None, 1e18
    for s in out:
        if s['id']: continue
        sx, sy = s['x0']+s['w']/2, s['y0']+s['h']/2
        d = (sx-cx)**2 + (sy-cy)**2
        if d < best_d:
            best, best_d = s, d
    if best is not None and best_d < 40**2:
        best['id'] = t
        used_ids.add(t)

# Zona 7 machinery stands (inside big blue blob at x=1585): add manually
out += [
    {'id': 'Z7-1', 'name': 'SITECH / CAT', 'x0': 1589, 'y0': 533, 'w': 133, 'h': 52, 'color': 'blue'},
    {'id': 'Z7-2', 'name': 'KUHN',         'x0': 1589, 'y0': 595, 'w': 133, 'h': 52, 'color': 'blue'},
    {'id': 'Z7-3', 'name': 'UTILBEN',      'x0': 1589, 'y0': 657, 'w': 133, 'h': 52, 'color': 'blue'},
]

json.dump(out, open(base/'stands.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('total stands:', len(out))
for s in sorted(out, key=lambda s: (s['id'] or 'zz')):
    print(f"{s['id'] or '--':5} | {s['color'][:2]} | {s['name'][:60]}")
