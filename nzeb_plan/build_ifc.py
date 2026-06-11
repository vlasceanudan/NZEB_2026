# -*- coding: utf-8 -*-
"""Generate IFC4 model of NZEB Expo 2026 - Romexpo Pavilion B2 with all stands."""
import json, csv, math, pathlib, re
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid

run = ifcopenshell.api.run
base = pathlib.Path(r'C:\ClaudeCode\NZEB_2026\nzeb_plan')
stands_data = json.load(open(base/'stands.json', encoding='utf-8'))
words = json.loads((base/'words.json').read_text(encoding='utf-8'))

SCALE = 7.375          # pt per meter (calibrated on FORD stand 18x7m)
YREF = 690.6           # page-y of pavilion south edge -> ifc y=0

def m(v): return v / SCALE
def conv(x0, y0, w, h):
    """page rect -> (x, y, w, d) meters, y flipped"""
    return (m(x0), m(YREF - y0 - h), m(w), m(h))

# ---------------------------------------------------------------- categories
CATS = {
 'C01': 'Izolatii termice si anvelopa cladirii',
 'C02': 'Ferestre, usi, fatade si tamplarie',
 'C03': 'HVAC, incalzire, ventilatie si instalatii',
 'C04': 'Acoperisuri si hidroizolatii',
 'C05': 'Materiale de constructii',
 'C06': 'Chimie pentru constructii (adezivi, spume, etansari)',
 'C07': 'Scule, unelte, fixari si echipamente de masura',
 'C08': 'Energie regenerabila si fotovoltaice',
 'C09': 'Instalatii electrice si smart home',
 'C10': 'Software, BIM si servicii digitale',
 'C11': 'Dezvoltare imobiliara',
 'C12': 'Arhitectura, inginerie si antreprenoriat constructii',
 'C13': 'Educatie, asociatii si ONG',
 'C14': 'Auto si mobilitate',
 'C15': 'Mobilier, design si amenajari interioare',
 'C16': 'Gradina, peisagistica si exterior',
 'C17': 'Media si publicatii de specialitate',
 'C18': 'Furnizor de energie',
 'C19': 'Servicii financiar-bancare',
 'C20': 'Food & beverage / ospitalitate',
 'C21': 'Utilaje si echipamente pentru constructii',
 'C22': 'Constructii si structuri din lemn',
 'C23': 'Electrocasnice si tehnologie consumer',
 'C99': 'Produse si servicii pentru constructii (general)',
}

# company -> (category, website)  — matched on normalized upper name substring
INFO = {
 'BIMTECH': ('C10', 'https://buildingsmartromania.org/'),
 'ROTHOBLAAS': ('C22', 'https://www.rothoblaas.com'),
 'ALUPROF': ('C02', 'https://aluprof.eu'),
 'QFORT': ('C02', 'https://www.qfort.ro'),
 'BT MAIN': ('C19', 'https://www.bancatransilvania.ro'),
 'CEMACON': ('C05', 'https://cemacon.ro'),
 'CELLECO': ('C01', ''),
 'DIZAINAR': ('C15', 'https://www.dizainar.ro'),
 'E.ON': ('C18', 'https://www.eon.ro'),
 'ALUKÖNIGSTAHL': ('C02', 'https://www.alukoenigstahl.com'),
 'ALUGARD': ('C02', ''), 'ALUFORM': ('C02', ''), 'MEXI': ('C02', ''),
 'GENWAY': ('C09', ''),
 'SOUDAL': ('C06', 'https://www.soudal.com'),
 'PENOSIL': ('C06', 'https://penosil.com'),
 'SELENA': ('C06', 'https://selena.com'),
 'ZEHNDER': ('C03', 'https://www.zehndergroup.com'),
 'KUNATURA': ('C01', ''),
 'ROOF POWER': ('C08', ''),
 'GLULAM': ('C22', ''),
 'SAINT GOBAN': ('C05', 'https://www.saint-gobain.ro'),
 'ECOVENT': ('C03', ''),
 'ROMEPS': ('C01', ''),
 'XELLA': ('C05', 'https://www.xella.com'),
 'HUBUL LEMMNULUI': ('C22', ''),
 'BARRIER': ('C02', 'https://www.barrier.ro'),
 'CLIMATICO': ('C03', ''),
 'SISTEMA FLOOR': ('C03', ''),
 'FIBRAN': ('C01', 'https://fibran.gr'),
 'METIGLA': ('C04', 'https://www.metigla.ro'),
 'KRAFT CAMPUS': ('C13', ''),
 'IZO ONE': ('C01', ''),
 'CLIVET': ('C03', 'https://www.clivet.com'),
 'MENATWORK': ('C05', 'https://www.menatwork.ro'),
 'ALUMIL': ('C02', 'https://www.alumil.com'),
 'BAUDER': ('C04', 'https://www.bauder.de'),
 'PM ALUMINIUM': ('C02', ''),
 'WEDI': ('C05', 'https://www.wedi.de'),
 'KNIPEX': ('C07', 'https://www.knipex.com'),
 'VELUX': ('C04', 'https://www.velux.ro'),
 'HITACHI': ('C03', ''),
 'NOVATIK': ('C04', 'https://www.novatik.ro'),
 'ELECTRICON': ('C09', ''),
 'KNAUF': ('C05', 'https://www.knauf.ro'),
 'KRONOSPAN': ('C05', 'https://kronospan.com'),
 'GENERAL MEMBRANE': ('C04', 'https://www.generalmembrane.it'),
 'PLUSMINUS': ('C12', ''),
 'ATREA': ('C03', 'https://www.atrea.cz'),
 'GERARD': ('C04', 'https://www.gerardroofs.eu'),
 'MC BAUCHIMIE': ('C06', 'https://www.mc-bauchemie.com'),
 'SMART CLIMA': ('C03', ''),
 'MITSUBISHI': ('C03', ''),
 'HIPESHOP': ('C99', 'https://www.hipeshop.ro'),
 'INGINERIE CREATIVA': ('C12', ''),
 'LA FANTANA': ('C20', 'https://www.lafantana.ro'),
 'MOB TOP': ('C15', ''),
 'MAKITA': ('C07', 'https://www.makita.ro'),
 'SITECH': ('C21', ''), 'KUHN': ('C21', ''),
 'UTILBEN': ('C21', 'https://www.utilben.ro'),
 'FORD': ('C14', 'https://www.ford.ro'),
 'SYMMETRICA': ('C05', 'https://www.symmetrica.ro'),
 'ADURO': ('C03', ''),
 'STRABAG': ('C12', 'https://www.strabag.com'),
 'SKYLUX': ('C04', 'https://www.skylux.be'),
 'BIKERS FOR': ('C13', ''),
 'BOSCH': ('C07', 'https://www.bosch.ro'),
 'IBC FOCUS': ('C17', 'https://www.ibcfocus.ro'),
 'WEICON': ('C06', 'https://www.weicon.de'),
 'WOODSENSE': ('C22', ''), 'ISOGREEN': ('C01', ''),
 'VALROM': ('C03', 'https://www.valrom.ro'),
 'ATX HVAC': ('C03', ''),
 'TESTO': ('C07', 'https://www.testo.com'),
 'HECO': ('C07', 'https://www.heco-schrauben.de'),
 'DECEUNINCK': ('C02', 'https://www.deceuninck.ro'),
 'SOLAX': ('C08', 'https://www.solaxpower.com'),
 'NOVING AIR': ('C03', ''),
 'ROCKWOOL': ('C01', 'https://www.rockwool.com'),
 'ELIS PAVAJE': ('C05', 'https://www.elispavaje.ro'),
 'HAUSENERGY': ('C03', ''),
 'SEMINEE DEUS': ('C03', ''),
 'THERMOTOP': ('C03', ''), 'MAGNUM HEATING': ('C03', ''),
 'INTERO PROPERTY': ('C11', ''),
 'ECO GARDEN': ('C16', ''),
 'SIEGENIA': ('C02', 'https://www.siegenia.com'),
 'AIRO VENT': ('C03', ''),
 'ION MINCU': ('C13', 'https://www.uauim.ro'),
 'ACOPERO': ('C04', ''),
 'DOMUSA': ('C03', 'https://www.domusateknik.com'),
 'HL ROMANIA': ('C03', ''),
 'AVI PISCINE': ('C16', ''),
 'HEXONIC': ('C03', ''),
 'DREAME': ('C23', ''), 'TINECO': ('C23', 'https://www.tineco.com'),
 'TESLA': ('C14', 'https://www.tesla.com'),
 'SOLIS': ('C14', ''), 'LYNK&CO': ('C14', ''), 'LEPAS': ('C14', ''),
 'ZAHARIA CERAMIC': ('C05', ''),
 'REGULUS': ('C03', 'https://www.regulus.cz'),
 'DEWALT': ('C07', 'https://www.dewalt.com'),
 'DIMMER': ('C09', ''),
 'SPA JOY': ('C16', ''),
 'ISOMAT': ('C06', 'https://www.isomat.eu'),
 'EJOT': ('C07', 'https://www.ejot.com'),
 'ADWISERS': ('C12', ''),
 'METAWEALTH': ('C11', ''),
 'CRIANO': ('C05', 'https://www.criano.ro'),
 'CABANE SUCEVITA': ('C22', ''),
 'DEPANERO': ('C99', ''),
 'LEVIATAN': ('C12', ''),
 'FPSC': ('C13', ''),
 'UTCB': ('C13', 'https://utcb.ro'),
 'VIAROM': ('C12', 'https://www.viarom.ro'),
 'ERBASU': ('C12', 'https://www.erbasu.ro'),
 'PRIMA DEVELOPMENT': ('C11', ''),
 'CAFEA': ('C20', ''),
 'CERTSIGN': ('C10', 'https://www.certsign.ro'),
 'HABITAT FOR': ('C13', 'https://www.habitat.org'),
 'RONGO': ('C15', ''),
 'FACULTATEA DE ENERGETICA': ('C13', ''),
 'MM CITE': ('C15', 'https://www.mmcite.com'),
 'HEMPCRETE': ('C01', ''),
 'HANG AROUND': ('C16', ''),
 'ART SHADOWS': ('C15', ''),
 'PRIMITIV PLANTS': ('C16', ''),
 'MIRKA': ('C07', 'https://www.mirka.com'),
 'ECO HOUSE GARDEN': ('C16', ''),
 'RHINO SAFETY': ('C07', ''),
 'EXTREME SOLUTIONS': ('C99', ''),
 'STERCHELE': ('C99', ''), 'UNIPREST': ('C03', ''),
 'GUTMAN': ('C04', ''),
 'ONE CONCEPT': ('C03', ''),
}

def classify(name):
    u = (name or '').upper()
    for key, (cat, web) in INFO.items():
        if key in u:
            return cat, web
    return 'C99', ''

# ---------------------------------------------------------------- file setup
f = run('project.create_file', version='IFC4')
project = run('root.create_entity', f, ifc_class='IfcProject', name='NZEB Expo Bucuresti 2026')
lu = run('unit.add_si_unit', f, unit_type='LENGTHUNIT')
au = run('unit.add_si_unit', f, unit_type='AREAUNIT')
vu = run('unit.add_si_unit', f, unit_type='VOLUMEUNIT')
run('unit.assign_unit', f, units=[lu, au, vu])
model_ctx = run('context.add_context', f, context_type='Model')
body = run('context.add_context', f, context_type='Model',
           context_identifier='Body', target_view='MODEL_VIEW', parent=model_ctx)

site = run('root.create_entity', f, ifc_class='IfcSite', name='Romexpo Bucuresti - NZEB Expo 2026')
building = run('root.create_entity', f, ifc_class='IfcBuilding', name='Pavilionul B2')
storey = run('root.create_entity', f, ifc_class='IfcBuildingStorey', name='Parter')
run('aggregate.assign_object', f, products=[site], relating_object=project)
run('aggregate.assign_object', f, products=[building], relating_object=site)
run('aggregate.assign_object', f, products=[storey], relating_object=building)

def axis3d(x=0., y=0., z=0., angle=None):
    p = f.createIfcCartesianPoint((float(x), float(y), float(z)))
    if angle is None:
        return f.createIfcAxis2Placement3D(p, None, None)
    a = math.radians(angle)
    return f.createIfcAxis2Placement3D(p, f.createIfcDirection((0., 0., 1.)),
                                       f.createIfcDirection((math.cos(a), math.sin(a), 0.)))

site.ObjectPlacement = f.createIfcLocalPlacement(None, axis3d())
building.ObjectPlacement = f.createIfcLocalPlacement(site.ObjectPlacement, axis3d())
storey.ObjectPlacement = f.createIfcLocalPlacement(building.ObjectPlacement, axis3d())

# ---------------------------------------------------------------- styles
_styles = {}
def style(name, rgb, transp=0.0):
    if name not in _styles:
        rendering = f.createIfcSurfaceStyleRendering(
            f.createIfcColourRgb(None, *[float(c) for c in rgb]), float(transp),
            None, None, None, None, None, None, 'NOTDEFINED')
        _styles[name] = f.createIfcSurfaceStyle(name, 'BOTH', [rendering])
    return _styles[name]

ST = {
 'floor':   style('Pardoseala stand', (0.55, 0.55, 0.58)),
 'wall':    style('Perete stand', (0.92, 0.92, 0.90)),
 'navy':    style('Navy buildingSMART', (0.10, 0.10, 0.30)),
 'white':   style('Panou alb', (0.97, 0.97, 0.98)),
 'gradient':style('Panou gradient albastru', (0.75, 0.85, 0.95)),
 'pink':    style('Panou roz BIMcon', (0.78, 0.15, 0.45)),
 'black':   style('Negru TV', (0.05, 0.05, 0.05)),
 'cyan':    style('Cub cyan', (0.27, 0.67, 0.84)),
 'red':     style('Cub rosu', (0.85, 0.16, 0.28)),
 'magenta': style('Cub magenta', (0.82, 0.15, 0.55)),
 'purple':  style('Cub mov', (0.49, 0.18, 0.62)),
 'grey':    style('Gri deschis', (0.75, 0.75, 0.78)),
 'hallwall':style('Perete pavilion', (0.88, 0.88, 0.86), 0.0),
 'roof':    style('Acoperis pavilion', (0.80, 0.82, 0.85), 0.6),
 'slab':    style('Placa pavilion', (0.70, 0.70, 0.70)),
 'space':   style('Zona speciala', (0.45, 0.30, 0.75), 0.65),
 'space2':  style('Zona forum', (0.20, 0.45, 0.80), 0.65),
 'carpet':  style('Mocheta gri', (0.42, 0.44, 0.50)),
 'eonzone': style('Zona main partner', (0.30, 0.60, 0.15), 0.65),
}
ZONE_FLOOR = {
 'ZONA 1': style('Pardoseala Z1', (0.85, 0.70, 0.45)),
 'ZONA 2': style('Pardoseala Z2', (0.80, 0.62, 0.40)),
 'ZONA 3': style('Pardoseala Z3', (0.86, 0.66, 0.36)),
 'ZONA 4': style('Pardoseala Z4', (0.78, 0.66, 0.48)),
 'ZONA 5': style('Pardoseala Z5', (0.83, 0.60, 0.45)),
 'ZONA 6': style('Pardoseala Z6', (0.88, 0.72, 0.40)),
 'ZONA 7': style('Pardoseala Z7', (0.70, 0.62, 0.50)),
}

def box(w, d, h, x=0., y=0., z=0., st=None):
    prof = f.createIfcRectangleProfileDef('AREA', None,
        f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((float(x + w/2), float(y + d/2)))),
        float(w), float(d))
    solid = f.createIfcExtrudedAreaSolid(prof, axis3d(0, 0, z), f.createIfcDirection((0., 0., 1.)), float(h))
    if st is not None:
        f.createIfcStyledItem(solid, [st], None)
    return solid

def add_product(ifc_class, name, x, y, solids, container=None, parent_pl=None, description=None, ptype=None, angle=None):
    el = run('root.create_entity', f, ifc_class=ifc_class, name=name)
    if description:
        el.Description = description
    if ptype and hasattr(el, 'PredefinedType'):
        try: el.PredefinedType = ptype
        except Exception: pass
    el.ObjectPlacement = f.createIfcLocalPlacement(parent_pl or storey.ObjectPlacement, axis3d(x, y, 0, angle))
    rep = f.createIfcShapeRepresentation(body, 'Body', 'SweptSolid', solids)
    el.Representation = f.createIfcProductDefinitionShape(None, None, [rep])
    if container is not None:
        run('spatial.assign_container', f, products=[el], relating_structure=container)
    return el

# ---------------------------------------------------------------- pavilion
HX0, HY0 = m(40), m(YREF - 688)           # ~ (5.4, 0.35)
HX1, HY1 = m(1412), m(YREF - 56)          # ~ (191.5, 86.0)
HW, HD, HH = HX1 - HX0, HY1 - HY0, 9.0
T = 0.30

add_product('IfcSlab', 'Placa pardoseala Pavilion B2', HX0, HY0,
            [box(HW, HD, 0.2, z=-0.2, st=ST['slab'])], storey, ptype='FLOOR')
add_product('IfcSlab', 'Acoperis Pavilion B2', HX0, HY0,
            [box(HW, HD, 0.3, z=HH, st=ST['roof'])], storey, ptype='ROOF')
add_product('IfcWall', 'Perete pavilion - Sud', HX0, HY0, [box(HW, T, HH, st=ST['hallwall'])], storey)
add_product('IfcWall', 'Perete pavilion - Nord', HX0, HY1 - T, [box(HW, T, HH, st=ST['hallwall'])], storey)
add_product('IfcWall', 'Perete pavilion - Vest', HX0, HY0 + T, [box(T, HD - 2*T, HH, st=ST['hallwall'])], storey)
add_product('IfcWall', 'Perete pavilion - Est', HX1 - T, HY0 + T, [box(T, HD - 2*T, HH, st=ST['hallwall'])], storey)

# ---------------------------------------------------------------- zones (labels)
zone_pts = []
for i, w in enumerate(words):
    if w['t'] == 'ZONA' and i + 1 < len(words) and words[i+1]['t'] in '1234567':
        zone_pts.append((f"ZONA {words[i+1]['t']}", (w['x0']+w['x1'])/2, (w['y0']+w['y1'])/2))

def zone_of(s):
    if s['x0'] > 1450: return 'ZONA 7'
    cx, cy = s['x0'] + s['w']/2, s['y0'] + s['h']/2
    best, bd = 'ZONA 1', 1e18
    for zn, zx, zy in zone_pts:
        d = (zx-cx)**2 + (zy-cy)**2
        if d < bd: best, bd = zn, d
    return best

# ---------------------------------------------------------------- classification
classification = run('classification.add_classification', f, classification='NZEB Expo 2026 - Domenii expozanti')
cat_refs = {}
cat_products = {c: [] for c in CATS}

# ---------------------------------------------------------------- stand orientation
# spatele standului = latura cu vecin (alt stand lipit sau perete de pavilion);
# deschiderea = spre aleea libera
_rects = {id(s): conv(s['x0'], s['y0'], s['w'], s['h']) for s in stands_data}
_OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

def _contact(a, b, gap=0.6, min_ov=0.8):
    """laturile lui a pe care dreptunghiul b e lipit (cu lungimea de contact)"""
    ax, ay, aw, ad = a; bx, by, bw, bd = b
    out = {}
    ovx = min(ax + aw, bx + bw) - max(ax, bx)
    ovy = min(ay + ad, by + bd) - max(ay, by)
    if ovx > min_ov:
        if abs(by - (ay + ad)) < gap: out['N'] = ovx
        if abs((by + bd) - ay) < gap: out['S'] = ovx
    if ovy > min_ov:
        if abs(bx - (ax + aw)) < gap: out['E'] = ovy
        if abs((bx + bw) - ax) < gap: out['W'] = ovy
    return out

def stand_back(s):
    a = _rects[id(s)]
    contact = {'N': 0., 'S': 0., 'E': 0., 'W': 0.}
    for o in stands_data:
        if o is s:
            continue
        for dr, ln in _contact(a, _rects[id(o)]).items():
            contact[dr] += ln
    ax, ay, aw, ad = a
    if s['x0'] <= 1450:  # doar in pavilion: peretii halei conteaza ca "vecin"
        if abs(HY1 - (ay + ad)) < 1.2: contact['N'] += aw
        if abs(ay - HY0) < 1.2:        contact['S'] += aw
        if abs(HX1 - (ax + aw)) < 1.2: contact['E'] += ad
        if abs(ax - HX0) < 1.2:        contact['W'] += ad
    # ideal: vecin la spate si alee libera pe latura opusa
    cands = [d for d in 'NSEW' if contact[d] > 0 and contact[_OPP[d]] == 0]
    if not cands:
        cands = [d for d in 'NSEW' if contact[d] > 0]
    return max(cands, key=lambda d: contact[d]) if cands else 'N'

# ---------------------------------------------------------------- generic stands
csv_rows = []
proxies = []
for s in stands_data:
    sid, name = s['id'], s['name'] or (f"Stand {s['id']}" if s['id'] else 'Stand')
    x, y, w, d = conv(s['x0'], s['y0'], s['w'], s['h'])
    zone = zone_of(s)
    cat, web = classify(name)
    outdoor = s['x0'] > 1450
    container = site if outdoor else storey
    parent_pl = site.ObjectPlacement if outdoor else storey.ObjectPlacement
    label = f"{sid} - {name}" if sid else name
    is_f15 = (sid == 'F15')

    if not is_f15:
        wt = 0.08
        back = stand_back(s)
        solids = [box(w, d, 0.10, st=ZONE_FLOOR.get(zone, ST['floor']))]
        if min(w, d) > 1.0:
            sd = min(d * 0.6, 4.0)   # adancime pereti laterali (back N/S)
            sw = min(w * 0.6, 4.0)   # latime pereti laterali (back E/W)
            if back == 'N':
                solids += [box(w, wt, 2.5, y=d - wt, z=0.10, st=ST['wall']),
                           box(wt, sd, 2.5, x=0,      y=d - sd, z=0.10, st=ST['wall']),
                           box(wt, sd, 2.5, x=w - wt, y=d - sd, z=0.10, st=ST['wall'])]
            elif back == 'S':
                solids += [box(w, wt, 2.5, y=0, z=0.10, st=ST['wall']),
                           box(wt, sd, 2.5, x=0,      y=0, z=0.10, st=ST['wall']),
                           box(wt, sd, 2.5, x=w - wt, y=0, z=0.10, st=ST['wall'])]
            elif back == 'E':
                solids += [box(wt, d, 2.5, x=w - wt, z=0.10, st=ST['wall']),
                           box(sw, wt, 2.5, x=w - sw, y=0,      z=0.10, st=ST['wall']),
                           box(sw, wt, 2.5, x=w - sw, y=d - wt, z=0.10, st=ST['wall'])]
            else:  # W
                solids += [box(wt, d, 2.5, x=0, z=0.10, st=ST['wall']),
                           box(sw, wt, 2.5, x=0, y=0,      z=0.10, st=ST['wall']),
                           box(sw, wt, 2.5, x=0, y=d - wt, z=0.10, st=ST['wall'])]
        el = add_product('IfcBuildingElementProxy', label, x, y, solids, container, parent_pl,
                         description=f'Stand expozitional generic - {name}')
    else:
        el = None  # detailed below

    if el is not None:
        pset = run('pset.add_pset', f, product=el, name='NZEB_ExhibitorInfo')
        props = {
            'CompanyName': name,
            'StandNumber': sid or '',
            'Zone': zone,
            'AreaSqm': round(w * d, 1),
            'Category': CATS[cat],
            'CategoryCode': cat,
            'Indoor': not outdoor,
            'Event': 'NZEB Expo Bucuresti 2026',
        }
        if web: props['Website'] = web
        run('pset.edit_pset', f, pset=pset, properties=props)
        cat_products[cat].append(el)
        proxies.append(el)
    csv_rows.append({'StandNumber': sid or '', 'Company': name, 'Zone': zone,
                     'Category': CATS[cat], 'Website': web,
                     'X_m': round(x, 2), 'Y_m': round(y, 2), 'W_m': round(w, 2), 'D_m': round(d, 2)})

# ---------------------------------------------------------------- F15 detailed
# Conform planse BIT Arhitectura: A12 "Vederi + dimensiuni", A13 "Plan detaliat"
# Stand 7.00 x 4.00 m (28 mp), panouri pop-up textil h=2.23, totem h=4.00.
# A13 este in oglinda fata de modelul global: x_model = 7.0 - x_plan
# (CULOAR = dreapta modelului, EXPOZANT F18 = spate, EXPOZANT F17/METIGLA = stanga)
f15 = next(s for s in stands_data if s['id'] == 'F15')
_fx, _fy, _fw, _fd = conv(f15['x0'], f15['y0'], f15['w'], f15['h'])
SW, SD = 7.0, 4.0
FX = _fx + _fw - SW    # ancorat pe coltul spate-dreapta (culoar)
FY = _fy + _fd - SD
f15_zone = zone_of(f15)
f15_els = []

def fel(ifc_class, name, solids, desc=None, ptype=None, x=None, y=None, angle=None):
    el = add_product(ifc_class, f'F15 - {name}',
                     FX if x is None else x, FY if y is None else y,
                     solids, storey, description=desc, ptype=ptype, angle=angle)
    f15_els.append(el)
    return el

def cyl(r, h, cx, cy, z=0., st=None):
    prof = f.createIfcCircleProfileDef('AREA', None,
        f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((float(cx), float(cy)))), float(r))
    s = f.createIfcExtrudedAreaSolid(prof, axis3d(0, 0, z), f.createIfcDirection((0., 0., 1.)), float(h))
    if st is not None: f.createIfcStyledItem(s, [st], None)
    return s

def ell(rx, ry, h, cx, cy, z=0., st=None):
    prof = f.createIfcEllipseProfileDef('AREA', None,
        f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((float(cx), float(cy)))), float(rx), float(ry))
    s = f.createIfcExtrudedAreaSolid(prof, axis3d(0, 0, z), f.createIfcDirection((0., 0., 1.)), float(h))
    if st is not None: f.createIfcStyledItem(s, [st], None)
    return s

def chair(cx, cy, facing='N', st=None):
    """scaun generic: sezut + spatar; facing = directia in care priveste (N/S/E/V)"""
    solids = [box(0.48, 0.48, 0.45, x=cx-0.24, y=cy-0.24, z=0.02, st=st)]
    if facing == 'N':   solids.append(box(0.48, 0.07, 0.50, x=cx-0.24, y=cy-0.31, z=0.45, st=st))
    elif facing == 'S': solids.append(box(0.48, 0.07, 0.50, x=cx-0.24, y=cy+0.24, z=0.45, st=st))
    elif facing == 'E': solids.append(box(0.07, 0.48, 0.50, x=cx-0.31, y=cy-0.24, z=0.45, st=st))
    else:               solids.append(box(0.07, 0.48, 0.50, x=cx+0.24, y=cy-0.24, z=0.45, st=st))
    return solids

PT = 0.05   # grosime panou pop-up
PH = 2.23   # inaltime panou
PZ = 0.02   # peste mocheta

# mocheta 7.00 x 4.00 (finisaj pardoseala conform A13)
fel('IfcCovering', 'Mocheta stand 28 mp', [box(SW, SD, 0.02, st=ST['carpet'])], ptype='FLOORING')

# perete spate (EXPOZANT/F18): 5 panouri 120+120+150+150+150 (stanga->dreapta in plan A13, oglindit aici)
back_panels = [(5.75, 1.20), (4.55, 1.20), (3.05, 1.50), (1.55, 1.50), (0.05, 1.50)]
for i, (px, pw) in enumerate(back_panels):
    stp = ST['gradient'] if i % 2 == 0 else ST['white']
    fel('IfcWall', f'Panou pop-up textil {int(pw*100)}x223 (spate {i+1})',
        [box(pw, PT, PH, x=px, y=SD - PT, z=PZ, st=stp)])

# perete lateral stanga (EXPOZANT/F17 METIGLA): 120+120+150 dinspre spate
side_panels = [(2.75, 1.20), (1.55, 1.20), (0.05, 1.50)]
for i, (py, pw) in enumerate(side_panels):
    fel('IfcWall', f'Panou pop-up textil {int(pw*100)}x223 (lateral {i+1})',
        [box(PT, pw, PH, x=0.0, y=py, z=PZ, st=ST['white'] if i % 2 == 0 else ST['gradient'])])

# front partial - inchidere zona Classroom: 150+120 dinspre stanga
front_panels = [(0.05, 1.50), (1.55, 1.20)]
for i, (px, pw) in enumerate(front_panels):
    fel('IfcWall', f'Panou pop-up textil {int(pw*100)}x223 (front {i+1})',
        [box(pw, PT, PH, x=px, y=0.0, z=PZ, st=ST['gradient'] if i % 2 == 0 else ST['white'])])

# panou despartitor 240x223 intre zona discutii si Classroom (la 2.93 de marginea stanga)
fel('IfcWall', 'Panou pop-up textil 240x223 (despartitor)',
    [box(PT, 2.40, PH, x=2.93, y=0.0, z=PZ, st=ST['pink'])],
    desc='Separa zona discutii de zona Classroom')

# totem "in openBIM we trust" - 4.00 m, coltul spate-dreapta, spre culoar (conform A12)
fel('IfcColumn', 'Totem "in openBIM we trust" 4.00 m',
    [box(0.80, 0.80, 4.00, x=6.10, y=3.15, z=PZ, st=ST['navy'])],
    desc='Totem textil navy 4.0 m cu branding buildingSMART Romania, colt culoar')

# --- Zona Classroom (stanga, x 0..2.93) ---
fel('IfcFurniture', 'Stand TV + Televizor (Classroom)', [
    box(0.10, 0.40, 0.80, x=1.35, y=3.40, z=PZ, st=ST['black']),
    box(0.10, 0.40, 0.80, x=2.45, y=3.40, z=PZ, st=ST['black']),
    box(1.30, 0.08, 0.75, x=1.30, y=3.56, z=0.80, st=ST['black']),
])
fel('IfcFurniture', 'Desk portabil oval',
    [ell(0.60, 0.32, 0.75, cx=0.75, cy=3.30, z=PZ, st=ST['white'])])
cls_chairs = []
for cy_ in (1.05, 1.95):
    for cx_ in (0.55, 1.35, 2.15):
        cls_chairs += chair(cx_, cy_, 'N', ST['navy'])
fel('IfcFurniture', 'Scaune zona Classroom (6 buc)', cls_chairs,
    desc='Doua randuri x 3 scaune orientate spre TV')

# --- Zona discutii (dreapta, x 2.98..7.0) ---
fel('IfcFurniture', 'Masa rotunda discutii + scaune',
    [cyl(0.40, 0.75, cx=5.35, cy=3.25, z=PZ, st=ST['white'])]
    + chair(5.35, 2.55, 'N', ST['navy'])
    + chair(4.70, 3.25, 'E', ST['navy'])
    + chair(6.00, 2.70, 'V', ST['navy']))
fel('IfcFurniture', 'Masa bar', [cyl(0.225, 1.05, cx=6.40, cy=2.45, z=PZ, st=ST['navy'])])
fel('IfcCovering', 'Covor oval decorativ',
    [ell(0.80, 0.50, 0.012, cx=4.60, cy=2.10, z=0.022, st=ST['grey'])], ptype='FLOORING')
# TV mobil pe diagonala, orientat spre zona discutii (oglindit fata de A12)
fel('IfcFurniture', 'Stand TV + Televizor (zona discutii)', [
    box(0.10, 0.40, 0.80, x=-0.60, y=-0.20, st=ST['black']),
    box(0.10, 0.40, 0.80, x=0.50, y=-0.20, st=ST['black']),
    box(1.30, 0.08, 0.75, x=-0.65, y=-0.04, z=0.80, st=ST['black']),
], x=FX + 4.50, y=FY + 2.35, angle=-45.0)

# cuburi decorative 50x50 cu litere IFC + logo deasupra (front zona discutii, conform A12/A13)
cb = 0.50
cube_items = [
    box(cb, cb, cb, x=4.70, y=0.15, z=PZ, st=ST['cyan']),
    box(cb, cb, cb, x=5.22, y=0.15, z=PZ, st=ST['red']),
    box(cb, cb, cb, x=5.74, y=0.15, z=PZ, st=ST['purple']),
    box(cb, cb, cb, x=6.40, y=0.35, z=PZ, st=ST['white']),
    box(cb, cb, cb, x=6.40, y=0.35, z=PZ + cb, st=ST['magenta']),
]
fel('IfcFurniture', 'Cuburi decorative 50x50 cu litere I-F-C', cube_items,
    desc='Cuburi decorative colorate cu literele I, F, C')
fel('IfcFurniture', 'Logo IFC 3D',
    [box(0.90, 0.25, 0.85, x=4.95, y=0.27, z=PZ + cb, st=ST['white'])],
    desc='Sculptura logo buildingSMART/IFC asezata pe cuburi')

# pset on every F15 element
F15_PROPS = {
    'CompanyName': 'buildingSMART Romania (BIMTECH)',
    'StandNumber': 'F15',
    'Zone': f15_zone,
    'AreaSqm': 28.0,
    'FloorFinish': 'mocheta',
    'Designer': 'BIT Arhitectura - arh. Stefan Constantinescu, arh. Ruxandra Chirca',
    'Category': CATS['C10'],
    'CategoryCode': 'C10',
    'Website': 'https://buildingsmartromania.org/',
    'Indoor': True,
    'Event': 'NZEB Expo Bucuresti 2026',
    'Slogan': 'in openBIM we trust.',
}
for el in f15_els:
    pset = run('pset.add_pset', f, product=el, name='NZEB_ExhibitorInfo')
    run('pset.edit_pset', f, pset=pset, properties=F15_PROPS)
    cat_products['C10'].append(el)
csv_rows.append({'StandNumber': 'F15', 'Company': 'buildingSMART Romania (BIMTECH)', 'Zone': f15_zone,
                 'Category': CATS['C10'], 'Website': 'https://buildingsmartromania.org/',
                 'X_m': round(FX, 2), 'Y_m': round(FY, 2), 'W_m': SW, 'D_m': SD})

# ---------------------------------------------------------------- special areas as IfcSpace
AREAS = [
    ('Networking Area',                  (837.7, 418.3, 96.9, 111.0), 'space'),
    ('Wembley Lounge',                   (253.6, 228.7, 125.4, 44.6), 'space'),
    ('VIP Lounge by The Concept',        (1030.0, 65.3, 155.4, 43.6), 'space'),
    ('Beer & Coffee Partner Lounge Area',(177.5, 133.3, 269.0, 67.3), 'space'),
    ('nZEB Depozit + Offices',           (48.4, 65.4, 94.8, 165.5),   'space'),
    ('Forumul Constructiilor',           (48.1, 451.9, 243.3, 228.5), 'space2'),
    ('Main Partner Area - powered by E.ON', (1186.3, 65.3, 214.4, 211.0), 'eonzone'),
    ('Arena Mesterilor (exterior)',      (1752.8, 429.1, 135.5, 356.0), 'space2'),
]
for name, rect, stkey in AREAS:
    x, y, w, d = conv(*rect)
    sp = run('root.create_entity', f, ifc_class='IfcSpace', name=name)
    sp.ObjectPlacement = f.createIfcLocalPlacement(storey.ObjectPlacement, axis3d(x, y, 0))
    rep = f.createIfcShapeRepresentation(body, 'Body', 'SweptSolid', [box(w, d, 3.0, st=ST[stkey])])
    sp.Representation = f.createIfcProductDefinitionShape(None, None, [rep])
    run('aggregate.assign_object', f, products=[sp], relating_object=storey)
    pset = run('pset.add_pset', f, product=sp, name='NZEB_AreaInfo')
    run('pset.edit_pset', f, pset=pset, properties={'AreaName': name, 'AreaSqm': round(w*d, 1),
                                                    'Event': 'NZEB Expo Bucuresti 2026'})

# ---------------------------------------------------------------- classification refs
for code, prods in cat_products.items():
    if not prods:
        continue
    run('classification.add_reference', f, products=prods,
        identification=code, name=CATS[code], classification=classification)

# ---------------------------------------------------------------- write outputs
out_ifc = r'C:\ClaudeCode\NZEB_2026\NZEB_Expo_2026_Romexpo_B2.ifc'
f.write(out_ifc)

with open(base/'stands_summary.csv', 'w', newline='', encoding='utf-8-sig') as fh:
    wcsv = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
    wcsv.writeheader()
    wcsv.writerows(csv_rows)

print('IFC written:', out_ifc)
print('stands (generic):', len(proxies), '| F15 elements:', len(f15_els), '| spaces:', len(AREAS))

# quick validation re-open
g = ifcopenshell.open(out_ifc)
from collections import Counter
c = Counter(e.is_a() for e in g.by_type('IfcProduct'))
for k, v in sorted(c.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')
print('classification refs:', len(g.by_type('IfcClassificationReference')))
print('psets:', len(g.by_type('IfcPropertySet')))
