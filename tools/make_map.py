"""Genera el SVG del mapa de Ñeembucú a partir de geoBoundaries (gbOpen, CC BY 4.0)."""
import json, math, unicodedata
from shapely.geometry import shape, box, Point, LineString, MultiLineString
from shapely.ops import unary_union

def norm(s): return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
def load(p): return json.load(open(p))['features']

pry1 = load('geoBoundaries-PRY-ADM1_simplified.geojson')
pry2 = load('geoBoundaries-PRY-ADM2_simplified.geojson')
arg1 = load('geoBoundaries-ARG-ADM1_simplified.geojson')

TOL = 0.004  # grados; ~400 m
def geom(f, tol=TOL): return shape(f['geometry']).buffer(0).simplify(tol, preserve_topology=True)

deps = {f['properties']['shapeName']: geom(f) for f in pry1}
neem = deps['ÑEEMBUCU']
neighbors = {n: g for n, g in deps.items() if n != 'ÑEEMBUCU'}
argentina = {f['properties']['shapeName']: geom(f) for f in arg1 if f['properties']['shapeName'] in ('Chaco', 'Corrientes', 'Formosa')}

OPER = ('Pilar', 'Humaita', 'Paso De Patria')

# Distritos de Ñeembucú: centroide dentro del departamento
districts = {}
for f in pry2:
    g = geom(f)
    if neem.contains(g.representative_point()):
        districts[f['properties']['shapeName']] = g

# ---------- Proyección ----------
minx, miny, maxx, maxy = neem.bounds
lat0 = (miny + maxy) / 2
K = math.cos(math.radians(lat0))
PAD = 0.14
W = 1000
sx = W / ((maxx - minx) * K + 2 * PAD * K)
def P(lon, lat):
    x = ((lon - minx) * K + PAD * K) * sx
    y = ((maxy - lat) + PAD) * sx
    return x, y
H = round(((maxy - miny) + 2 * PAD) * sx)
VIEW = box(minx - PAD, miny - PAD, maxx + PAD, maxy + PAD)

def path(g, prec=1):
    parts = []
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms) if g.geom_type == 'MultiPolygon' else []
    for poly in polys:
        for ring in [poly.exterior, *poly.interiors]:
            pts = [P(*c) for c in ring.coords]
            parts.append('M' + ' '.join(f'{x:.{prec}f},{y:.{prec}f}' for x, y in pts) + 'Z')
    return ''.join(parts)

def linepath(g, prec=1):
    lines = [g] if g.geom_type == 'LineString' else list(g.geoms)
    out = []
    for ln in lines:
        pts = [P(*c) for c in ln.coords]
        out.append('M' + ' '.join(f'{x:.{prec}f},{y:.{prec}f}' for x, y in pts))
    return ''.join(out)

# Ríos = frontera internacional de Paraguay dentro de la vista (Paraguay al oeste, Paraná al sur)
py_union = unary_union(list(deps.values()))
outer = max(py_union.geoms, key=lambda g: g.area) if py_union.geom_type == 'MultiPolygon' else py_union
ring = list(outer.exterior.coords)[:-1]
conf = (-58.63, -27.28)
ci = min(range(len(ring)), key=lambda i: (ring[i][0]-conf[0])**2 + (ring[i][1]-conf[1])**2)
def walk(step):
    pts = [ring[ci]]
    i = ci
    for _ in range(len(ring)):
        i = (i + step) % len(ring)
        if not VIEW.buffer(0.08).contains(Point(ring[i])): break
        pts.append(ring[i])
    return pts
a, b = walk(1), walk(-1)
# el que sube en latitud es el río Paraguay
if a[min(5, len(a)-1)][1] > b[min(5, len(b)-1)][1]: para_pts, parana_pts = a, b
else: para_pts, parana_pts = b, a
paraguay = [LineString(para_pts).simplify(0.003)]
parana = [LineString(parana_pts).simplify(0.003)]
# Paraná aguas abajo: límite Chaco / Corrientes
down = argentina['Chaco'].boundary.intersection(argentina['Corrientes'].buffer(0.01)).intersection(VIEW.buffer(0.08))
if not down.is_empty:
    parana.append(down.simplify(0.003))

# ---------- Ciudades ----------
cities = [
    ('Pilar',           -58.300, -26.858, 'P'),
    ('Humaitá',         -58.517, -27.058, 'H'),
    ('Paso de Patria',  -58.567, -27.250, 'PP'),
]
pins = []
for name, lon, lat, code in cities:
    x, y = P(lon, lat)
    pins.append({'name': name, 'code': code, 'x': round(x, 1), 'y': round(y, 1), 'left': round(100 * x / W, 2), 'top': round(100 * y / H, 2)})

# ---------- Etiquetas de vecinos ----------
def label_pos(g):
    c = g.intersection(VIEW)
    if c.is_empty: return None
    p = c.representative_point()
    return P(p.x, p.y)

svg = []
svg.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mapa del departamento de Ñeembucú con Pilar, Humaitá y Paso de Patria">')
svg.append('''<defs>
<linearGradient id="nfill" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#D5EBD9"/><stop offset="1" stop-color="#B9DEC1"/></linearGradient>
<filter id="nsh" x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#0E3D14" flood-opacity=".22"/></filter>
<clipPath id="vclip"><rect x="0" y="0" width="WW" height="HH" rx="22"/></clipPath>
</defs>'''.replace('WW', str(W)).replace('HH', str(H)))
svg.append(f'<rect width="{W}" height="{H}" rx="22" fill="#E6E9E4"/>')
svg.append('<g clip-path="url(#vclip)">')
# Argentina
for n, g in argentina.items():
    svg.append(f'<path d="{path(g.intersection(VIEW.buffer(0.05)))}" fill="#E6E9E4" stroke="#fff" stroke-width="1.5"/>')
# Departamentos vecinos
for n, g in neighbors.items():
    gg = g.intersection(VIEW.buffer(0.05))
    if gg.is_empty: continue
    svg.append(f'<path d="{path(gg)}" fill="#E1EBE3" stroke="#fff" stroke-width="1.5"/>')
# Ñeembucú
svg.append(f'<path d="{path(neem)}" fill="url(#nfill)" stroke="#1B5E20" stroke-width="3" stroke-linejoin="round" filter="url(#nsh)"/>')
# Distritos donde opera ALMAR (relleno más intenso)
for n in OPER:
    svg.append(f'<path d="{path(districts[n])}" fill="#A9D4B4" stroke="none"/>')
# Límites distritales
for n, g in districts.items():
    svg.append(f'<path d="{path(g)}" fill="none" stroke="#fff" stroke-width="1.4" stroke-opacity=".85" stroke-linejoin="round"/>')
# Ríos
for group in (paraguay, parana):
    for l in group:
        d = linepath(l)
        svg.append(f'<path d="{d}" fill="none" stroke="#BFD9F5" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" stroke-opacity=".6"/>')
        svg.append(f'<path d="{d}" fill="none" stroke="#4A86D6" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>')
svg.append('</g>')

# Etiquetas de vecinos (posiciones fijas)
FONT = "font-family=\"'Barlow Condensed','Oswald',sans-serif\""
fixed = [('FORMOSA', (-58.52, -26.00), '#7A8580', 24), ('CHACO', (-58.62, -26.92), '#7A8580', 24), ('CORRIENTES', (-57.60, -27.47), '#7A8580', 24),
         ('ARGENTINA', (-58.52, -26.35), '#6B766F', 34),
         ('MISIONES', (-57.24, -26.74), '#6E8A74', 24), ('PARAGUARÍ', (-57.22, -26.06), '#6E8A74', 24), ('CENTRAL', (-57.55, -25.70), '#6E8A74', 24)]
for text, (lon, lat), col, fs in fixed:
    x, y = P(lon, lat)
    svg.append(f'<text x="{x:.0f}" y="{y:.0f}" {FONT} font-weight="600" font-size="{fs}" letter-spacing="3" fill="{col}" text-anchor="middle">{text}</text>')

# Etiquetas de ríos: texto recto, rotado según el tramo, del lado argentino
def nearest(pts, key):
    return min(pts, key=key)
def rot_label(pts, text, pick, p1, p2, dx, dy, fs=26):
    c = P(*pick)
    x1, y1 = P(*p1); x2, y2 = P(*p2)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    svg.append(f'<text transform="translate({c[0]+dx:.0f},{c[1]+dy:.0f}) rotate({ang:.1f})" {FONT} font-weight="700" font-size="{fs}" letter-spacing="3" fill="#2F6BBF" text-anchor="middle">{text}</text>')
pp = para_pts
rot_label(pp, 'RÍO PARAGUAY', nearest(pp, lambda p: abs(p[1]+26.55)), nearest(pp, lambda p: abs(p[1]+26.80)), nearest(pp, lambda p: abs(p[1]+26.30)), -48, 0)
pn = parana_pts
rot_label(pn, 'RÍO PARANÁ', nearest(pn, lambda p: abs(p[0]+58.18)), nearest(pn, lambda p: abs(p[0]+58.40)), nearest(pn, lambda p: abs(p[0]+57.95)), 0, 46)

# Etiquetas de distritos (los grandes; los de operación llevan el nombre de la ciudad)
LABELS = {'San Juan Bautista De Ñeembucu': 'S. J. BAUTISTA', 'General Diaz': 'GRAL. DÍAZ', 'Guazu Cua': 'GUAZÚ CUÁ', 'Isla Umbu': 'ISLA UMBÚ',
          'Los Laureles': 'LAURELES', 'Mayor Martinez': 'MAYOR MARTÍNEZ', 'Villalbin': 'VILLALBÍN'}
for n, g in districts.items():
    if n in OPER: continue
    if g.area < 0.02: continue
    p = g.representative_point(); x, y = P(p.x, p.y)
    svg.append(f'<text class="map-detail" x="{x:.0f}" y="{y:.0f}" {FONT} font-weight="600" font-size="15" letter-spacing="1.5" fill="#3F6A47" fill-opacity=".9" text-anchor="middle">{LABELS.get(n, n.upper())}</text>')

# Ciudad de Formosa (referencia del lado argentino)
fx, fy = P(-58.183, -26.173)
svg.append(f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="5" fill="#8A948E"/><text x="{fx-12:.0f}" y="{fy+6:.0f}" {FONT} font-weight="600" font-size="18" fill="#6B766F" text-anchor="end">Formosa</text>')

# Leyenda
lx, ly = 706, 400
svg.append('<g class="map-detail">')
svg.append(f'<rect x="{lx}" y="{ly}" width="266" height="168" rx="12" fill="#fff" fill-opacity=".9" stroke="#D8E3DA"/>')
items = [
  ('rect', '#A9D4B4', '#1B5E20', 'Distritos donde operamos'),
  ('rect', '#C9E4CF', '#1B5E20', 'Departamento de Ñeembucú'),
  ('pin', None, None, 'Puntos de atención'),
  ('line', '#4A86D6', None, 'Ríos navegables'),
  ('line', '#fff', '#B9C9BC', 'Límite distrital'),
]
for i, (kind, fill, stroke, text) in enumerate(items):
    yy = ly + 28 + i * 28
    if kind == 'rect':
        svg.append(f'<rect x="{lx+16}" y="{yy-9}" width="26" height="18" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    elif kind == 'line':
        bg = stroke or fill
        svg.append(f'<line x1="{lx+16}" y1="{yy}" x2="{lx+42}" y2="{yy}" stroke="{bg}" stroke-width="{6 if stroke else 5}" stroke-linecap="round"/>')
        if stroke: svg.append(f'<line x1="{lx+16}" y1="{yy}" x2="{lx+42}" y2="{yy}" stroke="{fill}" stroke-width="2.5" stroke-linecap="round"/>')
    else:
        svg.append(f'<g transform="translate({lx+29},{yy+8}) scale(.62)"><path d="M0,-34C-6.6,-34 -12,-28.6 -12,-22c0,8.4 12,22 12,22s12,-13.6 12,-22C12,-28.6 6.6,-34 0,-34z" fill="#E53935"/><circle cy="-22" r="5" fill="#fff"/></g>')
    svg.append(f'<text x="{lx+56}" y="{yy+6}" {FONT} font-weight="600" font-size="17" fill="#2F4A35">{text}</text>')
svg.append('</g>')

# Bloque de título (arriba a la izquierda)
svg.append(f'<text x="34" y="74" {FONT} font-weight="700" font-size="50" letter-spacing="5" fill="#1B5E20">ÑEEMBUCÚ</text>')
svg.append(f'<text x="36" y="104" {FONT} font-weight="600" font-size="19" letter-spacing="3.5" fill="#2D7D32">DEPARTAMENTO · PARAGUAY</text>')

# Ciudades: etiqueta + pin animado (CSS en index.html: .map-pin / .pulse)
PIN = '<path d="M0,-54C-10.6,-54 -19,-45.4 -19,-35c0,13.4 19,35 19,35s19,-21.6 19,-35C19,-45.4 10.6,-54 0,-54z" fill="#E53935"/><circle cy="-35" r="8" fill="#fff"/>'
for i, p in enumerate(pins):
    svg.append(f'<text x="{p["x"]+22}" y="{p["y"]+10}" {FONT} font-weight="700" font-size="32" fill="#15241A">{p["name"]}</text>')
for i, p in enumerate(pins):
    svg.append(f'<g transform="translate({p["x"]},{p["y"]})"><g class="map-pin" data-i="{i}"><circle class="pulse" cy="-8" r="12" fill="#E53935" fill-opacity=".45"/><g class="pin-body">{PIN}</g></g></g>')

# Inset: Paraguay con Ñeembucú resaltado
IW, IH = 190, 210
ix, iy = W - IW - 26, 26
allp = unary_union(list(deps.values()))
bx0, by0, bx1, by1 = allp.bounds
isx = (IW - 20) / ((bx1 - bx0) * K); isy = (IH - 20) / (by1 - by0); s = min(isx, isy)
def IP(lon, lat): return ix + 10 + (lon - bx0) * K * s, iy + 10 + (by1 - lat) * s
def ipath(g):
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    out = []
    for poly in polys:
        pts = [IP(*c) for c in poly.exterior.coords]
        out.append('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z')
    return ''.join(out)
svg.append(f'<rect x="{ix}" y="{iy}" width="{IW}" height="{IH}" rx="12" fill="#fff" fill-opacity=".92" stroke="#D8E3DA"/>')
svg.append(f'<path d="{ipath(allp.simplify(0.02))}" fill="#DCE7DE" stroke="#9FB8A5" stroke-width="1.2"/>')
svg.append(f'<path d="{ipath(neem.simplify(0.01))}" fill="#2D7D32" stroke="#1B5E20" stroke-width="1"/>')
svg.append(f'<text x="{ix+IW/2:.0f}" y="{iy+IH-8:.0f}" {FONT} font-weight="600" font-size="15" letter-spacing="2" fill="#5B6E60" text-anchor="middle">PARAGUAY</text>')

# Norte
nx, ny = 56, 175
svg.append(f'<g transform="translate({nx},{ny})"><path d="M0,-26 L9,10 L0,4 L-9,10 Z" fill="#1B5E20"/><text y="30" {FONT} font-weight="700" font-size="18" fill="#1B5E20" text-anchor="middle">N</text></g>')

# Escala (~20 km)
km20 = 20 / (111.32 * K) * K * sx  # 20 km en px
sx0, sy0 = 40, H - 40
svg.append(f'<g><line x1="{sx0}" y1="{sy0}" x2="{sx0+km20:.0f}" y2="{sy0}" stroke="#15241A" stroke-width="3"/><line x1="{sx0}" y1="{sy0-6}" x2="{sx0}" y2="{sy0+6}" stroke="#15241A" stroke-width="3"/><line x1="{sx0+km20:.0f}" y1="{sy0-6}" x2="{sx0+km20:.0f}" y2="{sy0+6}" stroke="#15241A" stroke-width="3"/><text x="{sx0+km20/2:.0f}" y="{sy0-12}" {FONT} font-weight="600" font-size="16" fill="#15241A" text-anchor="middle">20 km</text></g>')
svg.append(f'<text x="{W-14}" y="{H-12}" {FONT} font-size="12" fill="#8A9A8E" text-anchor="end">Límites: geoBoundaries (CC BY 4.0)</text>')
svg.append('</svg>')

out = ''.join(svg)
open('neembucu.svg', 'w').write(out)
json.dump({'W': W, 'H': H, 'pins': pins, 'districts': sorted(districts)}, open('pins.json', 'w'), ensure_ascii=False, indent=1)
print('W,H', W, H, 'bytes', len(out.encode()))
print('districts', len(districts), sorted(districts))
print('pins', pins)
print('river parts', len(paraguay), len(parana))
