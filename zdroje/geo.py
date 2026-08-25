# -*- coding: utf-8 -*-
"""Z Natural Earth udela male datove pole pro zemekouli na strance.
Zdroj: nvkelso/natural-earth-vector (public domain)."""
import json, math

def dp(pts, eps):
    """Douglas-Peucker: zjednoduseni linie."""
    if len(pts) < 3: return pts
    dmax, idx = 0.0, 0
    x1, y1 = pts[0]; x2, y2 = pts[-1]
    dx, dy = x2 - x1, y2 - y1
    nrm = math.hypot(dx, dy)
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / nrm if nrm else math.hypot(x - x1, y - y1)
        if d > dmax: dmax, idx = d, i
    if dmax > eps:
        return dp(pts[:idx + 1], eps)[:-1] + dp(pts[idx:], eps)
    return [pts[0], pts[-1]]

def prstence(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon": return [c[0]]
    if t == "MultiPolygon": return [p[0] for p in c]
    return []

def zpracuj(rings, eps, minbod, des=1):
    out = []
    for r in rings:
        s = dp([(p[0], p[1]) for p in r], eps)
        if len(s) < minbod: continue
        out.append([[round(x, des), round(y, des)] for x, y in s])
    return out

def nacti(soubor):
    with open(soubor) as f: return json.load(f)["features"]

# --- pevnina pro zemekouli: hrubá, ale kontinenty musí být poznat ---
zeme = []
for f in nacti("ne_110m_land.json"):
    zeme += zpracuj(prstence(f["geometry"]), 0.9, 5, 1)

# --- Brazílie ---
brazilie = []
for f in nacti("ne_110m_admin_0_countries.json"):
    p = f["properties"]
    if p.get("ADM0_A3") == "BRA" or p.get("NAME") == "Brazil":
        brazilie += zpracuj(prstence(f["geometry"]), 0.25, 6, 2)

# --- Acre ---
acre = []
for f in nacti("ne_50m_admin_1_states_provinces.json"):
    p = f["properties"]
    if p.get("name") == "Acre" and p.get("admin") == "Brazil":
        acre += zpracuj(prstence(f["geometry"]), 0.06, 6, 2)

data = {"zeme": zeme, "brazilie": brazilie, "acre": acre}
s = json.dumps(data, separators=(",", ":"))
open("geo.json", "w").write(s)
print("pevnina:", len(zeme), "prstenců,", sum(len(r) for r in zeme), "bodů")
print("Brazílie:", len(brazilie), "prstenců,", sum(len(r) for r in brazilie), "bodů")
print("Acre:", len(acre), "prstenců,", sum(len(r) for r in acre), "bodů")
print("velikost:", round(len(s)/1024, 1), "KB")
