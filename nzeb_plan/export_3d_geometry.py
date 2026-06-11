# -*- coding: utf-8 -*-
"""Export triangulated geometry (with IFC styles) for the 3D dashboard view."""
import json, multiprocessing
import ifcopenshell, ifcopenshell.geom, ifcopenshell.util.element
import numpy as np

g = ifcopenshell.open(r'C:\ClaudeCode\NZEB_2026\NZEB_Expo_2026_Romexpo_B2.ifc')
settings = ifcopenshell.geom.settings()
settings.set('use-world-coords', True)

def mat_info(m):
    c, t = (0.75, 0.75, 0.75), 0.0
    d = getattr(m, 'diffuse', None)
    if d is not None:
        try:
            c = (float(d.r()), float(d.g()), float(d.b()))
        except Exception:
            try:
                c = tuple(float(x) for x in d)[:3]
            except Exception:
                pass
    tr = getattr(m, 'transparency', 0.0)
    try:
        t = float(tr) if tr is not None else 0.0
    except Exception:
        t = 0.0
    if t != t:  # NaN
        t = 0.0
    return [round(c[0], 3), round(c[1], 3), round(c[2], 3), round(t, 3)]

# classify products for layer control + stand mapping
f15_guids = set()
stand_guid_self = {}   # product guid -> stand guid (itself for normal stands)
kind = {}              # guid -> stand|building|roof|space
f15_stand_guid = None

for el in g.by_type('IfcProduct'):
    psets = ifcopenshell.util.element.get_psets(el)
    name = el.Name or ''
    if 'NZEB_ExhibitorInfo' in psets:
        if name.startswith('F15 - '):
            f15_guids.add(el.GlobalId)
            kind[el.GlobalId] = 'stand'
            # acelasi criteriu ca export_dashboard_data: PRIMUL produs F15 din iterarea by_type('IfcProduct')
            if f15_stand_guid is None:
                f15_stand_guid = el.GlobalId
        else:
            kind[el.GlobalId] = 'stand'
            stand_guid_self[el.GlobalId] = el.GlobalId
    elif el.is_a('IfcSpace'):
        kind[el.GlobalId] = 'space'
    elif el.is_a('IfcWall') or el.is_a('IfcSlab'):
        kind[el.GlobalId] = 'roof' if 'Acoperis' in name else 'building'

# F15 elements all map to the F15 "stand record" guid (the covering, same as dashboard data)
for gd in f15_guids:
    stand_guid_self[gd] = f15_stand_guid

products = []
it = ifcopenshell.geom.iterator(settings, g, multiprocessing.cpu_count())
if it.initialize():
    while True:
        shape = it.get()
        guid = shape.guid
        k = kind.get(guid)
        if k:
            geom = shape.geometry
            v = np.round(np.array(geom.verts, dtype=float), 3)
            f = np.array(geom.faces, dtype=int)
            mats = [mat_info(m) for m in geom.materials] or [[0.75, 0.75, 0.75, 0.0]]
            mids = list(geom.material_ids) if list(geom.material_ids) else [0] * (len(f) // 3)
            mids = [m if m >= 0 else 0 for m in mids]
            products.append({
                'guid': guid, 'kind': k,
                'stand': stand_guid_self.get(guid),
                'v': v.tolist(), 'f': f.tolist(),
                'mats': mats, 'fm': mids,
            })
        if not it.next():
            break

out = r'C:\ClaudeCode\NZEB_2026\nzeb_plan\geometry3d.json'
json.dump({'products': products}, open(out, 'w', encoding='utf-8'), separators=(',', ':'))
import os
print('products:', len(products), '| size:', round(os.path.getsize(out)/1024), 'KB')
from collections import Counter
print(Counter(p['kind'] for p in products))
