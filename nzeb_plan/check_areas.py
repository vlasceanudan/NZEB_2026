# Inspect non-orange rects (special areas) and find pavilion outline candidates
import json, pathlib

base = pathlib.Path(r'C:\ClaudeCode\NZEB_2026\nzeb_plan')
words = json.loads((base/'words.json').read_text(encoding='utf-8'))
rects = json.loads((base/'rects.json').read_text(encoding='utf-8'))

def words_in(r):
    out = []
    for w in words:
        cx = (w['x0']+w['x1'])/2
        cy = (w['y0']+w['y1'])/2
        if r['x0'] <= cx <= r['x0']+r['w'] and r['y0'] <= cy <= r['y0']+r['h']:
            out.append(w['t'])
    return out

# big rects = pavilion outline candidates
print('--- LARGE RECTS (w>300 or h>300) ---')
for r in rects:
    if r['w'] > 300 or r['h'] > 300:
        print(f"x={r['x0']:7.1f} y={r['y0']:6.1f} w={r['w']:7.1f} h={r['h']:7.1f} fill={r['fill']} stroke={r['stroke']}")

print('--- BLUE/GREEN/OTHER colored rects with text (w*h>800) ---')
seen = set()
for r in rects:
    f = tuple(r['fill']) if r['fill'] else None
    if f in ((0.98,0.69,0.25), (1.0,1.0,1.0), None):
        continue
    if r['w']*r['h'] < 800:
        continue
    key = (r['x0'], r['y0'], r['w'], r['h'])
    if key in seen: continue
    seen.add(key)
    ws = words_in(r)
    if ws:
        print(f"fill={f} x={r['x0']:7.1f} y={r['y0']:6.1f} w={r['w']:6.1f} h={r['h']:6.1f} :: {' '.join(ws)[:80]}")
