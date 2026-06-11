# -*- coding: utf-8 -*-
# Top-down plot of the generated IFC for visual verification
import ifcopenshell, ifcopenshell.geom
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import multiprocessing

g = ifcopenshell.open(r'C:\ClaudeCode\NZEB_2026\NZEB_Expo_2026_Romexpo_B2.ifc')
settings = ifcopenshell.geom.settings()
settings.set('use-world-coords', True)

fig, ax = plt.subplots(figsize=(22, 10))
colors = {'IfcBuildingElementProxy': '#f5b040', 'IfcSpace': '#9b6fd0', 'IfcWall': '#888888',
          'IfcSlab': '#dddddd', 'IfcColumn': '#1a1a4d', 'IfcFurniture': '#cc2244', 'IfcCovering': '#7080a0'}

it = ifcopenshell.geom.iterator(settings, g, multiprocessing.cpu_count())
n = 0
if it.initialize():
    while True:
        shape = it.get()
        el = g.by_guid(shape.guid)
        cls = el.is_a()
        v = np.array(shape.geometry.verts).reshape(-1, 3)
        if len(v):
            x0, y0 = v[:, 0].min(), v[:, 1].min()
            x1, y1 = v[:, 0].max(), v[:, 1].max()
            if cls == 'IfcSlab':
                pass
            else:
                ax.add_patch(plt.Rectangle((x0, y0), x1-x0, y1-y0,
                             facecolor=colors.get(cls, '#cccccc'), edgecolor='k', linewidth=0.3,
                             alpha=0.55 if cls == 'IfcSpace' else 0.9))
                if cls == 'IfcBuildingElementProxy' and (x1-x0) > 2.5:
                    name = (el.Name or '')[:14]
                    ax.text((x0+x1)/2, (y0+y1)/2, name, fontsize=3.5, ha='center', va='center')
        n += 1
        if not it.next():
            break
print('shapes processed:', n)
# F15 highlight
for el in g.by_type('IfcProduct'):
    if el.Name and el.Name.startswith('F15'):
        pass
ax.set_xlim(-5, 270); ax.set_ylim(-5, 95)
ax.set_aspect('equal'); ax.set_title('NZEB Expo 2026 - IFC top view')
plt.tight_layout()
plt.savefig(r'C:\ClaudeCode\NZEB_2026\nzeb_plan\ifc_topview.png', dpi=130)
print('saved topview')

# zoom on F15
fig2, ax2 = plt.subplots(figsize=(10, 6))
it2 = ifcopenshell.geom.iterator(settings, g, multiprocessing.cpu_count())
if it2.initialize():
    while True:
        shape = it2.get()
        el = g.by_guid(shape.guid)
        if el.Name and (el.Name.startswith('F15') or (el.Name or '').find('BIMTECH') >= 0):
            v = np.array(shape.geometry.verts).reshape(-1, 3)
            x0, y0, x1, y1 = v[:,0].min(), v[:,1].min(), v[:,0].max(), v[:,1].max()
            zmax = v[:,2].max()
            ax2.add_patch(plt.Rectangle((x0, y0), x1-x0, y1-y0, fill=False, edgecolor='navy', linewidth=1.0))
            ax2.text((x0+x1)/2, (y0+y1)/2, f"{el.Name.replace('F15 - ','')} (h={zmax:.1f})", fontsize=6, ha='center', va='center')
        if not it2.next():
            break
ax2.set_xlim(100, 112); ax2.set_ylim(54, 62); ax2.set_aspect('equal')
ax2.set_title('F15 buildingSMART Romania - detaliu')
plt.tight_layout()
plt.savefig(r'C:\ClaudeCode\NZEB_2026\nzeb_plan\f15_detail.png', dpi=150)
print('saved f15 detail')
