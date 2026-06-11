# NZEB Expo 2026 — Pavilion B2 (Romexpo) · openBIM

Model IFC al pavilionului B2 de la Romexpo pentru **NZEB Expo București 2026** — toate cele ~199 de standuri ca elemente generice cu proprietăți (companie, website, clasificare pe domenii, zonă, suprafață), plus standul **buildingSMART România (F15)** modelat detaliat conform planșelor de arhitectură (panouri pop-up 223 cm, totem 4 m, zona discuții + zona "Classroom").

> *in openBIM we trust.*

## Conținut

| Fișier | Descriere |
|---|---|
| `NZEB_Expo_2026_Romexpo_B2.ifc` | Modelul IFC4 complet (pavilion, standuri, zone speciale, clasificare `IfcClassification` pe 24 de domenii, pset `NZEB_ExhibitorInfo`) |
| `NZEB_Expo_2026_Dashboard.html` | Dashboard self-contained (un singur fișier, merge offline): vedere 3D a geometriei IFC (Three.js), plan 2D, filtre pe zone/domenii/căutare, KPI-uri, detalii per stand |
| `nzeb_plan/` | Pipeline-ul Python de generare (IfcOpenShell) |

## Pipeline de regenerare

```
python nzeb_plan/extract_layout.py        # extrage geometria/textul din planul PDF al evenimentului
python nzeb_plan/build_dataset.py         # construieste stands.json (nume, pozitii, ID-uri standuri)
python nzeb_plan/build_ifc.py             # genereaza IFC-ul (pavilion + standuri + F15 detaliat)
python nzeb_plan/export_dashboard_data.py # extrage datele pentru dashboard din IFC
python nzeb_plan/export_3d_geometry.py    # extrage geometria triangulata (cu stiluri IFC) pentru vederea 3D
python nzeb_plan/build_dashboard.py       # asambleaza dashboard-ul final (date + geometrie + three.js inline)
```

Dependențe: `pip install ifcopenshell pymupdf` (+ `matplotlib` pentru `verify_plot.py`).

Notă: PDF-urile sursă (planul expoziției, planșele standului) nu sunt incluse în repo.

---
**buildingSMART România** · stand F15, Zona 3 · <https://buildingsmartromania.org/>
