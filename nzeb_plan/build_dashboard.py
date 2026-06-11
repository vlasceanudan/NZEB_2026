# -*- coding: utf-8 -*-
"""Assemble the final self-contained dashboard HTML (data + 3D geometry + three.js inline)."""
import json, pathlib

base = pathlib.Path(r'C:\ClaudeCode\NZEB_2026\nzeb_plan')
tpl = (base/'dashboard_template.html').read_text(encoding='utf-8')
data = (base/'dashboard_data.json').read_text(encoding='utf-8')
geo = (base/'geometry3d.json').read_text(encoding='utf-8')
three = (base/'lib'/'three.min.js').read_text(encoding='utf-8')
orbit = (base/'lib'/'OrbitControls.js').read_text(encoding='utf-8')
logo = (base/'lib'/'logo_bsro.svg').read_text(encoding='utf-8')

html = (tpl.replace('__THREE__', three)
           .replace('__ORBIT__', orbit)
           .replace('__GEO__', geo)
           .replace('__DATA__', data)
           .replace('__LOGO__', logo))
out = pathlib.Path(r'C:\ClaudeCode\NZEB_2026\NZEB_Expo_2026_Dashboard.html')
out.write_text(html, encoding='utf-8')
print('written:', out, f'({out.stat().st_size/1024:.0f} KB)')
