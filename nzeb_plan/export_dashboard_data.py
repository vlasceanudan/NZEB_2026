# -*- coding: utf-8 -*-
"""Extract dashboard data (stands, areas, footprints) from the generated IFC."""
import json, multiprocessing
import ifcopenshell, ifcopenshell.geom, ifcopenshell.util.element
import numpy as np

g = ifcopenshell.open(r'C:\ClaudeCode\NZEB_2026\NZEB_Expo_2026_Romexpo_B2.ifc')
settings = ifcopenshell.geom.settings()
settings.set('use-world-coords', True)

bboxes = {}
it = ifcopenshell.geom.iterator(settings, g, multiprocessing.cpu_count())
if it.initialize():
    while True:
        shape = it.get()
        v = np.array(shape.geometry.verts).reshape(-1, 3)
        if len(v):
            bboxes[shape.guid] = [float(v[:,0].min()), float(v[:,1].min()),
                                  float(v[:,0].max()), float(v[:,1].max())]
        if not it.next():
            break

stands = []
f15_elements = []
f15_bb = None
pavilion = None
areas = []

for el in g.by_type('IfcProduct'):
    bb = bboxes.get(el.GlobalId)
    psets = ifcopenshell.util.element.get_psets(el)
    name = el.Name or ''

    if el.is_a('IfcSlab') and 'pardoseala Pavilion' in name and bb:
        pavilion = bb

    if 'NZEB_AreaInfo' in psets and bb:
        ai = psets['NZEB_AreaInfo']
        areas.append({'name': ai.get('AreaName', name), 'area': ai.get('AreaSqm', 0),
                      'x': round(bb[0],2), 'y': round(bb[1],2),
                      'w': round(bb[2]-bb[0],2), 'd': round(bb[3]-bb[1],2)})
        continue

    if 'NZEB_ExhibitorInfo' not in psets or not bb:
        continue
    info = psets['NZEB_ExhibitorInfo']

    if name.startswith('F15 - '):
        f15_elements.append(name[6:])
        f15_bb = bb if f15_bb is None else [min(f15_bb[0],bb[0]), min(f15_bb[1],bb[1]),
                                            max(f15_bb[2],bb[2]), max(f15_bb[3],bb[3])]
        if not any(s.get('f15') for s in stands):
            stands.append({'f15': True, 'guid': el.GlobalId,
                'id': 'F15', 'name': info.get('CompanyName',''),
                'zone': info.get('Zone',''), 'cat': info.get('Category',''),
                'catCode': info.get('CategoryCode',''), 'website': info.get('Website',''),
                'area': info.get('AreaSqm', 0), 'indoor': True,
                'designer': info.get('Designer',''), 'floor': info.get('FloorFinish',''),
                'x': 0, 'y': 0, 'w': 0, 'd': 0})
        continue

    stands.append({'f15': False, 'guid': el.GlobalId,
        'id': info.get('StandNumber','') or '', 'name': info.get('CompanyName', name),
        'zone': info.get('Zone',''), 'cat': info.get('Category',''),
        'catCode': info.get('CategoryCode',''), 'website': info.get('Website',''),
        'area': round(float(info.get('AreaSqm',0)),1), 'indoor': bool(info.get('Indoor', True)),
        'x': round(bb[0],2), 'y': round(bb[1],2),
        'w': round(bb[2]-bb[0],2), 'd': round(bb[3]-bb[1],2)})

# patch F15 footprint
for s in stands:
    if s.get('f15'):
        s['x'], s['y'] = round(f15_bb[0],2), round(f15_bb[1],2)
        s['w'], s['d'] = round(f15_bb[2]-f15_bb[0],2), round(f15_bb[3]-f15_bb[1],2)
        s['elements'] = f15_elements

data = {
    'event': 'NZEB Expo Bucuresti 2026',
    'building': 'Romexpo - Pavilionul B2',
    'pavilion': {'x': round(pavilion[0],2), 'y': round(pavilion[1],2),
                 'w': round(pavilion[2]-pavilion[0],2), 'd': round(pavilion[3]-pavilion[1],2)},
    'stands': stands,
    'areas': areas,
}
out = r'C:\ClaudeCode\NZEB_2026\nzeb_plan\dashboard_data.json'
json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
zones = sorted({s['zone'] for s in stands})
cats = sorted({s['cat'] for s in stands})
print('stands:', len(stands), '| areas:', len(areas), '| zones:', zones)
print('cats:', len(cats))
print('pavilion:', data['pavilion'])
