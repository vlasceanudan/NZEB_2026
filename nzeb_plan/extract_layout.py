# Extract stand layout from NZEB plan PDF: words with coords + filled rectangles
import fitz, json, re, pathlib

doc = fitz.open(r'C:\Users\Dannyx\Downloads\37.Plan nZEB Expo Bucuresti 2026_update.pdf')
page = doc[0]

words = page.get_text('words')  # x0,y0,x1,y1,word,block,line,wordno
words_out = [{'x0': round(w[0],1), 'y0': round(w[1],1), 'x1': round(w[2],1), 'y1': round(w[3],1), 't': w[4]} for w in words]

drawings = page.get_drawings()
rects = []
for d in drawings:
    r = d['rect']
    fill = d.get('fill')
    if r.width < 5 or r.height < 5:
        continue
    rects.append({
        'x0': round(r.x0,1), 'y0': round(r.y0,1),
        'w': round(r.width,1), 'h': round(r.height,1),
        'fill': [round(c,2) for c in fill] if fill else None,
        'stroke': [round(c,2) for c in d.get('color')] if d.get('color') else None,
        'type': d.get('type'),
    })

out = pathlib.Path(r'C:\ClaudeCode\NZEB_2026\nzeb_plan')
(out/'words.json').write_text(json.dumps(words_out, ensure_ascii=False), encoding='utf-8')
(out/'rects.json').write_text(json.dumps(rects, ensure_ascii=False), encoding='utf-8')
print('words:', len(words_out), 'rects:', len(rects))

# quick stats on fill colors of rects sized like stands
from collections import Counter
c = Counter(tuple(r['fill']) if r['fill'] else None for r in rects)
for k, v in c.most_common(15):
    print(k, v)
