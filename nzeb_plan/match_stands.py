# Match stand-ID labels + company names to orange stand rectangles
import json, re, pathlib

base = pathlib.Path(r'C:\ClaudeCode\NZEB_2026\nzeb_plan')
words = json.loads((base/'words.json').read_text(encoding='utf-8'))
rects = json.loads((base/'rects.json').read_text(encoding='utf-8'))

ORANGE = (0.98, 0.69, 0.25)
stand_rects = [r for r in rects if r['fill'] and tuple(r['fill']) == ORANGE]

# dedupe overlapping identical rects
seen = set()
uniq = []
for r in stand_rects:
    key = (r['x0'], r['y0'], r['w'], r['h'])
    if key not in seen:
        seen.add(key)
        uniq.append(r)
stand_rects = uniq
print('unique orange rects:', len(stand_rects))

id_re = re.compile(r'^([A-HMNO]\d{1,2}[ab]?|M0a?)$')
area_re = re.compile(r'^(\d+[.,]?\d*)\s*(sqm|mp|m)$', re.I)

def words_in(r, pad=1.0):
    out = []
    for w in words:
        cx = (w['x0']+w['x1'])/2
        cy = (w['y0']+w['y1'])/2
        if r['x0']-pad <= cx <= r['x0']+r['w']+pad and r['y0']-pad <= cy <= r['y0']+r['h']+pad:
            out.append(w)
    return out

stands = []
for r in stand_rects:
    ws = sorted(words_in(r), key=lambda w: (w['y0'], w['x0']))
    sid = None
    names = []
    area = None
    dims = None
    for w in ws:
        t = w['t'].strip()
        if not t:
            continue
        if id_re.match(t):
            sid = t if sid is None else sid
        elif area_re.match(t.replace(' ', '')):
            pass
        elif re.match(r'^\d+[.,]?\d*(sqm|mp)$', t, re.I):
            area = t
        elif re.match(r'^\d+[xX]\s?\d+', t) or t.lower() in ('sqm','mp','m','x','=') or re.match(r'^\d+[.,]?\d*$', t):
            dims = (dims or '') + ' ' + t
        else:
            names.append(t)
    stands.append({'rect': r, 'id': sid, 'name': ' '.join(names), 'area': area, 'dims': (dims or '').strip()})

with_id = [s for s in stands if s['id']]
print('with id:', len(with_id), '/ total:', len(stands))
for s in sorted(stands, key=lambda s: (s['id'] or 'zz')):
    r = s['rect']
    print(f"{s['id'] or '??':5} | {s['name'][:45]:45} | {s['area'] or '':8} | {s['dims'][:20]:20} | x={r['x0']:7.1f} y={r['y0']:6.1f} w={r['w']:6.1f} h={r['h']:6.1f}")
